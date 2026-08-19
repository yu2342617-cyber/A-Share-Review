"""models 包：导入全部 ORM 模型，保证 Base.metadata 完整（供 Alembic 使用）。"""

from __future__ import annotations

from ashare_review.db.base import Base
from ashare_review.models.companies import Company, Event
from ashare_review.models.instruments import Instrument, InstrumentTradeRule
from ashare_review.models.market_data import MarketDataPoint
from ashare_review.models.portfolio import Position, Trade
from ashare_review.models.quality import DataQualityIssue
from ashare_review.models.source_runs import SourceFetchRun

__all__ = [
    "Base",
    "Company",
    "DataQualityIssue",
    "Event",
    "Instrument",
    "InstrumentTradeRule",
    "MarketDataPoint",
    "Position",
    "SourceFetchRun",
    "Trade",
]
