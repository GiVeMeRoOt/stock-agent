"""FastAPI service exposing the daily stock picker."""

from __future__ import annotations

from typing import Annotated, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI

from dsp.agents.orchestrator_agent import OrchestratorAgent
from dsp.config.settings import settings
from dsp.scheduler.jobs import start_scheduler
from dsp.utils.dates import current_market_date
from dsp.utils.types import StockPick

app = FastAPI(title="Daily Stock Picker", version="0.1.0")
_scheduler: AsyncIOScheduler | None = None


async def get_orchestrator() -> OrchestratorAgent:
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize()
    return orchestrator


OrchestratorDep = Annotated[OrchestratorAgent, Depends(get_orchestrator)]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/pick/today")
async def pick_today(orchestrator: OrchestratorDep) -> dict[str, Any]:
    today = current_market_date()
    pick = await orchestrator.run_daily_pick(today)
    return _serialize_pick(pick)


@app.on_event("startup")
async def startup_event() -> None:  # pragma: no cover - scheduler bootstrap
    if settings.environment == "test":
        return
    global _scheduler
    if _scheduler is None:
        _scheduler = start_scheduler()


def _serialize_pick(pick: StockPick) -> dict[str, Any]:
    return {
        "symbol": pick.symbol,
        "date": pick.pick_date.isoformat(),
        "confidence": pick.confidence,
        "rationale": pick.rationale,
        "constraints": pick.constraints,
        "features": pick.features,
        "disclaimer": pick.disclaimer,
    }


__all__ = ["app"]
