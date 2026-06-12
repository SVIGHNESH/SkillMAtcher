import json
import logging

from openai import OpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
You are a precise skill extraction assistant. Given the following \
{label}, extract ALL professional and technical skills mentioned. \
Be thorough — include programming languages, frameworks, tools, \
platforms, soft skills, and domain expertise.

Return ONLY a raw JSON array of strings. Example:
["Python", "Machine Learning", "SQL", "Communication", "Project Management"]

Do NOT include any explanation, markdown formatting, or extra text.

{label}:
{text}
"""


def extract_skills(text: str, label: str) -> list[str]:
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    prompt = EXTRACTION_PROMPT.format(label=label, text=text)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    content = response.choices[0].message.content.strip()
    return _parse_skill_list(content)


def _parse_skill_list(raw: str) -> list[str]:
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        skills = json.loads(raw)
        if isinstance(skills, list):
            return [str(s).strip() for s in skills if s]
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM output as JSON: %s", raw[:200])
    return []
