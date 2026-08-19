"""repositories 测试：正常写入、重复约束、查询过滤。"""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from ashare_review.adapters.base import DailyBar
from ashare_review.db.timeutils import market_close_datetime, utc_now
from ashare_review.models import MarketDataPoint
from ashare_review.repositories import MarketDataRepository


def _bar(symbol: str = "510300.SH", market: str = "SH", day: int = 18) -> DailyBar:
    from datetime import date

    d = date(2026, 8, day)
    return DailyBar(
        symbol=symbol,
        market=market,
        trade_date=d,
        quote_time=market_close_datetime(d),
        fetched_at=utc_now(),
        source="fake",
        open=Decimal("4.01"),
        high=Decimal("4.10"),
        low=Decimal("3.98"),
        close=Decimal("4.05"),
        volume=Decimal("1200000"),
        amount=Decimal("4860000"),
        adjustment="none",
        is_delayed=False,
        raw={"日期": "2026-08-18", "收盘": "4.05"},
    )


def test_store_daily_bars_expands_to_points(session):
    repo = MarketDataRepository(session)
    n = repo.store_daily_bars([_bar(day=18), _bar(day=19)])
    assert n == 12  # 2 天 × 6 个 price_type

    points = repo.list_points(symbol="510300.SH")
    assert len(points) == 12
    types = {p.price_type for p in points}
    assert types == {"open", "high", "low", "close", "volume", "amount"}
    close = repo.get_point("510300.SH", "SH", __import__("datetime").date(2026, 8, 18), "close", "fake")
    assert close is not None
    assert close.normalized_value == Decimal("4.050000")
    assert close.raw_value == "4.05"


def test_duplicate_point_raises_integrity_error(session, make_point):
    repo = MarketDataRepository(session)
    repo.add_point(make_point())
    with pytest.raises(IntegrityError):
        repo.add_point(make_point())


def test_list_points_filters(session, make_point):
    repo = MarketDataRepository(session)
    repo.add_points(
        [
            make_point(price_type="close", normalized_value=Decimal("10.00")),
            make_point(price_type="open", normalized_value=Decimal("9.95")),
            make_point(symbol="000001.SZ", market="SZ", price_type="close"),
        ]
    )
    closes = repo.list_points(price_type="close")
    assert len(closes) == 2
    sh_only = repo.list_points(market="SH", price_type="close")
    assert len(sh_only) == 1
