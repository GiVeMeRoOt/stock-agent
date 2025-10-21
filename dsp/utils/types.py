"""Common data models used across agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pandas as pd


@dataclass(slots=True)
class MarketDataBundle:
    """Container for all datasets produced by the ingestion agent."""

    bhavcopy: pd.DataFrame
    indices: pd.DataFrame
    corporate_actions: pd.DataFrame
    deals: pd.DataFrame
    announcements: pd.DataFrame


@dataclass(slots=True)
class FeatureSummary:
    """Summary of engineered features for a stock symbol."""

    symbol: str
    features: dict[str, float]
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StockPick:
    """Representation of a single stock pick recommendation."""

    symbol: str
    pick_date: date
    confidence: float
    rationale: str
    constraints: list[str]
    features: dict[str, float]
    disclaimer: str = "Not investment advice"


@dataclass(slots=True)
class LearningOutcome:
    """Outcome of a prior selection used for learning."""

    symbol: str
    pick_date: date
    open_price: float
    close_price: float
    pnl: float
    metadata: dict[str, Any] = field(default_factory=dict)
