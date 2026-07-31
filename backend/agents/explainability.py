from helpers import ask_llm_json
from prompts.explainability_prompt import SYSTEM_PROMPT


def explainability_agent(state):
    """
    Explains how and why the prompt was refined.
    """

    user_message = f"""
User Level:
{state["level"]}

Original Prompt:
{state["original_prompt"]}

Selected Techniques:
{", ".join(state["selected_techniques"])}

Strategy:
{state["strategy"]}

Refined Prompt:
{state["refined_prompt"]}

Critique:
{state["critique"]}

Scorecard:
{state["score"]}
"""

    state["explanation"] = ask_llm_json(
        SYSTEM_PROMPT,
        user_message
    )

    return state