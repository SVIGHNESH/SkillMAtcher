"""SQLite-backed cache for LLM responses.

Keyed on a hash of (operation, model, input). Repeated extractions/matches of
the same text skip the network round-trip entirely. Stored alongside the match
history DB so it survives restarts and is covered by the same Docker volume.
"""

import hashlib
import json
import sqlite3
from typing import Callable, TypeVar

from config import LLM_CACHE_ENABLED, LLM_MODEL
from db import get_conn

T = TypeVar("T")


def init_cache() -> None:
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS llm_cache (
            key        TEXT PRIMARY KEY,
            response   TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def make_key(operation: str, payload: str) -> str:
    raw = f"{operation}\x00{LLM_MODEL}\x00{payload}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_or_compute(operation: str, payload: str, compute: Callable[[], T]) -> T:
    """Return a cached result for (operation, model, payload) or compute+store it.

    Results are JSON-serialised, so ``compute`` must return JSON-friendly data
    (lists, dicts, primitives). On any cache error we fall back to computing.
    """
    if not LLM_CACHE_ENABLED:
        return compute()

    key = make_key(operation, payload)
    try:
        conn = get_conn()
        row = conn.execute(
            "SELECT response FROM llm_cache WHERE key = ?", (key,)
        ).fetchone()
        conn.close()
        if row is not None:
            return json.loads(row["response"])
    except (sqlite3.Error, json.JSONDecodeError):
        pass

    result = compute()

    try:
        conn = get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO llm_cache (key, response) VALUES (?, ?)",
            (key, json.dumps(result)),
        )
        conn.commit()
        conn.close()
    except (sqlite3.Error, TypeError):
        pass

    return result
