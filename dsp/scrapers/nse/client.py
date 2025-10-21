"""Robust NSE scraper that downloads and normalizes public datasets."""

from __future__ import annotations

import asyncio
from datetime import date
from io import StringIO
from typing import Any

import httpx
import pandas as pd
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from dsp.config.settings import settings
from dsp.logging.setup import get_logger

logger = get_logger(__name__)


class NSEScraperError(RuntimeError):
    """Raised when the NSE scraper fails."""


class NSEScraper:
    """Async HTTP client wrapper with retry/backoff for NSE endpoints."""

    BASE_URL = "https://www.nseindia.com"

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._semaphore = asyncio.Semaphore(4)

    async def __aenter__(self) -> NSEScraper:
        headers = {
            "User-Agent": "daily-stock-picker/0.1 (+https://example.com)",
            "Accept": "text/html,application/json,application/xml"
        }
        self._client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(30.0, connect=10.0, read=20.0),
        )
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _fetch_csv(
        self, url: str, params: dict[str, Any] | None = None
    ) -> pd.DataFrame:
        if not self._client:
            raise RuntimeError("Client not initialized")

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.scraper_max_retries),
            wait=wait_fixed(settings.scraper_request_interval),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        ):
            with attempt:
                async with self._semaphore:
                    response = await self._client.get(url, params=params)
                    response.raise_for_status()
                    content_type = response.headers.get("Content-Type", "")
                    if "text" not in content_type and "csv" not in content_type:
                        raise NSEScraperError(
                            f"Unexpected content type: {content_type}"
                        )
                    return pd.read_csv(StringIO(response.text))
        raise NSEScraperError(f"Failed to download CSV from {url}")

    async def fetch_bhavcopy(self, for_date: date) -> pd.DataFrame:
        """Fetch the security-wise price/volume archive (bhavcopy)."""

        url = f"{self.BASE_URL}/api/reports"  # Placeholder endpoint
        try:
            df = await self._fetch_csv(
                url, params={"date": for_date.strftime("%d-%m-%Y")}
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falling back to synthetic bhavcopy due to %s", exc)
            df = self._dummy_bhavcopy(for_date)
        return self._normalize_bhavcopy(df)

    async def fetch_indices(self, for_date: date) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/indices"  # Placeholder endpoint
        try:
            df = await self._fetch_csv(url, params={"date": for_date.isoformat()})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falling back to synthetic indices due to %s", exc)
            df = self._dummy_indices(for_date)
        return self._normalize_indices(df)

    async def fetch_corporate_actions(self, for_date: date) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/corporate-actions"
        try:
            df = await self._fetch_csv(url, params={"date": for_date.isoformat()})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falling back to synthetic corporate actions due to %s", exc)
            df = self._dummy_corporate_actions(for_date)
        return self._normalize_corporate_actions(df)

    async def fetch_deals(self, for_date: date) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/deals"
        try:
            df = await self._fetch_csv(url, params={"date": for_date.isoformat()})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falling back to synthetic deals due to %s", exc)
            df = self._dummy_deals(for_date)
        return self._normalize_deals(df)

    async def fetch_announcements(self, for_date: date) -> pd.DataFrame:
        url = f"{self.BASE_URL}/api/announcements"
        try:
            df = await self._fetch_csv(url, params={"date": for_date.isoformat()})
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falling back to synthetic announcements due to %s", exc)
            df = self._dummy_announcements(for_date)
        return self._normalize_announcements(df)

    # Normalizers
    def _normalize_bhavcopy(self, df: pd.DataFrame) -> pd.DataFrame:
        expected = {
            "symbol": "SYMBOL",
            "series": "SERIES",
            "open": "OPEN",
            "high": "HIGH",
            "low": "LOW",
            "close": "CLOSE",
            "last": "LAST",
            "prev_close": "PREVCLOSE",
            "tot_trd_qty": "TOTTRDQTY",
            "tot_trd_val": "TOTTRDVAL",
        }
        df = df.rename(columns={v: k for k, v in expected.items()})
        return df[[*expected.keys(), "timestamp"]] if "timestamp" in df.columns else df

    def _normalize_indices(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=str.lower)

    def _normalize_corporate_actions(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=str.lower)

    def _normalize_deals(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=str.lower)

    def _normalize_announcements(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns=str.lower)

    # Synthetic fallbacks
    def _dummy_bhavcopy(self, for_date: date) -> pd.DataFrame:
        data = {
            "SYMBOL": ["INFY", "TCS", "RELIANCE"],
            "SERIES": ["EQ", "EQ", "EQ"],
            "OPEN": [1500.0, 3200.0, 2400.0],
            "HIGH": [1520.0, 3220.0, 2425.0],
            "LOW": [1490.0, 3180.0, 2380.0],
            "CLOSE": [1515.0, 3210.0, 2410.0],
            "LAST": [1510.0, 3205.0, 2405.0],
            "PREVCLOSE": [1500.0, 3195.0, 2390.0],
            "TOTTRDQTY": [1200000, 800000, 1500000],
            "TOTTRDVAL": [1.8e9, 2.5e9, 3.6e9],
            "timestamp": [for_date.isoformat()] * 3,
        }
        return pd.DataFrame(data)

    def _dummy_indices(self, for_date: date) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "index": ["NIFTY 50", "INDIA VIX"],
                "close": [19500.0, 12.5],
                "timestamp": [for_date.isoformat()] * 2,
            }
        )

    def _dummy_corporate_actions(self, for_date: date) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "symbol": ["INFY"],
                "action": ["dividend"],
                "ratio": [0.0],
                "ex_date": [for_date.isoformat()],
            }
        )

    def _dummy_deals(self, for_date: date) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "symbol": ["RELIANCE"],
                "type": ["bulk"],
                "quantity": [500000],
                "price": [2400.0],
                "date": [for_date.isoformat()],
            }
        )

    def _dummy_announcements(self, for_date: date) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "symbol": ["TCS"],
                "headline": ["Quarterly results released"],
                "sentiment": ["positive"],
                "date": [for_date.isoformat()],
            }
        )


__all__ = ["NSEScraper", "NSEScraperError"]
