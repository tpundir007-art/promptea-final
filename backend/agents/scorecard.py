from helpers import ask_llm_json
from prompts.scorecard_prompt import SYSTEM_PROMPT

def scorecard_agent(state):
    """
    Evaluates the quality of the refined prompt.
    """

    user_message = f"""
================ ORIGINAL =================
{state.get("original_prompt", "")}

================ PERSONALIZATION =================
{state.get("personalization", "")}

================ COMPLEXITY =================
{state.get("complexity", "")}

================ GAP ANALYSIS =================
{state.get("gap", "")}

================ USER ANSWERS =================
{state.get("answers", "")}

================ CONTEXT =================
{state.get("context", "")}

================ TECHNIQUES =================
Selected:
{state.get("selected_techniques", "")}

Reasoning:
{state.get("technique_reasoning", "")}

================ STRATEGY =================
{state.get("strategy", "")}

================ REFINED PROMPT =================
{state.get("refined_prompt", "")}

================ CRITIQUE =================
{state.get("critique", "")}

================ COST ANALYSIS =================
{state.get("cost", "")}

================ SIMULATION =================
{state.get("simulator", "")}
"""

    state["score"] = ask_llm_json(
        SYSTEM_PROMPT,
        user_message
    )

    return state