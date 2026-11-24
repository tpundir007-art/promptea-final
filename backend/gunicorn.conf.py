# Auto-loaded by `gunicorn app:app` when run from this folder.
# The pipeline makes several LLM calls; gunicorn's default 30s timeout kills it.
import os

bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
threads = 4
timeout = 300
graceful_timeout = 30
