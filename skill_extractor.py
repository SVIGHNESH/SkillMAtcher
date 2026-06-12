import json
import logging

from openai import OpenAI

import cache
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

# Canonical skill categories. The LLM is asked to pick one of these so the
# frontend can render a category breakdown / radar chart from the data.
CATEGORIES = [
    "Languages",
    "Frameworks",
    "Tools/Platforms",
    "Data/ML",
    "Soft Skills",
    "Domain",
]

EXTRACTION_PROMPT = """\
You are a precise skill extraction assistant. Given the following \
{label}, extract ALL professional and technical skills mentioned. \
Be thorough — include programming languages, frameworks, tools, \
platforms, soft skills, and domain expertise.

For each skill, classify it into exactly ONE of these categories:
{categories}

Return ONLY a JSON object with a "skills" array of objects, each with
"skill" and "category" keys. Example:
{{"skills": [{{"skill": "Python", "category": "Languages"}}, \
{{"skill": "Machine Learning", "category": "Data/ML"}}, \
{{"skill": "Communication", "category": "Soft Skills"}}]}}

Do NOT include any explanation, markdown formatting, or extra text.

{label}:
{text}
"""


def extract_skills(text: str, label: str) -> list[dict]:
    """Extract categorised skills from ``text``.

    Returns a list of ``{"skill": str, "category": str}`` dicts. Cached on the
    text content so re-running the same document is instant.
    """

    def _compute() -> list[dict]:
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        prompt = EXTRACTION_PROMPT.format(
            label=label,
            categories=", ".join(CATEGORIES),
            text=text,
        )
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content.strip()
        return _parse_skills(content)

    return cache.get_or_compute("extract", f"{label}\x00{text}", _compute)


def skill_names(skills: list[dict]) -> list[str]:
    """Flatten categorised skills to a plain list of names (for matching)."""
    return [s["skill"] for s in skills if s.get("skill")]


def _parse_skills(raw: str) -> list[dict]:
    raw = _strip_fences(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse extraction output as JSON: %s", raw[:200])
        return []

    items = data.get("skills", data) if isinstance(data, dict) else data
    result: list[dict] = []
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and item.get("skill"):
                category = str(item.get("category", "")).strip()
                if category not in CATEGORIES:
                    category = "Domain"
                result.append({"skill": str(item["skill"]).strip(), "category": category})
            elif isinstance(item, str) and item.strip():
                result.append({"skill": item.strip(), "category": "Domain"})
    return result


def _strip_fences(raw: str) -> str:
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()
