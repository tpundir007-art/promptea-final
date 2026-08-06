import json

from helpers import ask_llm
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
{json.dumps(state.get("answers", {}), indent=2)}

Context Package:
{json.dumps(state.get("context", {}), indent=2)}

Detected Techniques:
{", ".join(state.get("selected_techniques", []))}

Technique Reasoning:
{state.get("technique_reasoning", "")}

Refinement Strategy:
{json.dumps(state.get("strategy", {}), indent=2)}

Current Prompt:
{current}

Critic Feedback:
{json.dumps(state.get("critique", {}), indent=2)}

Refinement Round:
{state.get("retry_count", 0)}
"""

    state["refined_prompt"] = ask_llm(SYSTEM_PROMPT, user_message)
    state["draft_prompt"] = state["refined_prompt"]
    return state
