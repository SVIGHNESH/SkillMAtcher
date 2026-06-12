import datetime
import pathlib

REPORT_DIR = pathlib.Path("output")


def write_report(
    jd_name: str,
    resume_name: str,
    matched: list[str],
    missing: list[str],
    match_pct: float,
) -> str:
    REPORT_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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

    lines.append("=" * 48)
    lines.append(f"         Match Rate: {match_pct:.1f}%")
    lines.append("=" * 48)
    lines.append("")

    filename.write_text("\n".join(lines), encoding="utf-8")
    return str(filename)
