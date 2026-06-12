# --- SkillMatcher API (FastAPI + uv) ---
FROM python:3.12-slim

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project

# Copy application code (api/, core modules, main.py)
COPY . .
RUN uv sync

# SQLite DB (data/) and reports (output/) are mounted as volumes in compose
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
