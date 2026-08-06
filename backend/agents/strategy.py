from helpers import ask_llm_json
from prompts.strategy_prompt import STRATEGY_PROMPT


def strategy_agent(state):

    user_message = f"""
Detected Techniques:
{", ".join(state["selected_techniques"])}

Original Prompt:
{state["original_prompt"]}

User Knowledge Level:
{state.get("level", "Intermediate")}

User Personalization Instructions (explicit, verbatim from the user):
{state.get("personalization") or "None provided."}

Context Package:
{state.get("context", {})}
"""

    state["strategy"] = ask_llm_json(
        STRATEGY_PROMPT,
        user_message
    )

    return state