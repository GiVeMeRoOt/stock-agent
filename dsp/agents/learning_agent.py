"""Learning agent that updates selection weights based on outcomes."""

from __future__ import annotations

import json

import numpy as np

from dsp.agents.base import LearningAgent
from dsp.config.settings import settings
from dsp.logging.setup import get_logger
from dsp.storage.repository import record_learning_outcome
from dsp.utils.types import LearningOutcome

logger = get_logger(__name__)


class BanditLearningAgent(LearningAgent):
    """Applies a simple bandit-style update to feature weights."""

    def __init__(self, learning_rate: float = 0.1) -> None:
        super().__init__(name="learning_agent")
        self.learning_rate = learning_rate
        self._model_dir = settings.data_dir / "models"
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._weights_file = self._model_dir / "selection_weights.json"
        self._weights = self._load_weights()

    async def learn(self, outcome: LearningOutcome) -> None:  # type: ignore[override]
        logger.info("Learning from outcome for %s", outcome.pick_date)
        reward = np.tanh(outcome.pnl / max(abs(outcome.open_price), 1e-3))
        logger.debug("Calculated reward %.4f for symbol %s", reward, outcome.symbol)
        for feature_name in list(self._weights.keys()):
            self._weights[feature_name] += self.learning_rate * reward
        self._persist_weights()
        await record_learning_outcome(outcome)

    def _load_weights(self) -> dict[str, float]:
        if self._weights_file.exists():
            try:
                return json.loads(self._weights_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:  # noqa: BLE001
                logger.warning("Failed to parse weights file: %s", exc)
        logger.info("Initializing default weights")
        return {
            "momentum": 0.35,
            "rsi": -0.15,
            "volatility": -0.1,
            "liquidity": 0.2,
            "sentiment": 0.15,
            "rolling_return": 0.25,
        }

    def _persist_weights(self) -> None:
        self._weights_file.write_text(
            json.dumps(self._weights, indent=2), encoding="utf-8"
        )

    @property
    def weights(self) -> dict[str, float]:
        return self._weights


__all__ = ["BanditLearningAgent"]
