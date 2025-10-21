"""Scheduler configuration for running the daily pick job."""

from __future__ import annotations

import asyncio
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from dsp.agents.orchestrator_agent import OrchestratorAgent
from dsp.config.settings import settings
from dsp.logging.setup import get_logger

logger = get_logger(__name__)


async def _run_daily_job() -> None:
    orchestrator = OrchestratorAgent()
    today = datetime.now(pytz.timezone(settings.timezone)).date()
    logger.info("Scheduler triggered for %s", today)
    await orchestrator.run_daily_pick(today)


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    hour, minute = map(int, settings.scheduler_daily_time.split(":"))
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(
        lambda: asyncio.create_task(_run_daily_job()),
        trigger=trigger,
        id="daily-pick",
    )
    scheduler.start()
    logger.info("Scheduler started for %02d:%02d %s", hour, minute, settings.timezone)
    return scheduler


__all__ = ["start_scheduler"]
