"""Database session and engine management."""

from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from dsp.config.settings import settings


class Base(DeclarativeBase):
    """Declarative base class."""


engine = create_async_engine(settings.db_url, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncSession:
    """Provide an async SQLAlchemy session."""

    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
