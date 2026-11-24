
from helpers import ask_llm_json, compact
from prompts.context_prompt import CONTEXT_BUILDER_PROMPT


def context_agent(
    prompt: str,
    complexity: dict,
    gap: dict,
    answers: dict,
    level: str = "Intermediate",
    personalization: str = "",
):
    """
    Constructs a structured context package from the
    original prompt, complexity analysis, gap analysis,
    user clarification answers, the user's stated knowledge
    level, and any personalization instructions the user
    supplied for how the response should be delivered.
    """

    user_input = f"""
Original Prompt:
{prompt}

Complexity Analysis:
{compact(complexity)}

Gap Analysis:
{compact(gap)}

Clarification Answers:
{compact(answers)}

User Knowledge Level:
{level}

User Personalization Instructions (explicit, verbatim from the user):
{personalization if personalization else "None provided."}
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
            "user_level": level,
            "personalization": personalization,
            "requirements": [],
            "available_information": [],
            "missing_information": [],
            "assumptions": [],
            "optimization_notes": []
        }

    return result