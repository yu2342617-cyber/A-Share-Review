"""pytest 共享 fixtures（全部离线，使用内存 SQLite）。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ashare_review.db.timeutils import market_close_datetime, utc_now
from ashare_review.models import Base, MarketDataPoint

TRADE_DATE = date(2026, 8, 18)  # 周二


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine):
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    s = Session()
    yield s
    s.rollback()
    s.close()


@pytest.fixture()
def make_point():
    """构造合法的 MarketDataPoint（11 字段齐全），可覆盖任意字段。"""

    def _make(**overrides) -> MarketDataPoint:
        base = {
            "symbol": "600519.SH",
            "market": "SH",
            "trade_date": TRADE_DATE,
            "quote_time": market_close_datetime(TRADE_DATE),
            "fetched_at": utc_now(),
            "source": "akshare",
            "price_type": "close",
            "adjustment": "none",
            "is_delayed": False,
            "raw_value": "1435.50",
            "normalized_value": Decimal("1435.50"),
            "quality_status": "ok",
        }
        base.update(overrides)
        return MarketDataPoint(**base)

    return _make
