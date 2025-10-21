"""Date and time helpers for the Daily Stock Picker service."""

from __future__ import annotations

from datetime import date, datetime

import pytz

from dsp.config.settings import settings


def current_market_date(timezone_name: str | None = None) -> date:
    """Return today's date in the configured market timezone.

    Parameters
    ----------
    timezone_name:
        Optional override for the timezone to evaluate. When omitted the
        application-wide configured timezone is used.
    """
    tz = pytz.timezone(timezone_name or settings.timezone)
    # datetime.now with an explicit timezone ensures hosts in other timezones
    # still evaluate the pick for the target market trading day.
    return datetime.now(tz=tz).date()


__all__ = ["current_market_date"]
