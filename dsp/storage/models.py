"""SQLAlchemy models for the daily stock picker service."""

from __future__ import annotations

from datetime import date

from sqlalchemy import JSON, Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from dsp.storage.database import Base


class DailyPick(Base):
    """Stores daily pick recommendations."""

    __tablename__ = "daily_picks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pick_date: Mapped[date] = mapped_column(Date, index=True, unique=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(String(1024))
    constraints: Mapped[dict] = mapped_column(JSON)
    features: Mapped[dict] = mapped_column(JSON)


class LearningResult(Base):
    """Stores realized outcomes for learning."""

    __tablename__ = "learning_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pick_date: Mapped[date] = mapped_column(Date, index=True, unique=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    open_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float)
    pnl: Mapped[float] = mapped_column(Float)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
