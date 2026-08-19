"""source_fetch_runs：数据源抓取运行记录。"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ashare_review.constants import FETCH_STATUSES
from ashare_review.db.base import Base
from ashare_review.db.types import UTCDateTime


class SourceFetchRun(Base):
    __tablename__ = "source_fetch_runs"
    __table_args__ = (
        Index("ix_sfr_source_started", "source", "started_at"),
        Index("ix_sfr_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="running")
    records_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SourceFetchRun {self.source} {self.status} records={self.records_count}>"
