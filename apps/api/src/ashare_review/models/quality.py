"""data_quality_issues：数据质量问题记录。"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ashare_review.constants import ISSUE_STATUSES, ISSUE_TYPES, SEVERITIES
from ashare_review.db.base import Base
from ashare_review.db.timeutils import utc_now
from ashare_review.db.types import UTCDateTime


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"
    __table_args__ = (
        Index("ix_dqi_type", "issue_type"),
        Index("ix_dqi_status", "status"),
        Index("ix_dqi_symbol_trade_date", "symbol", "trade_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    issue_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(12), nullable=False, default="warning")
    source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    market: Mapped[str | None] = mapped_column(String(10), nullable=True)
    trade_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    evidence: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DataQualityIssue {self.issue_type} {self.severity} {self.status}>"
