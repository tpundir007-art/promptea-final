import logging
import threading
import time
import uuid
from collections import defaultdict, deque

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from graph.state import PromptState
from graph.workflow import post_gap_workflow, pre_gap_workflow
from helpers import LLMError, sanitize_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("promptea")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024  # reject oversized bodies early
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)  # real client IP behind Render's proxy

CORS(
    app,
    resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,
)

LEVELS = {"Novice", "Beginner", "Intermediate", "Advanced"}
_signer = URLSafeTimedSerializer(Config.SECRET_KEY, salt="promptea-pending-v1")


# ------------------------------------------------------------------
# Security / error plumbing
# ------------------------------------------------------------------
_hits = defaultdict(deque)
_hits_lock = threading.Lock()


def rate_limited(ip: str) -> bool:
    """Sliding-window limiter (per worker process)."""
    now = time.monotonic()
    with _hits_lock:
        q = _hits[ip]
        while q and now - q[0] > Config.RATE_WINDOW:
            q.popleft()
        if len(q) >= Config.RATE_LIMIT:
            return True
        q.append(now)
        if len(_hits) > 5000:  # keep memory bounded
            for k in [k for k, v in _hits.items() if not v]:
                del _hits[k]
        return False


def fail(message: str, status: int):
    return jsonify({"error": message, "request_id": getattr(g, "rid", "")}), status


@app.before_request
def _before():
    g.rid = uuid.uuid4().hex[:8]
    if request.method == "POST" and rate_limited(request.remote_addr or "?"):
        return fail("Too many requests. Please wait a minute and try again.", 429)


@app.after_request
def _security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return resp


@app.errorhandler(LLMError)
def _llm_error(e):
    log.error("[%s] LLM error: %s", g.get("rid"), e)
    return fail(str(e), e.status)


@app.errorhandler(HTTPException)
def _http_error(e):
    msg = "Request too large." if e.code == 413 else (e.description or e.name)
    return fail(msg, e.code or 500)


@app.errorhandler(Exception)
def _unhandled(e):
    # Full details go to the server log only - never to the client.
    log.exception("[%s] Unhandled error", g.get("rid"))
    return fail("Something went wrong while brewing. Please try again.", 500)


# ------------------------------------------------------------------
# Personalization
# ------------------------------------------------------------------
PERSONALIZATION_PRESETS = {
    "examples": (
        "Include real-world examples to illustrate the explanation."
    ),
    "bullet_points": (
        "Structure the response using bullet points or structured "
        "lists wherever appropriate."
    ),
    "step_by_step": (
        "Break the explanation or instructions down into clear, "
        "sequential steps."
    ),
    "concise": (
        "Keep the response concise and to the point, avoiding "
        "unnecessary elaboration."
    ),
}

MAX_PERSONALIZATION_LENGTH = 400
MAX_CUSTOM_PERSONALIZATION_LENGTH = 300


def build_personalization_string(data: dict) -> str:
    """
    Combines checkbox presets + free-text "Other" input into a single
    personalization string for the pipeline.

    Accepts EITHER:
      - "personalization_presets": list of preset keys (e.g.
        ["examples", "bullet_points"]) + "personalization_custom":
        free text from the "Other" box.
      - OR the legacy "personalization": a plain string (still
        supported so older frontend calls / the test script keep
        working unchanged).

    Unknown preset keys are silently ignored rather than erroring,
    so a frontend/backend key mismatch fails soft instead of
    breaking prompt generation.
    """
    preset_keys = data.get("personalization_presets", [])
    custom_text = sanitize_text(data.get("personalization_custom", ""), 2000)

    # Legacy path: a single plain string was sent instead.
    if not preset_keys and not custom_text and "personalization" in data:
        return sanitize_text(data.get("personalization", ""), MAX_PERSONALIZATION_LENGTH)

    if not isinstance(preset_keys, list):
        preset_keys = []
    preset_keys = [k for k in preset_keys if isinstance(k, str)]

    if len(custom_text) > MAX_CUSTOM_PERSONALIZATION_LENGTH:
        raise ValueError(
            f"Custom personalization must be under "
            f"{MAX_CUSTOM_PERSONALIZATION_LENGTH} characters."
        )

    instructions = [
        PERSONALIZATION_PRESETS[key]
        for key in preset_keys
        if key in PERSONALIZATION_PRESETS
    ]

    if custom_text:
        instructions.append(custom_text)

    combined = " ".join(instructions).strip()

    if len(combined) > MAX_PERSONALIZATION_LENGTH:
        raise ValueError(
            f"Personalization instructions must be under "
            f"{MAX_PERSONALIZATION_LENGTH} characters combined."
        )

    return combined


def empty_state(original_prompt, level, personalization=""):
    return {
        "original_prompt": original_prompt,
        "level": level,
        "personalization": personalization,
        "validation": {},
        "complexity": {},
        "gap": {},
        "answers": {},
        "context": {},
        "selected_techniques": [],
        "technique_reasoning": "",
        "strategy": {},
        "draft_prompt": "",
        "refined_prompt": "",
        "critique": {},
        "retry_count": 0,
        "cost": {},
        "simulator": {},
        "score": {},
        "explanation": {},
    }
def json_safe(value, _seen=None):
    """
    Convert nested values into JSON-safe Python objects.
    Detects circular references so recursive LangGraph/state
    structures cannot cause infinite recursion.
    """
    if _seen is None:
        _seen = set()

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # Detect circular references in containers/objects
    if isinstance(value, (dict, list, tuple, set)):
        value_id = id(value)

        if value_id in _seen:
            return "[Circular Reference]"

        _seen.add(value_id)

        try:
            if isinstance(value, dict):
                return {
                    str(k): json_safe(v, _seen)
                    for k, v in value.items()
                }

            return [
                json_safe(v, _seen)
                for v in value
            ]

        finally:
            _seen.remove(value_id)

    # Last-resort conversion for unexpected objects
    return str(value)

