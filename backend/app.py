from unittest import result

from flask import Flask, request, jsonify
from flask_cors import CORS

from graph.workflow import pre_gap_workflow, post_gap_workflow
from graph.state import PromptState

app = Flask(__name__)
CORS(app)


# --------------------------------------------------------------------
# Canonical personalization presets.
#
# Each key maps to a FIXED, hard-coded instruction. This is deliberate:
# for the common cases, we don't want the LLM to re-interpret a checkbox
# label's wording every single time (that reintroduces the phrasing
# inconsistency free text has). The frontend sends the KEY (e.g.
# "examples"), not the display label, and we always turn it into the
# exact same instruction text here.
#
# Keep these keys in sync with whatever values the frontend checkboxes
# submit.
# --------------------------------------------------------------------
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
    custom_text = str(data.get("personalization_custom", "")).strip()

    # Legacy path: a single plain string was sent instead.
    if not preset_keys and not custom_text and "personalization" in data:
        return str(data.get("personalization", "")).strip()

    if not isinstance(preset_keys, list):
        preset_keys = []

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
        "pending_state": clean_state if needs_clarification else None,
    }


@app.route("/")
def home():
    return jsonify({"message": "PrompTea Backend Running ☕🍒"})


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(silent=True) or {}
        original_prompt = str(data.get("prompt", "")).strip()
        level = data.get("level", "Intermediate")

        if not original_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        try:
            personalization = build_personalization_string(data)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

        state: PromptState = empty_state(original_prompt, level, personalization)
        result = pre_gap_workflow.invoke(state)

        if not result.get("validation", {}).get("continue_pipeline", True):
            return jsonify(response_from_state(result)), 200

        gap = result.get("gap") or {}
        needs_clarification = bool(gap.get("needs_clarification"))

        if needs_clarification:
            return jsonify(response_from_state(result, True)), 200

        final = post_gap_workflow.invoke(result)
        return jsonify(response_from_state(final)), 200

    except Exception as e:
        app.logger.exception("PrompTea /generate failed")
        return jsonify({"error": str(e)}), 500


@app.route("/continue", methods=["POST"])
def continue_brewing():
    try:
        data = request.get_json(silent=True) or {}
        state = data.get("state")
        answers = data.get("answers", {})

        if not isinstance(state, dict):
            return jsonify({"error": "A pending brewing state is required."}), 400

        state["answers"] = answers if isinstance(answers, dict) else {}
        final = post_gap_workflow.invoke(state)

        return jsonify(response_from_state(final)), 200

    except Exception as e:
        app.logger.exception("PrompTea /continue failed")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)