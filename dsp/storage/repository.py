"""Repository functions for database persistence."""

from __future__ import annotations

from sqlalchemy import select

from dsp.storage.database import Base, engine, get_session
from dsp.storage.models import DailyPick, LearningResult
from dsp.utils.types import LearningOutcome, StockPick


async def init_db() -> None:
    """Create database tables if they do not exist."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def upsert_pick(pick: StockPick) -> None:
    """Insert or update the daily pick record."""

    async with get_session() as session:
        existing = await session.scalar(
            select(DailyPick).where(DailyPick.pick_date == pick.pick_date)
        )
        if existing:
            existing.symbol = pick.symbol
            existing.confidence = pick.confidence
            existing.rationale = pick.rationale
            existing.constraints = {"items": pick.constraints}
            existing.features = pick.features
        else:
            record = DailyPick(
                pick_date=pick.pick_date,
                symbol=pick.symbol,
                confidence=pick.confidence,
                rationale=pick.rationale,
                constraints={"items": pick.constraints},
                features=pick.features,
            )
            session.add(record)
        await session.commit()


async def record_learning_outcome(outcome: LearningOutcome) -> None:
    """Persist realized outcomes for learning."""

    async with get_session() as session:
        existing = await session.scalar(
            select(LearningResult).where(LearningResult.pick_date == outcome.pick_date)
        )
        if existing:
            existing.symbol = outcome.symbol
            existing.open_price = outcome.open_price
            existing.close_price = outcome.close_price
            existing.pnl = outcome.pnl
            existing.extra_metadata = outcome.metadata
        else:
            record = LearningResult(
                pick_date=outcome.pick_date,
                symbol=outcome.symbol,
                open_price=outcome.open_price,
                close_price=outcome.close_price,
                pnl=outcome.pnl,
                extra_metadata=outcome.metadata,
            )
            session.add(record)
        await session.commit()
