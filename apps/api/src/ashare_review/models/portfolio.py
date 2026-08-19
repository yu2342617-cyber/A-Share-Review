"""positions 与 trades：持仓与交易记录结构（Phase 1 只建结构，不导入真实持仓）。

金额/价格一律 Decimal（ExactDecimal）；禁止 float 计算（DECISIONS.md D-010）。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ashare_review.db.base import Base
from ashare_review.db.timeutils import utc_now
from ashare_review.db.types import ExactDecimal, UTCDateTime


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("symbol", "market", name="uq_positions_symbol_market"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(ExactDecimal(18, 4), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(ExactDecimal(18, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="CNY")
    note: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Position {self.symbol} qty={self.quantity} cost={self.cost_price}>"


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        Index("ix_trades_symbol_trade_date", "symbol", "trade_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    side: Mapped[str] = mapped_column(String(4), nullable=False)  # buy / sell
    quantity: Mapped[Decimal] = mapped_column(ExactDecimal(18, 4), nullable=False)
    price: Mapped[Decimal] = mapped_column(ExactDecimal(18, 6), nullable=False)
    fee: Mapped[Decimal] = mapped_column(ExactDecimal(18, 6), nullable=False, default=Decimal("0"))
    amount: Mapped[Decimal] = mapped_column(ExactDecimal(18, 6), nullable=False)  # 成交金额
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="CNY")
    settlement_rule: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 结算规则（T+0/T+1 等）
    note: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Trade {self.symbol} {self.side} {self.quantity}@{self.price}>"
