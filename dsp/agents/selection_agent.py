"""Selection agent responsible for ranking stocks and choosing the daily pick."""

from __future__ import annotations

from datetime import date

import numpy as np

from dsp.agents.base import SelectionAgent
from dsp.logging.setup import get_logger
from dsp.utils.types import FeatureSummary, StockPick

logger = get_logger(__name__)


class ScoringSelectionAgent(SelectionAgent):
    """Scores candidates using a weighted combination of engineered features."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        super().__init__(name="selection_agent")
        self.weights = weights or {
            "momentum": 0.35,
            "rsi": -0.15,
            "volatility": -0.1,
            "liquidity": 0.2,
            "sentiment": 0.15,
            "rolling_return": 0.25,
        }

    def update_weights(self, weights: dict[str, float]) -> None:
        """Update internal weights, e.g. after learning updates."""

        self.weights.update(weights)

    async def select(
        self, features: list[FeatureSummary], for_date: date
    ) -> StockPick:  # type: ignore[override]
        logger.info("Selecting daily pick for %s", for_date)
        if not features:
            raise ValueError("No features provided for selection")

        scores = []
        for summary in features:
            score = self._score_summary(summary)
            scores.append((score, summary))
            logger.debug("Scored %s -> %.4f", summary.symbol, score)
        best_score, best_summary = max(scores, key=lambda item: item[0])

        rationale_lines = [
            f"Momentum: {best_summary.features.get('momentum', np.nan):.3f}",
            f"Liquidity: {best_summary.features.get('liquidity', np.nan)/1e7:.2f}cr",
            f"RSI moderation: {best_summary.features.get('rsi', np.nan):.1f}",
        ]
        rationale_lines.extend(best_summary.notes)
        pick = StockPick(
            symbol=best_summary.symbol,
            pick_date=for_date,
            confidence=float(np.clip(best_score, 0, 1)),
            rationale="; ".join(rationale_lines),
            constraints=[
                "Uses EOD data only",
                "TODO: enforce universe & liquidity guardrails",
            ],
            features=best_summary.features,
        )
        logger.info("Selected %s with confidence %.2f", pick.symbol, pick.confidence)
        return pick

    def _score_summary(self, summary: FeatureSummary) -> float:
        score = 0.0
        for key, weight in self.weights.items():
            value = summary.features.get(key)
            if value is None or np.isnan(value):
                continue
            normalized = float(value)
            if key == "rsi":
                normalized = (50.0 - abs(50.0 - normalized)) / 50.0
            elif key == "liquidity":
                normalized = np.log1p(normalized) / 20.0
            elif key == "volatility":
                normalized = 1.0 - normalized
            score += weight * normalized
        return float(score)


__all__ = ["ScoringSelectionAgent"]
