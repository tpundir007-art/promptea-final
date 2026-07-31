# agents/gap.py

from helpers import ask_llm_json
from prompts.gap_prompt import GAP_PROMPT


def gap_agent(prompt: str):
    """
    Analyze the user's prompt and determine whether
    additional information is needed before refinement.

    The agent should only request clarification when
    the missing information would materially affect the
    resulting prompt.
    """

    result = ask_llm_json(
        GAP_PROMPT,
        prompt
    )

    # Safety fallback
    if not isinstance(result, dict):
        return {
            "task_type": "unknown",
            "needs_clarification": False,
            "confidence": 0.0,
            "missing_fields": [],
            "reasoning": "Gap analysis failed; continuing with available information."
        }

    # Normalize fields so downstream nodes always receive
    # the expected structure.
    result.setdefault("task_type", "unknown")
    result.setdefault("needs_clarification", False)
    result.setdefault("confidence", 0.0)
    result.setdefault("missing_fields", [])

    # Make sure missing_fields is always a list.
    if not isinstance(result["missing_fields"], list):
        result["missing_fields"] = [str(result["missing_fields"])]

    return result