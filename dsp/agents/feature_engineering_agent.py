"""Feature engineering agent implementation."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from dsp.agents.base import FeatureEngineeringAgent
from dsp.logging.setup import get_logger
from dsp.utils.types import FeatureSummary, MarketDataBundle

logger = get_logger(__name__)


class TechnicalFeatureEngineeringAgent(FeatureEngineeringAgent):
    """Computes technical and event-driven features from ingested data."""

    def __init__(self, rsi_period: int = 14, momentum_period: int = 5) -> None:
        super().__init__(name="feature_engineering_agent")
        self.rsi_period = rsi_period
        self.momentum_period = momentum_period

    async def compute(
        self, data: MarketDataBundle, for_date: date
    ) -> list[FeatureSummary]:  # type: ignore[override]
        logger.info("Computing features for %s", for_date)
        bhav = data.bhavcopy.copy()
        bhav["rsi"] = self._compute_single_day_rsi(bhav)
        bhav["atr"] = bhav["high"] - bhav["low"]
        bhav["momentum"] = bhav["close"] / bhav["prev_close"] - 1.0
        bhav["rolling_return"] = bhav["momentum"]
        bhav["liquidity"] = bhav["tot_trd_val"]
        bhav["volatility"] = (bhav["high"] - bhav["low"]) / bhav["close"]

        event_flags = self._build_event_flags(data)
        summaries: list[FeatureSummary] = []
        for _, row in bhav.iterrows():
            symbol = row["symbol"]
            features = {
                "rsi": float(row.get("rsi", np.nan)),
                "atr": float(row.get("atr", np.nan)),
                "momentum": float(row.get("momentum", np.nan)),
                "rolling_return": float(row.get("rolling_return", np.nan)),
                "liquidity": float(row.get("liquidity", np.nan)),
                "volatility": float(row.get("volatility", np.nan)),
            }
            notes = event_flags.get(symbol, [])
            summaries.append(
                FeatureSummary(symbol=symbol, features=features, notes=notes)
            )
        logger.info("Computed %d feature summaries", len(summaries))
        return summaries

    def _compute_single_day_rsi(self, df: pd.DataFrame) -> pd.Series:
        change = df["close"] - df["prev_close"]
        gain = change.clip(lower=0)
        loss = (-change.clip(upper=0)).replace(0, np.nan)
        rs = gain / loss
        rsi = 100 - 100 / (1 + rs)
        return rsi.fillna(50.0)

    def _build_event_flags(self, data: MarketDataBundle) -> dict[str, list[str]]:
        flags: dict[str, list[str]] = {}
        for _, row in data.corporate_actions.iterrows():
            flags.setdefault(row["symbol"], []).append(
                f"corporate_action:{row.get('action', '')}"
            )
        for _, row in data.deals.iterrows():
            flags.setdefault(row["symbol"], []).append(
                f"deal:{row.get('type', '')}"
            )
        for _, row in data.announcements.iterrows():
            sentiment = row.get("sentiment", "neutral")
            flags.setdefault(row["symbol"], []).append(f"announcement:{sentiment}")
        return flags


__all__ = ["TechnicalFeatureEngineeringAgent"]
