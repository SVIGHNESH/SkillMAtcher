import json
import logging
import os
import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

import cache
from config import RATE_LIMIT
from db import delete_match, get_match, init_db, list_matches, save_match
from matcher import match_skills
from output import REPORT_DIR, build_json_report, write_report
from parsers import read_document
from recommendations import analyze_gap
from skill_extractor import extract_skills, skill_names

from .schemas import (
    BatchMatchResponse,
    HealthResponse,
    HistoryItem,
    HistoryListResponse,
    MatchResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skillmatcher.api")

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    cache.init_cache()
    logger.info("SkillMatcher API started")
    yield


app = FastAPI(title="SkillMatcher API", version="0.2.0", lifespan=lifespan)

# Dynamic CORS from environment, defaulting to the local dev origins.
allowed_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173"
).split(",")
if "*" in allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional rate limiting on the match endpoints (slowapi). Enabled only when
# RATE_LIMIT is set, so local dev is unaffected.
limiter = None
if RATE_LIMIT:
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded
        from slowapi.util import get_remote_address

        limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info("Rate limiting enabled: %s", RATE_LIMIT)
    except ImportError:
        logger.warning("RATE_LIMIT set but slowapi not installed; skipping")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.0f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Input resolution & core pipeline
# ---------------------------------------------------------------------------


async def _resolve_input(
    file: UploadFile | None, text: str | None, label: str, tmp_dir: Path
) -> tuple[str, str]:
    """Return ``(extracted_text, display_name)`` from a file OR pasted text.

    Exactly one of ``file``/``text`` must be provided.
    """
    has_text = bool(text and text.strip())
    has_file = file is not None and file.filename

    if has_file and has_text:
        raise HTTPException(
            status_code=400, detail=f"Provide either a {label} file or text, not both"
        )
    if not has_file and not has_text:
        raise HTTPException(
            status_code=400, detail=f"No {label} provided (upload a file or paste text)"
        )

    if has_text:
        return text.strip(), f"{label} (pasted)"

    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported {label} format '{ext}'. Supported: .txt, .pdf, .docx",
        )
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"{label} file exceeds 10 MB limit")

    tmp_path = tmp_dir / (file.filename or f"{label}.txt")
    tmp_path.write_bytes(data)
    try:
        extracted = read_document(str(tmp_path))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e))
    if not extracted.strip():
        raise HTTPException(
            status_code=400, detail=f"No extractable text found in {label} file"
        )
    return extracted, Path(file.filename).name


def _build_categories(jd_skills: list[dict], matched: list[str], missing: list[str]) -> dict:
    """Group matched/missing JD skills by their category for the chart."""
    cat_of = {s["skill"]: s.get("category", "Domain") for s in jd_skills}
    out: dict[str, dict[str, list[str]]] = {}
    for name in matched:
        out.setdefault(cat_of.get(name, "Domain"), {"matched": [], "missing": []})[
            "matched"
        ].append(name)
    for name in missing:
        out.setdefault(cat_of.get(name, "Domain"), {"matched": [], "missing": []})[
            "missing"
        ].append(name)
    return out


