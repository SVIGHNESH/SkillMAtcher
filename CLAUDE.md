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
```

## Architecture

The app has two entry points that share the same core modules:

- **`main.py`** — interactive CLI loop
- **`api/app.py`** — FastAPI server (6 endpoints), calls the same core modules

**Core pipeline** (shared by both):
1. `parsers.py` — extracts text from `.txt`, `.pdf`, `.docx` files
2. `skill_extractor.py` — sends text to Groq LLM, returns list of skills
3. `matcher.py` — LLM compares JD skills vs resume skills → `(matched, missing)` lists
4. `output.py` — writes `.txt` report to `output/` directory
5. `db.py` — persists match results to SQLite at `data/skillmatcher.db`

**Frontend** (`frontend/`) is SvelteKit + Tailwind CSS v4. Key components are under `frontend/src/lib/components/` (FileDropZone, MatchGauge, ResultsCard). History browsing lives in `frontend/src/routes/`.

## Configuration

All config is via `.env` (copy from `.env.example`):
- `LLM_API_KEY` — Groq API key (required)
- `LLM_BASE_URL` — defaults to Groq's OpenAI-compatible endpoint
- `LLM_MODEL` — defaults to `llama-3.3-70b-versatile`
- `CORS_ORIGINS` — comma-separated origins (default: localhost:5173/4173)

The OpenAI Python SDK is used with Groq's base URL — any OpenAI-compatible provider works by changing `LLM_BASE_URL` and `LLM_MODEL`.
