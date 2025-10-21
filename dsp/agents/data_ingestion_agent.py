"""Implementation of the data ingestion agent."""

from __future__ import annotations

from datetime import date

import pandas as pd

from dsp.agents.base import DataIngestionAgent
from dsp.config.settings import settings
from dsp.logging.setup import get_logger
from dsp.scrapers.nse.client import NSEScraper
from dsp.utils.types import MarketDataBundle

logger = get_logger(__name__)


class NSEDataIngestionAgent(DataIngestionAgent):
    """Ingests public NSE datasets via the scraper."""

    def __init__(self) -> None:
        super().__init__(name="data_ingestion_agent")
        self._output_dir = settings.data_dir / "raw"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    async def ingest(self, for_date: date) -> MarketDataBundle:  # type: ignore[override]
        logger.info("Starting data ingestion for %s", for_date)
        async with NSEScraper() as scraper:
            (
                bhavcopy,
                indices,
                corp_actions,
                deals,
                announcements,
            ) = await _gather_datasets(scraper, for_date)
        self._persist_dataset("bhavcopy", for_date, bhavcopy)
        self._persist_dataset("indices", for_date, indices)
        self._persist_dataset("corporate_actions", for_date, corp_actions)
        self._persist_dataset("deals", for_date, deals)
        self._persist_dataset("announcements", for_date, announcements)

        logger.info("Completed ingestion for %s", for_date)
        return MarketDataBundle(
            bhavcopy=bhavcopy,
            indices=indices,
            corporate_actions=corp_actions,
            deals=deals,
            announcements=announcements,
        )

    def _persist_dataset(self, name: str, for_date: date, df: pd.DataFrame) -> None:
        file_path = self._output_dir / f"{for_date.isoformat()}_{name}.csv"
        try:
            df.to_csv(file_path, index=False)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist %s to %s: %s", name, file_path, exc)


async def _gather_datasets(
    scraper: NSEScraper, for_date: date
) -> tuple[pd.DataFrame, ...]:
    bhavcopy = await scraper.fetch_bhavcopy(for_date)
    indices = await scraper.fetch_indices(for_date)
    corporate_actions = await scraper.fetch_corporate_actions(for_date)
    deals = await scraper.fetch_deals(for_date)
    announcements = await scraper.fetch_announcements(for_date)
    return bhavcopy, indices, corporate_actions, deals, announcements


__all__ = ["NSEDataIngestionAgent"]
