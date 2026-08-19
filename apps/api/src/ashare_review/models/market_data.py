"""market_data_points：统一行情点模型（11 字段 + 质量状态）。"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ashare_review.constants import ADJUSTMENTS, PRICE_TYPES, QUALITY_STATUS
from ashare_review.db.base import Base
from ashare_review.db.types import ExactDecimal, UTCDateTime


class MarketDataPoint(Base):
    """每条行情记录必须包含全部 11 个字段（AGENTS.md 铁律 2）。"""

    __tablename__ = "market_data_points"
    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "market",
            "trade_date",
            "quote_time",
            "source",
            "price_type",
            "adjustment",
            "is_delayed",
            name="uq_mdp_dedup",
        ),
        Index("ix_mdp_symbol_trade_date", "symbol", "market", "trade_date"),
        Index("ix_mdp_trade_date_type", "trade_date", "price_type"),
        Index("ix_mdp_source_fetched", "source", "fetched_at"),
        Index("ix_mdp_quality", "quality_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # --- 11 字段（铁律） ---
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    quote_time: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    price_type: Mapped[str] = mapped_column(String(16), nullable=False)
    adjustment: Mapped[str] = mapped_column(String(8), nullable=False, default="none")
    is_delayed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[Decimal | None] = mapped_column(ExactDecimal(18, 6), nullable=True)
    # --- 质量状态 ---
    quality_status: Mapped[str] = mapped_column(String(12), nullable=False, default="ok")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<MarketDataPoint {self.symbol} {self.trade_date} "
            f"{self.price_type} {self.normalized_value} src={self.source}>"
        )
