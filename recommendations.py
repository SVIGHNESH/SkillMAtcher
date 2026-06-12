"""LLM-generated skill-gap analysis.

Given the matched/missing skills for a JD–resume pair, produce an overall
fit verdict plus an actionable learning recommendation per missing skill.
"""

import json
import logging

from openai import OpenAI

import cache
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

VERDICTS = ["Strong fit", "Moderate fit", "Partial fit", "Weak fit"]

ANALYSIS_PROMPT = """\
You are a career coach analysing how well a candidate fits a role for \
"{jd_name}".

Matched skills (candidate has these): {matched}
Missing skills (required but absent): {missing}

Produce a concise, encouraging but honest gap analysis. Return ONLY a JSON \
object with this shape:
{{
  "verdict": one of {verdicts},
  "summary": "2-3 sentence overall assessment, naming the top 1-2 gaps to close",
  "recommendations": [
    {{
      "skill": "<a missing skill>",
      "why_it_matters": "1 sentence on its relevance to this role",
      "how_to_learn": "1 concrete, specific way to learn it (a resource type, \
project, or path)"
    }}
  ]
}}

Only include recommendations for the most important missing skills (at most 6). \
Do NOT include markdown or any text outside the JSON object.
"""


def analyze_gap(
    jd_name: str, matched: list[str], missing: list[str]
) -> dict:
    """Return ``{verdict, summary, recommendations[]}``.

    Falls back to a deterministic, non-LLM summary on any error so the match
    flow never fails because of the (optional) coaching layer.
    """
    if not missing:
        return {
            "verdict": "Strong fit",
            "summary": "The candidate covers all required skills for this role.",
            "recommendations": [],
        }

    def _compute() -> dict:
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        prompt = ANALYSIS_PROMPT.format(
            jd_name=jd_name,
            matched=json.dumps(matched),
            missing=json.dumps(missing),
            verdicts=json.dumps(VERDICTS),
        )
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content.strip()
        return _parse_analysis(content, missing)

    try:
        payload = json.dumps(
            {"jd": jd_name, "matched": matched, "missing": missing}, sort_keys=True
        )
        return cache.get_or_compute("analyze", payload, _compute)
    except Exception as e:  # noqa: BLE001 - coaching is best-effort
        logger.warning("Gap analysis failed, using fallback: %s", e)
        return _fallback(matched, missing)


def _parse_analysis(raw: str, missing: list[str]) -> dict:
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        data = json.loads(raw)
        verdict = str(data.get("verdict", "")).strip()
        if verdict not in VERDICTS:
            verdict = _rate_verdict(missing)
        recs = []
        for r in data.get("recommendations", []):
            if isinstance(r, dict) and r.get("skill"):
                recs.append(
                    {
                        "skill": str(r.get("skill", "")).strip(),
                        "why_it_matters": str(r.get("why_it_matters", "")).strip(),
                        "how_to_learn": str(r.get("how_to_learn", "")).strip(),
                    }
                )
        return {
            "verdict": verdict,
            "summary": str(data.get("summary", "")).strip(),
            "recommendations": recs,
        }
    except (json.JSONDecodeError, KeyError):
        logger.warning("Failed to parse analysis JSON: %s", raw[:200])
        return _fallback([], missing)


def _rate_verdict(missing: list[str]) -> str:
    n = len(missing)
    if n == 0:
        return "Strong fit"
    if n <= 2:
        return "Moderate fit"
    if n <= 5:
        return "Partial fit"
    return "Weak fit"


def _fallback(matched: list[str], missing: list[str]) -> dict:
    top = missing[:3]
    return {
        "verdict": _rate_verdict(missing),
        "summary": (
            f"Candidate matches {len(matched)} skills and is missing "
            f"{len(missing)}. Focus on: {', '.join(top)}."
            if missing
            else "Candidate covers all required skills."
        ),
        "recommendations": [
            {
                "skill": s,
                "why_it_matters": "Listed as a required skill for this role.",
                "how_to_learn": "Take a focused online course or build a small project using it.",
            }
            for s in top
        ],
    }
