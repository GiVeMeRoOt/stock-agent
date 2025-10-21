"""Research agent that enriches feature summaries with textual insights."""

from __future__ import annotations

from datetime import date

from dsp.agents.base import ResearchAgent
from dsp.logging.setup import get_logger
from dsp.utils.types import FeatureSummary, MarketDataBundle

logger = get_logger(__name__)

_SENTIMENT_MAP = {
    "positive": 1.0,
    "neutral": 0.0,
    "negative": -1.0,
}


class DisclosureResearchAgent(ResearchAgent):
    """Transforms corporate disclosures into numerical features."""

    def __init__(self) -> None:
        super().__init__(name="research_agent")

    async def enrich(
        self,
        features: list[FeatureSummary],
        data: MarketDataBundle,
        for_date: date,
    ) -> list[FeatureSummary]:  # type: ignore[override]
        logger.info("Enriching features with research insights for %s", for_date)
        sentiment_by_symbol = {
            row["symbol"]: _SENTIMENT_MAP.get(
                str(row.get("sentiment", "")).lower(), 0.0
            )
            for _, row in data.announcements.iterrows()
        }
        for summary in features:
            if summary.symbol in sentiment_by_symbol:
                summary.features["sentiment"] = sentiment_by_symbol[summary.symbol]
                summary.notes.append(
                    f"sentiment_score:{sentiment_by_symbol[summary.symbol]:.2f}"
                )
        return features


__all__ = ["DisclosureResearchAgent"]
