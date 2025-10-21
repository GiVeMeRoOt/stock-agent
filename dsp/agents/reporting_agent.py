"""Reporting agent that emits Markdown and CSV summaries."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from dsp.agents.base import ReportingAgent
from dsp.config.settings import settings
from dsp.logging.setup import get_logger
from dsp.utils.types import FeatureSummary, StockPick

logger = get_logger(__name__)


class MarkdownReportingAgent(ReportingAgent):
    """Persist reports for the daily pick in Markdown and CSV formats."""

    def __init__(self) -> None:
        super().__init__(name="reporting_agent")
        self._reports_dir = settings.data_dir / "reports"
        self._reports_dir.mkdir(parents=True, exist_ok=True)

    async def report(
        self, pick: StockPick, features: list[FeatureSummary]
    ) -> None:  # type: ignore[override]
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        md_path = self._reports_dir / f"{pick.pick_date.isoformat()}_{timestamp}.md"
        csv_path = self._reports_dir / f"{pick.pick_date.isoformat()}_{timestamp}.csv"
        logger.info("Writing reports to %s and %s", md_path, csv_path)

        md_content = self._render_markdown(pick)
        md_path.write_text(md_content, encoding="utf-8")

        df = pd.DataFrame(
            [
                {
                    "symbol": summary.symbol,
                    **summary.features,
                    "notes": "|".join(summary.notes),
                }
                for summary in features
            ]
        )
        df.to_csv(csv_path, index=False)

    def _render_markdown(self, pick: StockPick) -> str:
        lines = [
            f"# Daily Stock Pick - {pick.pick_date.isoformat()}",
            "",
            f"**Symbol:** {pick.symbol}",
            f"**Confidence:** {pick.confidence:.2f}",
            "",
            "## Rationale",
            pick.rationale,
            "",
            "## Constraints",
            "".join(f"- {item}\n" for item in pick.constraints),
            "",
            "## Features",
        ]
        for key, value in pick.features.items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")
        lines.append(pick.disclaimer)
        return "\n".join(lines)


__all__ = ["MarkdownReportingAgent"]
