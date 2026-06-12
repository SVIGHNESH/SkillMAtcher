import json
import logging

from openai import OpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

MATCHING_PROMPT = """\
You are a precise skill matching assistant. Compare the Job Description \
skills list with the Resume skills list below.

Identify which JD skills are present in the resume. Be smart about \
fuzzy/synonym matches — for example:
- "React" matches "React.js" or "ReactJS"
- "Python" matches "Python 3" or "Python3"
- "ML" matches "Machine Learning"
- "AWS" matches "Amazon Web Services"
- "K8s" matches "Kubernetes"

Return ONLY a JSON object with two arrays. Example:
{{"matched": ["Python", "React"], "missing": ["Kubernetes"]}}

Use the exact skill name as it appears in the JD skills list for the \
"matched" array.

JD Skills: {jd_skills}
Resume Skills: {resume_skills}
"""


def match_skills(
    jd_skills: list[str], resume_skills: list[str]
) -> tuple[list[str], list[str]]:
    if not jd_skills:
        return [], []
    if not resume_skills:
        return [], list(jd_skills)

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    prompt = MATCHING_PROMPT.format(
        jd_skills=json.dumps(jd_skills),
        resume_skills=json.dumps(resume_skills),
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    content = response.choices[0].message.content.strip()
    return _parse_match_result(content, jd_skills)


def _parse_match_result(
    raw: str, jd_skills: list[str]
) -> tuple[list[str], list[str]]:
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        data = json.loads(raw)
        matched = [str(s).strip() for s in data.get("matched", []) if s]
        missing = [str(s).strip() for s in data.get("missing", []) if s]
        return matched, missing
    except (json.JSONDecodeError, KeyError):
        logger.warning(
            "Failed to parse match result as JSON: %s", raw[:200]
        )
        return list(jd_skills), []
