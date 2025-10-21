"""Base classes for agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from dsp.utils.types import FeatureSummary, LearningOutcome, MarketDataBundle, StockPick


class Agent(ABC):
    """Base interface for all agents."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name


class DataIngestionAgent(Agent, ABC):
    """Interface for agents that ingest and normalize external data."""

    @abstractmethod
    async def ingest(self, for_date: date) -> MarketDataBundle:
        """Ingest all datasets required for the given trading date."""


class FeatureEngineeringAgent(Agent, ABC):
    """Interface for agents that compute technical features."""

    @abstractmethod
    async def compute(
        self, data: MarketDataBundle, for_date: date
    ) -> list[FeatureSummary]:
        """Compute features for all tradable instruments."""


class ResearchAgent(Agent, ABC):
    """Interface for agents that analyze textual/structured disclosures."""

    @abstractmethod
    async def enrich(
        self,
        features: list[FeatureSummary],
        data: MarketDataBundle,
        for_date: date,
    ) -> list[FeatureSummary]:
        """Return feature summaries augmented with research insights."""


class SelectionAgent(Agent, ABC):
    """Interface for agents that select the final pick."""

    @abstractmethod
    async def select(
        self, features: list[FeatureSummary], for_date: date
    ) -> StockPick:
        """Return the stock pick for the given date."""


class LearningAgent(Agent, ABC):
    """Interface for agents that learn from trading outcomes."""

    @abstractmethod
    async def learn(self, outcome: LearningOutcome) -> None:
        """Update models based on realized outcomes."""


class ReportingAgent(Agent, ABC):
    """Interface for agents that generate reports."""

    @abstractmethod
    async def report(
        self, pick: StockPick, features: list[FeatureSummary]
    ) -> None:
        """Persist or publish reports for the daily pick."""
