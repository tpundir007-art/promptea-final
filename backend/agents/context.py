import json

from helpers import ask_llm_json
from prompts.context_prompt import CONTEXT_BUILDER_PROMPT


def context_agent(
    prompt: str,
    complexity: dict,
    gap: dict,
    answers: dict
):
    """
    Constructs a structured context package from the
    original prompt, complexity analysis, gap analysis,
    and user clarification answers.
    """

    user_input = f"""
Original Prompt:
{prompt}

Complexity Analysis:
{json.dumps(complexity, indent=2)}

Gap Analysis:
{json.dumps(gap, indent=2)}

Clarification Answers:
{json.dumps(answers, indent=2)}
"""

    result = ask_llm_json(
        CONTEXT_BUILDER_PROMPT,
        user_input
    )

    if not result:
        return {
            "intent": "",
            "task_type": "",
            "goal": "",
            "context": {},
            "requirements": [],
            "available_information": [],
            "missing_information": [],
            "assumptions": [],
            "optimization_notes": []
        }

    return result