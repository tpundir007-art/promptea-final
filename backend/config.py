import os
from dotenv import load_dotenv

# Load .env
load_dotenv()


class Config:
    # =========================
    # Groq Configuration
    # =========================
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")

    # =========================
    # LLM Parameters
    # =========================
    TEMPERATURE = 0.7
    MAX_ITERATIONS = 3

    # =========================
    # Prompt Quality
    # =========================
    TARGET_SCORE = 9.0

    # =========================
    # Debugging
    # =========================
    DEBUG = True


if not Config.GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found.\n"
        "Create a .env file with:\n\n"
        "GROQ_API_KEY=your_api_key_here"
    )