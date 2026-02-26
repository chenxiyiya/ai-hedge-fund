# AI Hedge Fund

## Cursor Cloud specific instructions

### Project Overview

AI-powered hedge fund simulator with a CLI and a full-stack web app (FastAPI backend + React/Vite frontend). See `README.md` for full details.

### Services

| Service | Command (from repo root) | Port |
|---------|--------------------------|------|
| Backend (FastAPI) | `poetry run uvicorn app.backend.main:app --reload --host 127.0.0.1 --port 8000` | 8000 |
| Frontend (Vite) | `cd app/frontend && npm run dev` | 5173 |

- The backend **must** be started from the repo root (not `app/backend/`) so `app.backend.main:app` module path resolves correctly.
- SQLite DB (`hedge_fund.db`) is auto-created on first backend startup — no migrations needed.
- A `.env` file in the repo root is required (copy from `.env.example`). At least one LLM API key must be set for AI agent analysis to function. Financial data for AAPL/GOOGL/MSFT/NVDA/TSLA is free without an API key.

### Lint / Test / Build

- **Python lint:** `poetry run black --check src/ app/ tests/`, `poetry run isort --check-only src/ app/ tests/`, `poetry run flake8 src/ app/ tests/ --max-line-length 420`
- **Frontend lint:** `cd app/frontend && npx eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0`
- **Tests:** `poetry run pytest tests/ -v` (43 tests, all pass)
- **Frontend build:** `cd app/frontend && npm run build` (pre-existing TS strict errors — dev server works fine)

### Gotchas

- **Case-sensitive imports on Linux:** The frontend import in `App.tsx` must use `./components/Layout` (capital L) to match the actual filename `Layout.tsx`. This was fixed in commit `edc8c73`.
- **Poetry path:** Poetry is installed to `~/.local/bin`. Ensure this is on `PATH` (`export PATH="$HOME/.local/bin:$PATH"`).
- **Python version:** Python `^3.11` is required. Python 3.13+ may cause compatibility issues (per project docs).
- **Frontend uses npm** (there is both `package-lock.json` and `pnpm-lock.yaml`; the `run.sh` script and README use `npm`).
