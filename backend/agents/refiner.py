
from helpers import ask_llm, compact
from prompts.refiner_prompt import SYSTEM_PROMPT


def refiner_agent(state):
    """Refine using the actual strategy, context, answers and critic feedback."""

    current = state.get("refined_prompt") or state["original_prompt"]

    user_message = f"""
Original Prompt:
{state["original_prompt"]}

User Knowledge Level:
{state.get("level", "Intermediate")}

User Personalization Instructions (explicit, verbatim from the user):
{state.get("personalization") or "None provided."}

Clarification Answers:
{compact(state.get("answers", {}))}

Context Package:
{compact(state.get("context", {}))}

Detected Techniques:
{", ".join(state.get("selected_techniques", []))}

Technique Reasoning:
{state.get("technique_reasoning", "")}

Refinement Strategy:
{compact(state.get("strategy", {}))}

Current Prompt:
{current}

Critic Feedback:
{compact(state.get("critique", {}))}

Refinement Round:
{state.get("retry_count", 0)}
"""

    state["refined_prompt"] = ask_llm(SYSTEM_PROMPT, user_message)
    state["draft_prompt"] = state["refined_prompt"]
    return state
