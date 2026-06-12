import os

from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL", "https://api.groq.com/openai/v1"
)
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# Toggle the SQLite-backed LLM response cache (speeds up repeated matches).
LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "true").lower() not in (
    "0",
    "false",
    "no",
)

# Optional per-client rate limit on the match endpoints, e.g. "30/minute".
# Empty disables rate limiting (the default, convenient for local dev).
RATE_LIMIT = os.getenv("RATE_LIMIT", "").strip()
