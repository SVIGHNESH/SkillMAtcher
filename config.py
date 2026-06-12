import os

from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL", "https://api.groq.com/openai/v1"
)
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
