from helpers import ask_llm_json
from prompts.technique_prompt import SYSTEM_PROMPT


def technique_agent(user_prompt: str):
    """Recommend prompt-engineering techniques (always returns a clean dict)."""
    result = ask_llm_json(SYSTEM_PROMPT, user_prompt)
    techniques = result.get("selected_techniques")
    if not isinstance(techniques, list):
        techniques = []
    return {
        "selected_techniques": [str(t) for t in techniques],
        "technique_reasoning": result.get("technique_reasoning", ""),
    }
