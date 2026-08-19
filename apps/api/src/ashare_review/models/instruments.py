"""instruments 与 instrument_trade_rules。

- instruments：证券档案（代码/市场/名称/类型/币种/最小变动单位/交易状态）。
- instrument_trade_rules：交易制度（T+0/T+1、最小交易单位、价格精度、市场规则）。
  ETF 规则必须按证券代码配置，不能统一假设（DECISIONS.md D-006）。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ashare_review.constants import SECURITY_TYPES, TRADE_CYCLES, TRADE_STATUSES
from ashare_review.db.base import Base
from ashare_review.db.timeutils import utc_now
from ashare_review.db.types import ExactDecimal, UTCDateTime


class Instrument(Base):
    __tablename__ = "instruments"
    __table_args__ = (
        UniqueConstraint("symbol", "market", name="uq_instruments_symbol_market"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    security_type: Mapped[str] = mapped_column(String(16), nullable=False, default="stock")
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="CNY")
    price_tick: Mapped[Decimal] = mapped_column(ExactDecimal(18, 6), nullable=False, default=Decimal("0.01"))
    trade_status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Instrument {self.symbol} {self.market} {self.name}>"


class InstrumentTradeRule(Base):
    """交易制度，按 (symbol, market) 唯一配置——ETF 与个股各自独立。"""

    __tablename__ = "instrument_trade_rules"
    __table_args__ = (
        UniqueConstraint("symbol", "market", name="uq_trade_rules_symbol_market"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    trade_cycle: Mapped[str] = mapped_column(String(4), nullable=False, default="T+1")
    min_trade_unit: Mapped[Decimal] = mapped_column(ExactDecimal(18, 4), nullable=False, default=Decimal("100"))
    price_precision: Mapped[int] = mapped_column(nullable=False, default=2)
    settlement_rule: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    note: Mapped[str | None] = mapped_column(String(128), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InstrumentTradeRule {self.symbol} {self.trade_cycle}>"
