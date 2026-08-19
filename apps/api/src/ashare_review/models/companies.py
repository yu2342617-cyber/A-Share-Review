"""companies 与 events：公司档案与事件（公告/新闻/政策/公司事件）。

事件保留来源与时间；event_time 必须为 aware 时间（D-011）。
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ashare_review.constants import EVENT_TYPES
from ashare_review.db.base import Base
from ashare_review.db.timeutils import utc_now
from ashare_review.db.types import UTCDateTime


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("symbol", "market", name="uq_companies_symbol_market"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    company_name: Mapped[str] = mapped_column(String(128), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(64), nullable=True)
    listing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, default=utc_now, onupdate=utc_now
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Company {self.symbol} {self.company_name}>"


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_symbol_time", "symbol", "event_time"),
        Index("ix_events_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    market: Mapped[str | None] = mapped_column(String(10), nullable=True)
    event_type: Mapped[str] = mapped_column(String(24), nullable=False, default="other")
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    event_time: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)
    fetched_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Event {self.event_type} {self.title[:30]}>"
