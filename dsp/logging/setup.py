"""Logging helpers for the Daily Stock Picker project."""

from __future__ import annotations

import sys

from loguru import logger

from dsp.config.settings import settings


def configure_logging() -> None:
    """Configure loguru logging sinks and formats."""

    logger.remove()
    log_dir = settings.data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(sys.stderr, level="INFO", enqueue=True, backtrace=False, diagnose=False)
    logger.add(
        log_dir / "app.log",
        rotation="7 days",
        retention="30 days",
        level="DEBUG",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )


def get_logger(name: str):  # type: ignore[explicit-any]
    """Return a child logger with contextual binding."""

    return logger.bind(context=name)


configure_logging()
