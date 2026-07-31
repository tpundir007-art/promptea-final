import re

from helpers import ask_llm_json
from prompts.validator_prompt import SYSTEM_PROMPT, USER_PROMPT


# -------------------------
# Rule-based Checks
# -------------------------

CHAT_WORDS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
    "thanks",
    "thank you",
    "bye",
}

VAGUE_WORDS = {
    "email",
    "resume",
    "essay",
    "story",
    "presentation",
    "website",
    "report",
    "project",
    "post",
    "article",
}


PROMPT_INJECTION_PATTERNS = {
    "ignore previous instructions",
    "ignore all previous instructions",
    "forget previous instructions",
    "forget all previous instructions",
    "override previous instructions",
    "override instructions",
    "system prompt",
    "developer prompt",
    "hidden prompt",
    "hidden instructions",
    "internal instructions",
    "reveal your prompt",
    "show your prompt",
    "print your prompt",
    "show system prompt",
    "reveal system prompt",
    "print system prompt",
    "ignore safety",
    "disable safety",
    "bypass safety",
    "bypass restrictions",
    "jailbreak",
    "developer mode",
    "dan mode",
    "repeat the instructions above",
    "output the conversation above",
    "you are no longer chatgpt",
}


SAFE_REFINEMENT_CONTEXTS = (
    "improve this prompt",
    "rewrite this prompt",
    "refine this prompt",
    "optimise this prompt",
    "optimize this prompt",
    "translate this",
    "summarise this",
    "summarize this",
)


def is_math_expression(text):
    """
    Detect simple arithmetic expressions.

    Examples:
    2+2
    15/3
    10*8
    """

    return bool(re.fullmatch(r"[0-9+\-*/(). ]+", text))


def is_gibberish(text):
    """
    Detect meaningless input.
    """

    text = text.strip()

    if text == "":
        return True

    # Only punctuation
    if re.fullmatch(r"[^\w]+", text):
        return True

    # Repeated characters
    if len(set(text)) <= 2 and len(text) > 4:
        return True

    # Random keyboard smash
    if len(text.split()) == 1:

        word = text.lower()

        if len(word) >= 5 and not re.search(r"[aeiou]", word):
            return True

    return False


def is_prompt_injection(text):
    """
    Detect prompt injection attempts aimed at manipulating PrompTea itself.

    This intentionally allows:
    - Act as a teacher
    - Act as an interviewer
    - Improve this prompt: Ignore previous instructions...
    - Explain prompt injection
    """

    lower = text.lower().strip()

    # -------------------------
    # Legitimate refinement
    # -------------------------

    if any(ctx in lower for ctx in SAFE_REFINEMENT_CONTEXTS):
        return False

    # -------------------------
    # Educational requests
    # -------------------------

    educational_prefixes = (
        "explain",
        "describe",
        "what is",
        "write a blog",
        "write an article",
        "give examples",
    )

    if lower.startswith(educational_prefixes):
        return False

    # -------------------------
    # Legitimate role prompting
    # -------------------------

    if lower.startswith("act as"):
        return False

    # -------------------------
    # Injection patterns
    # -------------------------

    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in lower:
            return True

    return False


def validation_agent(state):
    """
    Validate the user's original prompt.

    IMPORTANT:
    This function returns ONLY the validation result.
    It must NOT return the entire LangGraph state,
    otherwise state["validation"] would contain the
    state itself and create a circular reference.
    """

    prompt = state["original_prompt"].strip()

    lower = prompt.lower()

    # -----------------------------------
    # Empty
    # -----------------------------------

    if prompt == "":

        return {
            "status": "GIBBERISH",
            "confidence": 1.0,
            "reason": "Input is empty.",
            "message": "Please enter a prompt you'd like PrompTea to improve.",
            "continue_pipeline": False,
        }

    # -----------------------------------
    # Greetings
    # -----------------------------------

    if lower in CHAT_WORDS:

        return {
            "status": "CASUAL_CHAT",
            "confidence": 1.0,
            "reason": "Greeting detected.",
            "message": (
                "Hi! I'm PrompTea ☕. I specialise in improving prompts. "
                "Try entering a prompt you'd like me to optimise."
            ),
            "continue_pipeline": False,
        }

    # -----------------------------------
    # Gibberish
    # -----------------------------------

    if is_gibberish(prompt):

        return {
            "status": "GIBBERISH",
            "confidence": 1.0,
            "reason": "Input appears meaningless.",
            "message": (
                "I couldn't identify a meaningful prompt. "
                "Please enter a prompt you'd like PrompTea to improve."
            ),
            "continue_pipeline": False,
        }

    # -----------------------------------
    # Prompt Injection
    # -----------------------------------

    if is_prompt_injection(prompt):

        return {
            "status": "PROMPT_INJECTION",
            "confidence": 1.0,
            "reason": (
                "Prompt attempts to manipulate PrompTea's "
                "internal behaviour."
            ),
            "message": (
                "This appears to be a prompt injection attempt. "
                "PrompTea only refines prompts and cannot process "
                "instructions that attempt to override or reveal "
                "its internal behaviour."
            ),
            "continue_pipeline": False,
        }

    # -----------------------------------
    # Maths
    # -----------------------------------

    if is_math_expression(prompt):

        return {
            "status": "DIRECT_QUERY",
            "confidence": 1.0,
            "reason": "Mathematical expression detected.",
            "message": (
                "This looks like a direct question rather than a "
                "prompt to optimise. PrompTea specialises in "
                "refining prompts."
            ),
            "continue_pipeline": False,
        }

    # -----------------------------------
    # Very vague prompts
    # -----------------------------------

    if lower in VAGUE_WORDS:

        return {
            "status": "NEEDS_CLARIFICATION",
            "confidence": 0.98,
            "reason": "Prompt is too vague.",
            "message": (
                "Could you provide a little more detail so I can "
                "improve your prompt?"
            ),
            "continue_pipeline": False,
        }

    # -----------------------------------
    # LLM handles everything else
    # -----------------------------------

    result = ask_llm_json(
        SYSTEM_PROMPT,
        USER_PROMPT.format(
            user_prompt=prompt
        )
    )

    return result

