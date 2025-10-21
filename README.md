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

### Run the API Locally

```bash
uvicorn dsp.api.main:app --reload
```

Generate today's pick via CLI:

```bash
python -m dsp.pick_today
```

### Using the Makefile

Common development workflows are wrapped in the `Makefile` for convenience:

```bash
# Install development dependencies and pre-commit hooks
make dev

# Run linting and the pytest suite
make test

# Produce today's recommendation via the CLI
make pick

# Build and deploy using Docker Compose (see Docker section below)
make deploy
```

### Using Docker

The project includes Docker assets for local evaluation or deployment. To
bootstrap the environment:

```bash
cp .env.example .env
docker compose build
docker compose up -d
```

Once the services are running, the FastAPI app is exposed on port 8000 by
default. You can follow logs with `docker compose logs -f app` and stop the
stack using `docker compose down` when finished. The same workflow is automated
via `make deploy` and the `scripts/deploy.sh` helper, which will load your
`.env`, build the image, run migrations, and start the services idempotently.

## Project Structure

- `dsp/agents/`: Agent implementations and orchestrator.
- `dsp/scrapers/`: Robust NSE scraping utilities.
- `dsp/storage/`: SQLAlchemy models and repository helpers (SQLite by default; configurable via env).
- `config/`: Application settings powered by Pydantic.
- `models/`: TODO stubs for model persistence.
- `tests/`: Pytest suite.
- `scripts/`: Deployment helpers.

> **Note:** This project is a research tool and outputs "Not investment advice" on every recommendation.
