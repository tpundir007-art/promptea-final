import hashlib
import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


class Config:
    # LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    TEMPERATURE = 0.4
    LLM_TIMEOUT = _int("LLM_TIMEOUT", 60)        # seconds per LLM call
    LLM_RETRIES = _int("LLM_RETRIES", 2)         # retries on 429/5xx/timeouts
    MAX_ITERATIONS = _int("MAX_ITERATIONS", 2)   # critic -> refiner loops
    TARGET_SCORE = 9.0

    # Security
    DEBUG = _bool("DEBUG", False)                # never True in production
    SECRET_KEY = os.getenv("SECRET_KEY") or hashlib.sha256(
        ("promptea:" + GROQ_API_KEY).encode()
    ).hexdigest()
    ALLOWED_ORIGINS = [
        o.strip().rstrip("/")
        for o in os.getenv(
            "ALLOWED_ORIGINS",
            "https://prompteafinal.netlify.app,http://localhost:5173",
        ).split(",")
        if o.strip()
    ]
    MAX_PROMPT_CHARS = _int("MAX_PROMPT_CHARS", 4000)
    MAX_ANSWER_CHARS = _int("MAX_ANSWER_CHARS", 1000)
    MAX_ANSWERS = _int("MAX_ANSWERS", 15)
    PENDING_TTL = _int("PENDING_TTL", 3600)      # seconds a clarification stays valid
    RATE_LIMIT = _int("RATE_LIMIT", 10)          # LLM requests per IP per window
    RATE_WINDOW = _int("RATE_WINDOW", 60)


if not Config.GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to backend/.env or your host's "
        "environment variables."
    )
