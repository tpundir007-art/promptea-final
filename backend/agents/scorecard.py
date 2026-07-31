from helpers import ask_llm_json
from prompts.scorecard_prompt import SYSTEM_PROMPT


def scorecard_agent(state):
    """
    Evaluates the quality of the refined prompt.
    """

    user_message = f"""
Original Prompt:
{state["original_prompt"]}

Refined Prompt:
{state["refined_prompt"]}

Critique:
{state["critique"]}
"""

    state["score"] = ask_llm_json(
        SYSTEM_PROMPT,
        user_message
    )

    return state