from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class Recommendation(BaseModel):
    skill: str
    why_it_matters: str = ""
    how_to_learn: str = ""


class GapAnalysis(BaseModel):
    verdict: str = ""
    summary: str = ""
    recommendations: list[Recommendation] = []


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
    # category -> {"matched": [...], "missing": [...]} for the breakdown chart
    categories: dict = {}
    analysis: GapAnalysis = GapAnalysis()


class BatchMatchResponse(BaseModel):
    status: str
    job_description: str
    # Ranked by match_rate descending.
    items: list[MatchResponse] = []


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
    categories: dict = {}
    recommendations: dict = {}
    created_at: str


class HistoryListResponse(BaseModel):
    items: list[HistoryItem]
    total: int
