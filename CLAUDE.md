# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
uv sync                                          # install Python deps
uv run python main.py                            # CLI mode
uv run uvicorn api.app:app --reload --port 8000  # API server
```

### Frontend
```bash
cd frontend && npm install   # install Node deps
cd frontend && npm run dev   # dev server (http://localhost:5173)
cd frontend && npm run check # type-check
cd frontend && npm run build # production build (adapter-node)
```

### Docker (full stack)
```bash
cp .env.example .env          # set LLM_API_KEY
docker compose up --build     # UI :3000, API :8000, persistent volumes
```

## Architecture

The app has two entry points that share the same core modules:

- **`main.py`** — interactive CLI loop
- **`api/app.py`** — FastAPI server, calls the same core modules

**Core pipeline** (shared by both):
1. `parsers.py` — extracts text from `.txt`, `.pdf`, `.docx` files
2. `skill_extractor.py` — Groq LLM returns **categorised** skills (`{skill, category}`); `skill_names()` flattens to a name list for matching
3. `matcher.py` — LLM compares JD skills vs resume skills → `(matched, missing)` lists
4. `recommendations.py` — LLM produces a fit verdict + per-missing-skill learning plan (graceful fallback)
5. `cache.py` — SQLite-backed cache wrapping every LLM call (`get_or_compute`)
6. `output.py` — writes a `.txt` report and builds a JSON report
7. `db.py` — persists results (incl. `categories`, `recommendations`) to SQLite at `data/skillmatcher.db`; `init_db()` idempotently migrates new columns

`api/app.py` exposes single (`/api/match`) and batch (`/api/match/batch`) endpoints, both accepting **files or pasted text** via `_resolve_input`; `_run_pipeline` runs the full extract→match→analyse→persist flow.

**Frontend** (`frontend/`) is SvelteKit 5 + Tailwind CSS v4, design system "Signal" (warm paper, deep-teal accent, semantic score colors). API base is read at **runtime** from `PUBLIC_API_BASE` (`$env/dynamic/public`) — not build-inlined — so one Docker image works anywhere. Key components under `frontend/src/lib/components/` (FileDropZone, InputSource, ScoreRing, SkillChips, CategoryBreakdown, RecommendationCard, ResultsCard, ResumeLeaderboard). Routes: `/` (match), `/history`, `/result/[id]` (shareable).

## Configuration

All config is via `.env` (copy from `.env.example`):
- `LLM_API_KEY` — Groq API key (required)
- `LLM_BASE_URL` — defaults to Groq's OpenAI-compatible endpoint
- `LLM_MODEL` — defaults to `llama-3.3-70b-versatile`
- `CORS_ORIGINS` — comma-separated origins (default: localhost:5173/4173)

The OpenAI Python SDK is used with Groq's base URL — any OpenAI-compatible provider works by changing `LLM_BASE_URL` and `LLM_MODEL`.
