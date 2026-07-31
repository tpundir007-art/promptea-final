from unittest import result

from flask import Flask, request, jsonify
from flask_cors import CORS

from graph.workflow import pre_gap_workflow, post_gap_workflow
from graph.state import PromptState

app = Flask(__name__)
CORS(app)


def empty_state(original_prompt, level):
    return {
        "original_prompt": original_prompt,
        "level": level,
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

        state: PromptState = empty_state(original_prompt, level)
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
