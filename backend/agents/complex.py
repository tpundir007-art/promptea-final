# agents/complex.py

from helpers import ask_llm_json
from prompts.complex_prompt import COMPLEXITY_PROMPT


def complexity_agent(user_prompt: str):
    """
    Analyzes the complexity of the user's prompt.

    Returns:
        dict: Complexity analysis in JSON format.
    """

    result = ask_llm_json(
        COMPLEXITY_PROMPT,
        user_prompt
    )

    if not result:
        return {
            "complexity_level": "Unknown",
            "complexity_score": 0,
            "confidence": 0.0,
            "task_type": "Unknown",
            "reasoning_required": "Unknown",
            "requires_clarification": False,
            "summary": "Unable to analyze prompt complexity.",
            "factors": {
                "ambiguity": 0,
                "technical_depth": 0,
                "multi_step_reasoning": 0,
                "domain_knowledge": 0,
                "constraint_density": 0,
                "creativity": 0
            }
        }

    return result