def _run_pipeline(
    jd_text: str, resume_text: str, jd_name: str, resume_name: str
) -> MatchResponse:
    """Extract → match → analyse → persist for one JD/resume pair."""
    try:
        jd_skills = extract_skills(jd_text, "Job Description")
        resume_skills = extract_skills(resume_text, "Resume")
        jd_names = skill_names(jd_skills)
        resume_named = skill_names(resume_skills)
        matched, missing = match_skills(jd_names, resume_named)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"LLM processing failed: {e}")

    total = len(matched) + len(missing)
    match_pct = (len(matched) / total * 100) if total > 0 else 0.0
    categories = _build_categories(jd_skills, matched, missing)
    analysis = analyze_gap(jd_name, matched, missing)

    report_path = write_report(jd_name, resume_name, matched, missing, match_pct, analysis)
    report_filename = Path(report_path).name

    match_id = save_match(
        jd_filename=jd_name,
        resume_filename=resume_name,
        matched=matched,
        missing=missing,
        report_filename=report_filename,
        categories=categories,
        recommendations=analysis,
    )

    return MatchResponse(
        status="success",
        match_id=match_id,
        job_description=jd_name,
        resume=resume_name,
        matched=matched,
        missing=missing,
        total_jd_skills=total,
        total_resume_skills=len(resume_named),
        match_rate=round(match_pct, 1),
        report_url=f"/api/report/{report_filename}",
        categories=categories,
        analysis=analysis,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@app.post("/api/match", response_model=MatchResponse)
async def match_endpoint(
    jd_file: UploadFile | None = File(None),
    resume_file: UploadFile | None = File(None),
    jd_text: str | None = Form(None),
    resume_text: str | None = Form(None),
):
    with tempfile.TemporaryDirectory(prefix="skillmatcher_") as tmp:
        tmp_dir = Path(tmp)
        jd_doc, jd_name = await _resolve_input(jd_file, jd_text, "Job Description", tmp_dir)
        resume_doc, resume_name = await _resolve_input(
            resume_file, resume_text, "Resume", tmp_dir
        )
    return _run_pipeline(jd_doc, resume_doc, jd_name, resume_name)


@app.post("/api/match/batch", response_model=BatchMatchResponse)
async def match_batch_endpoint(
    jd_file: UploadFile | None = File(None),
    jd_text: str | None = Form(None),
    resume_files: list[UploadFile] = File(default=[]),
):
    if not resume_files:
        raise HTTPException(status_code=400, detail="No resume files provided")

    with tempfile.TemporaryDirectory(prefix="skillmatcher_") as tmp:
        tmp_dir = Path(tmp)
        jd_doc, jd_name = await _resolve_input(jd_file, jd_text, "Job Description", tmp_dir)

        results: list[MatchResponse] = []
        for rf in resume_files:
            resume_doc, resume_name = await _resolve_input(rf, None, "Resume", tmp_dir)
            results.append(_run_pipeline(jd_doc, resume_doc, jd_name, resume_name))

    results.sort(key=lambda r: r.match_rate, reverse=True)
    return BatchMatchResponse(status="success", job_description=jd_name, items=results)


@app.get("/api/report/{filename}")
def get_report(filename: str, format: str = Query("txt", pattern="^(txt|json)$")):
    # Guard against path traversal — only serve flat names from REPORT_DIR.
    safe = Path(filename).name
    report_file = REPORT_DIR / safe
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    if format == "json":
        # Rebuild JSON from the persisted match keyed by this report filename.
        for item in list_matches(limit=100):
            if item["report_filename"] == safe:
                analysis = item.get("recommendations") or {}
                body = build_json_report(
                    item["jd_filename"],
                    item["resume_filename"],
                    item["matched_skills"],
                    item["missing_skills"],
                    item["match_rate"],
                    item.get("categories"),
                    analysis,
                )
                return JSONResponse(content=json.loads(body))
        raise HTTPException(status_code=404, detail="Report metadata not found")

    return PlainTextResponse(
        report_file.read_text(encoding="utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{safe}"'},
    )


@app.get("/api/history", response_model=HistoryListResponse)
def history_list(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    items = list_matches(limit, offset)
    return HistoryListResponse(items=items, total=len(items))


@app.get("/api/history/{match_id}", response_model=HistoryItem)
def history_detail(match_id: int):
    item = get_match(match_id)
    if not item:
        raise HTTPException(status_code=404, detail="Match not found")
    return HistoryItem(**item)


@app.delete("/api/history/{match_id}")
def history_delete(match_id: int):
    if not delete_match(match_id):
        raise HTTPException(status_code=404, detail="Match not found")
    return {"status": "deleted"}
