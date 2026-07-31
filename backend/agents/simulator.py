import json

from helpers import ask_llm_json
from prompts.simulator_prompt import SIMULATOR_PROMPT


def simulator_agent(
    original_prompt: str,
    context: dict,
    optimized_prompt: str
):
    """
    Simulates the expected output of the optimized prompt.
    """

    user_input = f"""
Original Prompt:
{original_prompt}

Context Package:
{json.dumps(context, indent=2)}

Optimized Prompt:
{optimized_prompt}
"""

    result = ask_llm_json(
        SIMULATOR_PROMPT,
        user_input
    )

    if not result:
        return {
            "predicted_quality": "Unknown",
            "confidence": 0.0,
            "output_preview": "",
            "strengths": [],
            "possible_issues": [],
            "recommendation": "",
            "execution_profile": {
                "estimated_tokens": 0,
                "reasoning_level": "Unknown",
                "estimated_sections": []
            }
        }

    return result