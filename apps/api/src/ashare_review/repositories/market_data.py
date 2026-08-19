"""repositories：数据访问薄封装（Phase 1 最小集合）。"""

from __future__ import annotations

import json
from datetime import date
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ashare_review.adapters.base import DailyBar
from ashare_review.models.market_data import MarketDataPoint
from ashare_review.models.quality import DataQualityIssue
from ashare_review.quality.service import QualityIssue


class MarketDataRepository:
    """行情点读写。"""

    def __init__(self, session: Session):
        self.session = session

    def add_point(self, point: MarketDataPoint) -> MarketDataPoint:
        self.session.add(point)
        self.session.flush()
        return point

    def add_points(self, points: Iterable[MarketDataPoint]) -> int:
        points = list(points)
        if points:
            self.session.add_all(points)
            self.session.flush()
        return len(points)

    def get_point(
        self,
        symbol: str,
        market: str,
        trade_date: date,
        price_type: str,
        source: str,
        adjustment: str = "none",
    ) -> MarketDataPoint | None:
        stmt = (
            select(MarketDataPoint)
            .where(
                MarketDataPoint.symbol == symbol,
                MarketDataPoint.market == market,
                MarketDataPoint.trade_date == trade_date,
                MarketDataPoint.price_type == price_type,
                MarketDataPoint.source == source,
                MarketDataPoint.adjustment == adjustment,
            )
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def list_points(
        self,
        symbol: str | None = None,
        market: str | None = None,
        trade_date: date | None = None,
        price_type: str | None = None,
        source: str | None = None,
    ) -> list[MarketDataPoint]:
        stmt = select(MarketDataPoint)
        if symbol:
            stmt = stmt.where(MarketDataPoint.symbol == symbol)
        if market:
            stmt = stmt.where(MarketDataPoint.market == market)
        if trade_date:
            stmt = stmt.where(MarketDataPoint.trade_date == trade_date)
        if price_type:
            stmt = stmt.where(MarketDataPoint.price_type == price_type)
        if source:
            stmt = stmt.where(MarketDataPoint.source == source)
        return list(self.session.scalars(stmt))

    def store_daily_bars(self, bars: Sequence[DailyBar]) -> int:
        """把 DailyBar 展开为行情点（open/high/low/close/volume/amount）。

        每个点：raw_value = 原始标量字符串；normalized_value = Decimal。
        """
        points: list[MarketDataPoint] = []
        for bar in bars:
            fields = (
                ("open", bar.open),
                ("high", bar.high),
                ("low", bar.low),
                ("close", bar.close),
                ("volume", bar.volume),
                ("amount", bar.amount),
            )
            for price_type, value in fields:
                if value is None:
                    continue
                points.append(
                    MarketDataPoint(
                        symbol=bar.symbol,
                        market=bar.market,
                        trade_date=bar.trade_date,
                        quote_time=bar.quote_time,
                        fetched_at=bar.fetched_at,
                        source=bar.source,
                        price_type=price_type,
                        adjustment=bar.adjustment,
                        is_delayed=bar.is_delayed,
                        raw_value=str(value),
                        normalized_value=value,
                        quality_status="ok",
                    )
                )
        return self.add_points(points)


class QualityRepository:
    """质量问题持久化。"""

    def __init__(self, session: Session):
        self.session = session

    def add_issue(self, issue: QualityIssue) -> DataQualityIssue:
        row = DataQualityIssue(
            issue_type=issue.issue_type,
            severity=issue.severity,
            source=issue.source,
            symbol=issue.symbol,
            market=issue.market,
            trade_date=issue.trade_date,
            evidence=issue.evidence,
            status="open",
        )
        self.session.add(row)
        self.session.flush()
        return row

    def add_issues(self, issues: Iterable[QualityIssue]) -> int:
        rows = [self.add_issue(i) for i in issues]
        return len(rows)

    def list_issues(self, issue_type: str | None = None, status: str | None = None) -> list[DataQualityIssue]:
        stmt = select(DataQualityIssue).order_by(DataQualityIssue.created_at.desc())
        if issue_type:
            stmt = stmt.where(DataQualityIssue.issue_type == issue_type)
        if status:
            stmt = stmt.where(DataQualityIssue.status == status)
        return list(self.session.scalars(stmt))
