"""Orchestrator agent that coordinates the full workflow."""

from __future__ import annotations

from datetime import date

from dsp.agents.data_ingestion_agent import NSEDataIngestionAgent
from dsp.agents.feature_engineering_agent import TechnicalFeatureEngineeringAgent
from dsp.agents.learning_agent import BanditLearningAgent
from dsp.agents.reporting_agent import MarkdownReportingAgent
from dsp.agents.research_agent import DisclosureResearchAgent
from dsp.agents.selection_agent import ScoringSelectionAgent
from dsp.logging.setup import get_logger
from dsp.storage.repository import init_db, upsert_pick
from dsp.utils.types import LearningOutcome, StockPick

logger = get_logger(__name__)


class OrchestratorAgent:
    """Coordinates all sub-agents to produce the daily stock pick."""

    def __init__(self) -> None:
        self.data_agent = NSEDataIngestionAgent()
        self.feature_agent = TechnicalFeatureEngineeringAgent()
        self.research_agent = DisclosureResearchAgent()
        self.learning_agent = BanditLearningAgent()
        self.selection_agent = ScoringSelectionAgent(
            weights=self.learning_agent.weights
        )
        self.reporting_agent = MarkdownReportingAgent()
        self._initialized = False
        # TODO: add caching layer for reusing ingested datasets across calls.

    async def initialize(self) -> None:
        if not self._initialized:
            await init_db()
            self._initialized = True
            logger.info("Orchestrator initialized")

    async def run_daily_pick(self, for_date: date) -> StockPick:
        await self.initialize()
        data = await self.data_agent.ingest(for_date)
        features = await self.feature_agent.compute(data, for_date)
        enriched = await self.research_agent.enrich(features, data, for_date)
        self.selection_agent.update_weights(self.learning_agent.weights)
        pick = await self.selection_agent.select(enriched, for_date)
        await upsert_pick(pick)
        await self.reporting_agent.report(pick, enriched)
        return pick

    async def learn_from_outcome(self, outcome: LearningOutcome) -> None:
        await self.initialize()
        await self.learning_agent.learn(outcome)


__all__ = ["OrchestratorAgent"]
