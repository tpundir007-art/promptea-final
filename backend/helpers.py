import json
import re

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config import Config


# ==========================
# LLM
# ==========================

llm = ChatGroq(
    model=Config.MODEL_NAME,
    groq_api_key=Config.GROQ_API_KEY,
    temperature=Config.TEMPERATURE,
)


# ==========================
# Plain Text Response
# ==========================

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Send a prompt to the LLM and return plain text.

    This function is intentionally kept simple because
    some PrompTea agents need normal text responses.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)

    if response is None:
        return ""

    content = response.content

    if content is None:
        return ""

    # LangChain can theoretically return non-string content.
    if not isinstance(content, str):
        content = str(content)

    return content.strip()


# ==========================
# JSON Cleaning
# ==========================

def clean_json_response(response: str) -> str:
    """
    Clean common formatting problems from an LLM JSON response.

    Handles:
    - Markdown ```json fences
    - Markdown ``` fences
    - Extra text before JSON
    - Extra text after JSON
    """

    if not response:
        return ""

    response = response.strip()

    # -----------------------------------
    # Remove markdown code fences
    # -----------------------------------

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    response = response.strip()

    # -----------------------------------
    # Extract JSON object
    # -----------------------------------

    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1 and end > start:
        response = response[start:end + 1]

    return response.strip()


# ==========================
# JSON Response
# ==========================

def ask_llm_json(system_prompt: str, user_prompt: str):
    """
    Ask the LLM for JSON and safely parse the response.

    Never allows malformed LLM JSON to crash the
    entire Flask/LangGraph pipeline.
    """

    response = ask_llm(system_prompt, user_prompt)

    # -----------------------------------
    # Empty response
    # -----------------------------------

    if not response:
        print_debug(
            "LLM JSON ERROR",
            "LLM returned an empty response."
        )
        return {}

    # -----------------------------------
    # Clean response
    # -----------------------------------

    cleaned = clean_json_response(response)

    # -----------------------------------
    # Parse JSON
    # -----------------------------------

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as error:

        print_debug(
            "LLM JSON ERROR",
            {
                "error": str(error),
                "raw_response": response,
                "cleaned_response": cleaned,
            },
        )

        return {}


# ==========================
# Debug
# ==========================

def print_debug(title: str, content):

    if Config.DEBUG:
        print("\n" + "=" * 60)
        print(title)
        print("=" * 60)
        print(content)
        print("=" * 60 + "\n")