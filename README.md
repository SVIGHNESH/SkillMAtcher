# SkillMatcher

An AI-powered job description vs. resume skill matching tool. Upload a job description and a resume — SkillMatcher extracts skills from both using an LLM (Groq), compares them, and generates a detailed gap analysis report.

---

## Architecture

```
SkillMatcher/
├── main.py                  # CLI entry point
├── parsers.py               # .txt / .pdf / .docx text extraction
├── skill_extractor.py       # Groq LLM skill extraction
├── matcher.py               # LLM skill comparison
├── output.py                # .txt report writer
├── config.py                # Environment config (API key, model)
├── db.py                    # SQLite storage for match history
├── api/
│   ├── app.py               # FastAPI application (6 endpoints)
│   └── schemas.py           # Pydantic request/response models
├── frontend/                # SvelteKit + Tailwind CSS UI
│   └── src/
│       ├── lib/components/  # FileDropZone, MatchGauge, ResultsCard
│       └── routes/          # Main page, history page
├── output/                  # Generated .txt reports (gitignored)
└── data/                    # SQLite database (gitignored)
```

---

## Prerequisites

- Python 3.12+
- Node.js 20+
- A Groq API key (free at https://console.groq.com)

---

## Setup

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env and set your Groq API key:
#   LLM_API_KEY=gsk_your_key_here
```

### 2. Python dependencies

```bash
uv sync
```

### 3. Frontend dependencies

```bash
cd frontend && npm install
```

---

## Usage

### CLI Mode

```bash
uv run python main.py
```

Follow the interactive prompts to enter JD and resume file paths.

### Web UI (recommended)

**Terminal 1 — Backend:**
```bash
uv run uvicorn api.app:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend && npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/match` | Upload JD + resume files (multipart) |
| `GET` | `/api/report/{filename}` | Download .txt report |
| `GET` | `/api/history` | List past matches (paginated) |
| `GET` | `/api/history/{id}` | Match detail |
| `DELETE` | `/api/history/{id}` | Delete a match record |

---

## Configuration

All via `.env` file:

| Variable | Default | Description |
|---|---|---|
| `LLM_API_KEY` | — | Groq API key (required) |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible API base |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model name |

---

## Supported File Formats

- Plain text (`.txt`)
- PDF (`.pdf`)
- Microsoft Word (`.docx`)

---

## Tech Stack

- **Backend:** Python, FastAPI, Groq (LLaMA 3.3)
- **Frontend:** SvelteKit, Tailwind CSS v4
- **Database:** SQLite
- **Fonts:** Chakra Petch + JetBrains Mono
