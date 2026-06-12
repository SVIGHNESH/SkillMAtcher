from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class MatchResponse(BaseModel):
    status: str
    match_id: int | None = None
    job_description: str
    resume: str
    matched: list[str] = []
    missing: list[str] = []
    total_jd_skills: int = 0
    total_resume_skills: int = 0
    match_rate: float = 0.0
    report_url: str | None = None


class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str


class HistoryItem(BaseModel):
    id: int
    jd_filename: str
    resume_filename: str
    matched_skills: list[str]
    missing_skills: list[str]
    total_jd: int
    total_resume: int
    match_rate: float
    report_filename: str
    created_at: str


class HistoryListResponse(BaseModel):
    items: list[HistoryItem]
    total: int
