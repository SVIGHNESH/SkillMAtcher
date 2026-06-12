import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_DIR = Path("data")
DB_PATH = DB_DIR / "skillmatcher.db"


def get_conn() -> sqlite3.Connection:
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# Columns added after the initial schema. Applied idempotently on init so
# existing databases pick them up without a destructive migration.
_EXTRA_COLUMNS = {
    "categories": "TEXT NOT NULL DEFAULT '{}'",
    "recommendations": "TEXT NOT NULL DEFAULT '{}'",
}


def init_db() -> None:
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_filename     TEXT NOT NULL,
            resume_filename TEXT NOT NULL,
            matched_skills  TEXT NOT NULL,
            missing_skills  TEXT NOT NULL,
            total_jd        INTEGER NOT NULL,
            total_resume    INTEGER NOT NULL,
            match_rate      REAL NOT NULL,
            report_filename TEXT NOT NULL,
            categories      TEXT NOT NULL DEFAULT '{}',
            recommendations TEXT NOT NULL DEFAULT '{}',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(matches)")}
    for col, ddl in _EXTRA_COLUMNS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE matches ADD COLUMN {col} {ddl}")
    conn.commit()
    conn.close()


def save_match(
    jd_filename: str,
    resume_filename: str,
    matched: list[str],
    missing: list[str],
    report_filename: str,
    categories: dict | None = None,
    recommendations: dict | None = None,
) -> int:
    conn = get_conn()
    total = len(matched) + len(missing)
    match_rate = (len(matched) / total * 100) if total > 0 else 0.0
    cur = conn.execute(
        """
        INSERT INTO matches (jd_filename, resume_filename, matched_skills,
                             missing_skills, total_jd, total_resume,
                             match_rate, report_filename, categories,
                             recommendations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            jd_filename,
            resume_filename,
            json.dumps(matched),
            json.dumps(missing),
            total,
            len(matched),
            round(match_rate, 1),
            report_filename,
            json.dumps(categories or {}),
            json.dumps(recommendations or {}),
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def list_matches(limit: int = 20, offset: int = 0) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM matches ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_match(match_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM matches WHERE id = ?", (match_id,)
    ).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def delete_match(match_id: int) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["matched_skills"] = json.loads(d["matched_skills"])
    d["missing_skills"] = json.loads(d["missing_skills"])
    d["categories"] = json.loads(d.get("categories") or "{}")
    d["recommendations"] = json.loads(d.get("recommendations") or "{}")
    return d
