# Daily Stock Picker

Daily Stock Picker is an agentic Python 3.11 service that selects one NSE-listed stock every morning using EOD-only signals. The project provides:

- A FastAPI service exposing `/health` and `/pick/today` endpoints.
- A CLI entry point available via `python -m dsp.pick_today`.
- An APScheduler job that triggers the daily pick at 08:30 Asia/Kolkata.
- Modular agents for ingestion, feature engineering, research, selection, learning, and reporting.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

Run the API:

```bash
uvicorn dsp.api.main:app --reload
```

Generate today's pick via CLI:

```bash
python -m dsp.pick_today
```

Run tests and formatters using the provided `Makefile` targets.

## Project Structure

- `dsp/agents/`: Agent implementations and orchestrator.
- `dsp/scrapers/`: Robust NSE scraping utilities.
- `dsp/storage/`: SQLAlchemy models and repository helpers (SQLite by default; configurable via env).
- `config/`: Application settings powered by Pydantic.
- `models/`: TODO stubs for model persistence.
- `tests/`: Pytest suite.
- `scripts/`: Deployment helpers.

> **Note:** This project is a research tool and outputs "Not investment advice" on every recommendation.
