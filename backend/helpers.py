import json
import logging
import re
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config import Config

log = logging.getLogger("promptea")


class LLMError(Exception):
    """Raised when the LLM is unreachable, rate-limited or times out."""

    def __init__(self, message: str, status: int = 503):
        super().__init__(message)
        self.status = status


llm = ChatGroq(
    model=Config.MODEL_NAME,
    groq_api_key=Config.GROQ_API_KEY,
    temperature=Config.TEMPERATURE,
    timeout=Config.LLM_TIMEOUT,
    max_retries=0,  # we do our own retry/backoff below
)

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(value, limit: int) -> str:
    """Coerce to str, strip control characters, cap the length."""
    text = _CONTROL.sub("", str(value if value is not None else "")).strip()
    return text[:limit]


def compact(obj) -> str:
    """Token-cheap JSON (no indentation)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), default=str)


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    last = None
    for attempt in range(Config.LLM_RETRIES + 1):
        try:
            content = llm.invoke(messages).content
            return (content if isinstance(content, str) else str(content or "")).strip()
        except Exception as exc:  # noqa: BLE001 - classify below
            last = exc
            name = type(exc).__name__.lower()
            msg = str(exc).lower()
            transient = any(
                k in name + msg
                for k in ("ratelimit", "429", "timeout", "timed out",
                          "connection", "502", "503", "504", "overloaded")
            )
            log.warning("LLM call failed (attempt %d): %s", attempt + 1, exc)
            if not transient or attempt == Config.LLM_RETRIES:
                break
            time.sleep(2 ** attempt * 2)  # 2s, 4s
    text = (type(last).__name__ + str(last)).lower()
    if "ratelimit" in text or "429" in text:
        raise LLMError("The AI service is busy right now. Please try again in a minute.", 429)
    if "timeout" in text or "timed out" in text:
        raise LLMError("The AI service took too long to respond. Please try again.", 504)
    if "auth" in text or "401" in text or "invalid api key" in text:
        raise LLMError("The AI service is misconfigured. Please contact the site owner.", 503)
    raise LLMError("The AI service is temporarily unavailable. Please try again.", 503)


def clean_json_response(response: str) -> str:
    if not response:
        return ""
    response = re.sub(r"^```(?:json)?\s*", "", response.strip(), flags=re.I)
    response = re.sub(r"\s*```$", "", response).strip()
    start, end = response.find("{"), response.rfind("}")
    return response[start:end + 1] if 0 <= start < end else response


def ask_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """Always returns a dict ({} if the model gave nothing parseable)."""
    response = ask_llm(system_prompt, user_prompt)
    if not response:
        print_debug("LLM JSON ERROR", "empty response")
        return {}
    try:
        parsed = json.loads(clean_json_response(response))
    except json.JSONDecodeError as error:
        print_debug("LLM JSON ERROR", f"{error}\n{response[:500]}")
        return {}
    return parsed if isinstance(parsed, dict) else {}


def print_debug(title: str, content):
    if Config.DEBUG:
        log.info("%s: %s", title, content)
