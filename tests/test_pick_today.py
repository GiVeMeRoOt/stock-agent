"""Tests for the daily stock picker workflow."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pytest
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


@pytest.mark.asyncio
async def test_orchestrator_generates_pick(tmp_path: Path) -> None:
    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"
    orchestrator = OrchestratorAgent()
    pick = await orchestrator.run_daily_pick(date(2024, 1, 2))
    assert pick.symbol
    assert 0 <= pick.confidence <= 1
    assert pick.features
    assert pick.disclaimer == "Not investment advice"


def test_api_pick_today(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"
    client = TestClient(app)
    response = client.get("/pick/today")
    assert response.status_code == 200
    payload = response.json()
    assert "symbol" in payload
    assert payload["disclaimer"] == "Not investment advice"


@pytest.mark.asyncio
async def test_cli_output_contains_disclaimer(tmp_path: Path) -> None:
    os.environ["DATA_DIR"] = str(tmp_path)
    os.environ["DB_URL"] = f"sqlite+aiosqlite:///{tmp_path}/dsp.db"
    markdown = await _run(date(2024, 1, 3))
    assert "Not investment advice" in markdown
    assert "Daily Stock Pick" in markdown
