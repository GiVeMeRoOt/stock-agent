"""CLI entry point to fetch today's stock pick."""

from __future__ import annotations

import argparse
import asyncio
from datetime import date, datetime

from dsp.agents.orchestrator_agent import OrchestratorAgent
from dsp.utils.dates import current_market_date


async def _run(for_date: date) -> str:
    orchestrator = OrchestratorAgent()
    pick = await orchestrator.run_daily_pick(for_date)
    feature_lines = "\n".join(
        f"- **{key}**: {value}" for key, value in pick.features.items()
    )
    markdown = (
        f"# Daily Stock Pick\n\n"
        f"**Date:** {pick.pick_date.isoformat()}\n"
        f"**Symbol:** {pick.symbol}\n"
        f"**Confidence:** {pick.confidence:.2f}\n\n"
        f"## Rationale\n{pick.rationale}\n\n"
        f"## Constraints\n" + "".join(f"- {c}\n" for c in pick.constraints) + "\n"
        f"## Features\n{feature_lines}\n\n"
        f"{pick.disclaimer}\n"
    )
    return markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily Stock Picker")
    parser.add_argument(
        "--date",
        type=str,
        help=(
            "Date to run the pick for (YYYY-MM-DD). Defaults to today in the "
            "configured timezone."
        ),
    )
    args = parser.parse_args()
    if args.date:
        for_date = datetime.fromisoformat(args.date).date()
    else:
        for_date = current_market_date()
    markdown = asyncio.run(_run(for_date))
    print(markdown)


if __name__ == "__main__":
    main()
