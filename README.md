# Signal — Skill Match Intelligence

An AI-powered tool that compares a **job description** against one or more **résumés**.
Signal extracts and categorises skills from both sides using an LLM (Groq), identifies
matched and missing skills, scores the fit, and generates an actionable plan to close
the gaps — with a polished SvelteKit UI and a FastAPI backend.

![stack](https://img.shields.io/badge/FastAPI-Groq-166e63) ![ui](https://img.shields.io/badge/SvelteKit-5-ff3e00)

---

## Features

- **Match a JD against a résumé** — matched / missing skills, a fit verdict, and a match rate.
- **Skill-gap recommendations** — per missing skill: why it matters and how to learn it.
- **Paste or upload** — provide text directly or drop a `.txt` / `.pdf` / `.docx` file.
- **Rank several résumés** — upload many résumés against one JD and get a ranked leaderboard.
- **Category breakdown** — skills grouped by Languages, Frameworks, Tools, Data/ML, Soft Skills, Domain.
- **Export** — download reports as TXT or JSON, or print/save the result as a PDF.
- **History & shareable links** — every match is saved; open `/result/{id}` to revisit one.
- **LLM response caching** — repeat matches return instantly (SQLite-backed).
- **Light & dark themes**, fully responsive, accessible (keyboard nav, reduced-motion).

---

## Architecture

```
SkillMatcher/
├── main.py                  # CLI entry point
├── parsers.py               # .txt / .pdf / .docx text extraction
├── skill_extractor.py       # Groq LLM categorised skill extraction
├── matcher.py               # LLM skill comparison (fuzzy/synonym aware)
├── recommendations.py       # LLM skill-gap analysis & learning plan
├── cache.py                 # SQLite-backed LLM response cache
├── output.py                # TXT + JSON report builders
├── config.py                # Environment config
├── db.py                    # SQLite storage for match history
├── api/
│   ├── app.py               # FastAPI application
│   └── schemas.py           # Pydantic request/response models
├── frontend/                # SvelteKit + Tailwind CSS UI ("Signal")
├── Dockerfile.api           # API container
├── frontend/Dockerfile      # UI container
├── docker-compose.yml       # Full stack (api + web) with volumes
├── render.yaml              # Managed deploy (Render)
├── output/  data/           # Reports & SQLite DB (gitignored, mounted as volumes)
```

---

## Quick start — Docker (deploy anywhere)

The fastest way to run the whole stack. Requires Docker.

```bash
cp .env.example .env      # set LLM_API_KEY (Groq key) in .env
docker compose up --build
```

- UI:  http://localhost:3000
- API: http://localhost:8000

History and reports persist in named volumes across restarts.

> **Note:** `PUBLIC_API_BASE` is used by the **browser**, so it must be a host-reachable
> URL (`http://localhost:8000`) — *not* the compose-internal `http://api:8000`.
> The image reads it at runtime, so one build works against any backend.

---

## Local development

**Prerequisites:** Python 3.12+, Node.js 20+, a Groq API key (free at https://console.groq.com).

```bash
cp .env.example .env        # set LLM_API_KEY
uv sync                     # Python deps
cd frontend && npm install  # frontend deps
```

**Run:**

```bash
# Terminal 1 — API
uv run uvicorn api.app:app --reload --port 8000

# Terminal 2 — UI
cd frontend && npm run dev   # http://localhost:5173
```

**CLI mode:** `uv run python main.py`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/match` | Match one JD + one résumé (files **or** `jd_text`/`resume_text`) |
| `POST` | `/api/match/batch` | Match one JD against many résumés → ranked list |
| `GET` | `/api/report/{filename}?format=txt\|json` | Download a report |
| `GET` | `/api/history` | List past matches (paginated) |
| `GET` | `/api/history/{id}` | Match detail (powers shareable `/result/{id}`) |
| `DELETE` | `/api/history/{id}` | Delete a match record |

---

## Configuration

All via `.env` (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `LLM_API_KEY` | — | Groq API key (required) |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible API base |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model name |
| `LLM_CACHE_ENABLED` | `true` | Cache LLM responses in SQLite |
| `RATE_LIMIT` | _(empty)_ | Optional per-client limit, e.g. `30/minute` |
| `CORS_ORIGINS` | localhost dev origins | Comma-separated allowed origins (`*` = all) |
| `PUBLIC_API_BASE` | `http://localhost:8000` | Browser-facing API URL (frontend, runtime) |

Any OpenAI-compatible provider works by changing `LLM_BASE_URL` / `LLM_MODEL`.

---

## Deploying to managed platforms

`render.yaml` defines both services for [Render](https://render.com). After the first deploy,
set `LLM_API_KEY` and `CORS_ORIGINS` on the API service and `PUBLIC_API_BASE` on the UI service
in the dashboard. The same Docker images work on Railway, Fly.io, or any container host.

---

## Tech Stack

- **Backend:** Python · FastAPI · Groq (LLaMA 3.3) · SQLite
- **Frontend:** SvelteKit 5 · Tailwind CSS v4 · Bricolage Grotesque + Public Sans + JetBrains Mono
- **Deploy:** Docker / docker-compose · Render
