"""Tests for the daily stock picker workflow."""

from __future__ import annotations

import asyncio
import os
from datetime import date, datetime
from pathlib import Path

import pytest
import pytz

# FastAPI relies on pydantic_core.__version__ which is missing in certain
# stripped-down binary builds. Set it explicitly for deterministic tests.
try:  # pragma: no cover - defensive guard for environments missing attribute
    import pydantic_core  # type: ignore

    if not hasattr(pydantic_core, "__version__"):
        pydantic_core.__version__ = "2.41.4"
except Exception:  # pragma: no cover - best effort shim
    pass

from fastapi.testclient import TestClient

# Configure environment before importing project modules
DEFAULT_TEST_DATA_DIR = Path("./test-data")
os.environ.setdefault("DATA_DIR", str(DEFAULT_TEST_DATA_DIR))
os.environ.setdefault("DB_URL", "sqlite+aiosqlite:///./test-data/dsp.db")
os.environ.setdefault("ENVIRONMENT", "test")
DEFAULT_TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

from dsp.agents.orchestrator_agent import OrchestratorAgent  # noqa: E402
from dsp.api.main import app  # noqa: E402
from dsp.cli.pick_today import _run  # noqa: E402
from dsp.config.settings import settings  # noqa: E402
from dsp.utils.types import StockPick  # noqa: E402


def test_orchestrator_generates_pick(tmp_path: Path) -> None:
    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"
    orchestrator = OrchestratorAgent()
    pick = asyncio.run(orchestrator.run_daily_pick(date(2024, 1, 2)))
    assert pick.symbol
    assert 0 <= pick.confidence <= 1
    assert pick.features
    assert pick.disclaimer == "Not investment advice"


def test_api_pick_today(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"

    class DummyOrchestrator:
        async def initialize(self) -> None:
            return None

        async def run_daily_pick(self, run_date: date) -> StockPick:
            captured_dates.append(run_date)
            return StockPick(
                symbol="TEST",
                pick_date=run_date,
                confidence=0.75,
                rationale="Stub rationale",
                constraints=["Constraint"],
                features={"feature": 1.0},
            )

    captured_dates: list[date] = []
    monkeypatch.setattr("dsp.api.main.OrchestratorAgent", DummyOrchestrator)

    real_datetime = datetime

    class StrictDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            if tz is None:
                raise AssertionError(
                    "Timezone must be provided for market date computation"
                )
            return real_datetime.now(tz=tz)

    import dsp.utils.dates as dates_module

    monkeypatch.setattr(dates_module, "datetime", StrictDatetime)
    monkeypatch.setattr(settings, "timezone", "Asia/Kolkata")

    client = TestClient(app)
    response = client.get("/pick/today")
    assert response.status_code == 200
    payload = response.json()
    assert "symbol" in payload
    assert payload["disclaimer"] == "Not investment advice"
    assert captured_dates, "Orchestrator should receive the computed date"
    expected_date = real_datetime.now(pytz.timezone(settings.timezone)).date()
    assert captured_dates[0] == expected_date


def test_ui_homepage_renders(tmp_path: Path) -> None:
    """Ensure the HTML front-end renders with the configured timezone."""

    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"
    os.environ["ENVIRONMENT"] = "test"

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Daily Stock Picker" in response.text
    assert settings.timezone in response.text
    assert "Start Analysis" in response.text
    assert "Logs" in response.text


def test_cli_output_contains_disclaimer(tmp_path: Path) -> None:
    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"
    markdown = asyncio.run(_run(date(2024, 1, 3)))
    assert "Not investment advice" in markdown
    assert "Daily Stock Pick" in markdown
