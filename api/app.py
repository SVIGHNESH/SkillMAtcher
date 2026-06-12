from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse

from db import delete_match, init_db, list_matches, save_match, get_match
from matcher import match_skills
from output import REPORT_DIR, write_report
from parsers import read_document
from skill_extractor import extract_skills

from .schemas import (
    ErrorResponse,
    HealthResponse,
    HistoryItem,
    HistoryListResponse,
    MatchResponse,
)

import os

app = FastAPI(title="SkillMatcher API", version="0.1.0")

# Allow dynamic CORS from environment or default to local/all
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173").split(",")
if "*" in allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/api/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@app.post("/api/match", response_model=MatchResponse)
async def match_endpoint(
    jd_file: UploadFile = File(...),
    resume_file: UploadFile = File(...),
):
    jd_ext = Path(jd_file.filename or "").suffix.lower()
    resume_ext = Path(resume_file.filename or "").suffix.lower()

    if jd_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported JD file format '{jd_ext}'. Supported: .txt, .pdf, .docx",
        )
    if resume_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported resume file format '{resume_ext}'. Supported: .txt, .pdf, .docx",
        )

    jd_bytes = await jd_file.read()
    resume_bytes = await resume_file.read()

    if len(jd_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="JD file exceeds 10 MB limit"
        )
    if len(resume_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="Resume file exceeds 10 MB limit"
        )

    tmp_dir = Path("/tmp/skillmatcher")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    jd_tmp = tmp_dir / (jd_file.filename or "jd.txt")
    resume_tmp = tmp_dir / (resume_file.filename or "resume.txt")
    jd_tmp.write_bytes(jd_bytes)
    resume_tmp.write_bytes(resume_bytes)

    try:
        jd_text = read_document(str(jd_tmp))
        resume_text = read_document(str(resume_tmp))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in JD file",
        )
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in resume file",
        )

    try:
        jd_skills = extract_skills(jd_text, "Job Description")
        resume_skills = extract_skills(resume_text, "Resume")
        matched, missing = match_skills(jd_skills, resume_skills)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM processing failed: {e}",
        )

    total = len(matched) + len(missing)
    match_pct = (len(matched) / total * 100) if total > 0 else 0.0

    jd_name = Path(jd_file.filename or "jd.txt").name
    resume_name = Path(resume_file.filename or "resume.txt").name
    report_path = write_report(
        jd_name, resume_name, matched, missing, match_pct
    )
    report_filename = Path(report_path).name

    match_id = save_match(
        jd_filename=jd_name,
        resume_filename=resume_name,
        matched=matched,
        missing=missing,
        report_filename=report_filename,
    )

    return MatchResponse(
        status="success",
        match_id=match_id,
        job_description=jd_name,
        resume=resume_name,
        matched=matched,
        missing=missing,
        total_jd_skills=total,
        total_resume_skills=len(resume_skills),
        match_rate=round(match_pct, 1),
        report_url=f"/api/report/{report_filename}",
    )


@app.get("/api/report/{filename}")
def get_report(filename: str):
    report_file = REPORT_DIR / filename
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return PlainTextResponse(
        report_file.read_text(encoding="utf-8"),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
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