def response_from_state(result, needs_clarification=False):
    """
    Build a clean JSON-safe API response.

    Never return the raw LangGraph state because it may contain
    circular/internal objects that Flask cannot serialize.
    """

    clean_state = {
    "original_prompt": json_safe(result.get("original_prompt", "")),
    "level": json_safe(result.get("level", "Intermediate")),
    "personalization": json_safe(result.get("personalization", "")),
    "validation": json_safe(result.get("validation", {})),
    "complexity": json_safe(result.get("complexity", {})),
    "gap": json_safe(result.get("gap", {})),
    "answers": json_safe(result.get("answers", {})),
    "context": json_safe(result.get("context", {})),
    "selected_techniques": json_safe(
        result.get("selected_techniques", [])
    ),
    "technique_reasoning": json_safe(
        result.get("technique_reasoning", "")
    ),
    "strategy": json_safe(result.get("strategy", {})),
    "draft_prompt": json_safe(result.get("draft_prompt", "")),
    "refined_prompt": json_safe(result.get("refined_prompt", "")),
    "critique": json_safe(result.get("critique", {})),
    "retry_count": json_safe(result.get("retry_count", 0)),
    "cost": json_safe(result.get("cost", {})),
    "simulator": json_safe(result.get("simulator", {})),
    "score": json_safe(result.get("score", {})),
    "explanation": json_safe(result.get("explanation", {})),
    }
    return {
        "status": (
            "clarification_required"
            if needs_clarification
            else "complete"
        ),
        "needs_clarification": needs_clarification,

        "level": clean_state["level"],
        "personalization": clean_state["personalization"],
        "validation": clean_state["validation"],
        "complexity": clean_state["complexity"],
        "gap": clean_state["gap"],
        "answers": clean_state["answers"],
        "context": clean_state["context"],
        "selected_techniques": clean_state["selected_techniques"],
        "technique_reasoning": clean_state["technique_reasoning"],
        "strategy": clean_state["strategy"],
        "draft_prompt": clean_state["draft_prompt"],
        "refined_prompt": clean_state["refined_prompt"],
        "critique": clean_state["critique"],
        "cost": clean_state["cost"],
        "simulator": clean_state["simulator"],
        "score": clean_state["score"],
        "explanation": clean_state["explanation"],
        "retry_count": clean_state["retry_count"],
        "iterations": clean_state["retry_count"],

        # Only send our explicitly known state fields for resuming.
        "pending_state": pack_state(clean_state) if needs_clarification else None,
    }



# ------------------------------------------------------------------
# Signed pending state (prevents clients from forging/tampering state)
# ------------------------------------------------------------------
def pack_state(state: dict) -> str:
    return _signer.dumps(state)


def unpack_state(token):
    if not isinstance(token, str) or len(token) > 200_000:
        return None
    try:
        state = _signer.loads(token, max_age=Config.PENDING_TTL)
    except (BadSignature, SignatureExpired):
        return None
    return state if isinstance(state, dict) else None


def clean_answers(answers) -> dict:
    if not isinstance(answers, dict):
        return {}
    out = {}
    for k, v in list(answers.items())[: Config.MAX_ANSWERS]:
        if isinstance(v, (list, tuple)):
            v = ", ".join(str(x) for x in v)
        out[sanitize_text(k, 100)] = sanitize_text(v, Config.MAX_ANSWER_CHARS)
    return out


@app.route("/")
def home():
    return jsonify({"message": "PrompTea Backend Running"})


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("Request body must be valid JSON.", 400)

    prompt = sanitize_text(data.get("prompt"), Config.MAX_PROMPT_CHARS + 1)
    if not prompt:
        return fail("Prompt cannot be empty.", 400)
    if len(prompt) > Config.MAX_PROMPT_CHARS:
        return fail(f"Prompt is too long (max {Config.MAX_PROMPT_CHARS} characters).", 400)

    level = data.get("level")
    level = level if level in LEVELS else "Intermediate"

    try:
        personalization = build_personalization_string(data)
    except ValueError as ve:
        return fail(str(ve), 400)

    result = pre_gap_workflow.invoke(empty_state(prompt, level, personalization))

    if not (result.get("validation") or {}).get("continue_pipeline", True):
        return jsonify(response_from_state(result)), 200

    if (result.get("gap") or {}).get("needs_clarification"):
        return jsonify(response_from_state(result, True)), 200

    return jsonify(response_from_state(post_gap_workflow.invoke(result))), 200


@app.route("/continue", methods=["POST"])
def continue_brewing():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return fail("Request body must be valid JSON.", 400)

    state = unpack_state(data.get("state"))
    if state is None:
        return fail("This brew has expired or is invalid. Please start again.", 400)

    # Only accept the fields we issued; re-apply server-side limits.
    base = empty_state(
        sanitize_text(state.get("original_prompt"), Config.MAX_PROMPT_CHARS),
        state.get("level") if state.get("level") in LEVELS else "Intermediate",
        sanitize_text(state.get("personalization"), MAX_PERSONALIZATION_LENGTH),
    )
    for key in ("validation", "complexity", "gap"):
        if isinstance(state.get(key), dict):
            base[key] = state[key]
    base["answers"] = clean_answers(data.get("answers"))

    return jsonify(response_from_state(post_gap_workflow.invoke(base))), 200


if __name__ == "__main__":
    app.run(debug=False, port=5000)  # production: gunicorn app:app
