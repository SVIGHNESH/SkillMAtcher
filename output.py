import datetime
import json
import pathlib

REPORT_DIR = pathlib.Path("output")


def write_report(
    jd_name: str,
    resume_name: str,
    matched: list[str],
    missing: list[str],
    match_pct: float,
    analysis: dict | None = None,
) -> str:
    """Write a human-readable .txt report and return its path."""
    REPORT_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = REPORT_DIR / f"skillmatcher_report_{ts}.txt"

    lines = [
        "=" * 48,
        "  SKILLMATCHER REPORT",
        "=" * 48,
        f"  Generated:    {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Job Desc:     {jd_name}",
        f"  Resume:       {resume_name}",
        "=" * 48,
        "",
    ]

    if analysis:
        lines.append(f"VERDICT: {analysis.get('verdict', '-')}")
        if analysis.get("summary"):
            lines.append(f"  {analysis['summary']}")
        lines.append("")

    lines.append(f"[OK] MATCHED SKILLS ({len(matched)} / {len(matched) + len(missing)})")
    lines.append("-" * 40)
    if matched:
        for s in matched:
            lines.append(f"  + {s}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"[!!] MISSING SKILLS ({len(missing)})")
    lines.append("-" * 40)
    if missing:
        for s in missing:
            lines.append(f"  - {s}")
    else:
        lines.append("  (none)")
    lines.append("")

    recs = (analysis or {}).get("recommendations") or []
    if recs:
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for r in recs:
            lines.append(f"  * {r.get('skill', '')}")
            if r.get("why_it_matters"):
                lines.append(f"      Why:  {r['why_it_matters']}")
            if r.get("how_to_learn"):
                lines.append(f"      Learn: {r['how_to_learn']}")
        lines.append("")

    lines.append("=" * 48)
    lines.append(f"         Match Rate: {match_pct:.1f}%")
    lines.append("=" * 48)
    lines.append("")

    filename.write_text("\n".join(lines), encoding="utf-8")
    return str(filename)


def build_json_report(
    jd_name: str,
    resume_name: str,
    matched: list[str],
    missing: list[str],
    match_pct: float,
    categories: dict | None = None,
    analysis: dict | None = None,
) -> str:
    """Serialise a full report as a JSON string (for the export endpoint)."""
    payload = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "job_description": jd_name,
        "resume": resume_name,
        "match_rate": round(match_pct, 1),
        "matched": matched,
        "missing": missing,
        "categories": categories or {},
        "analysis": analysis or {},
    }
    return json.dumps(payload, indent=2)
