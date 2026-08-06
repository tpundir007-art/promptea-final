from helpers import ask_llm_json
from prompts.critic_prompt import SYSTEM_PROMPT


def critic_agent(state):
    """
    Evaluates the latest refined prompt and decides
    whether another refinement iteration is needed.
    """

    user_message = f"""
Original Prompt:
{state["original_prompt"]}

User Knowledge Level:
{state.get("level", "Intermediate")}

User Personalization Instructions (explicit, verbatim from the user):
{state.get("personalization") or "None provided."}

Detected Techniques:
{", ".join(state["selected_techniques"])}

Prompt Strategy:
{state["strategy"]}

Current Prompt:
{state["refined_prompt"]}

Current Iteration:
{state["retry_count"] + 1}
"""

    state["critique"] = ask_llm_json(
        SYSTEM_PROMPT,
        user_message
    )

    return state