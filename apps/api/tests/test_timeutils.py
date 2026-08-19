"""时间处理测试（DECISIONS.md D-011）：UTC 存储、Asia/Shanghai 展示、naive 拦截。"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from ashare_review.adapters.base import QuoteTick
from ashare_review.db.timeutils import (
    as_shanghai,
    ensure_aware,
    market_close_datetime,
    market_date_of,
    to_utc,
)


def test_to_utc_and_as_shanghai_roundtrip():
    sh = datetime(2026, 8, 18, 15, 0, tzinfo=timezone.utc)  # 15:00 UTC = 23:00 北京时间
    assert as_shanghai(sh).hour == 23
    back = to_utc(as_shanghai(sh))
    assert back == sh
    assert back.tzinfo is not None


def test_ensure_aware_treats_naive_as_shanghai():
    naive = datetime(2026, 8, 18, 9, 30)
    aware = ensure_aware(naive)
    assert aware.tzinfo is not None
    assert aware.utcoffset().total_seconds() == 8 * 3600  # Asia/Shanghai UTC+8


def test_market_date_of():
    # UTC 2026-08-17 20:00 = 北京 2026-08-18 04:00 → 市场日 18 日
    utc_dt = datetime(2026, 8, 17, 20, 0, tzinfo=timezone.utc)
    assert market_date_of(utc_dt) == date(2026, 8, 18)


def test_market_close_datetime_is_aware_15_00():
    dt = market_close_datetime(date(2026, 8, 18))
    assert dt.tzinfo is not None
    assert as_shanghai(dt).hour == 15


def test_pydantic_rejects_naive_datetime():
    with pytest.raises(ValidationError):
        QuoteTick(
            symbol="600519.SH",
            market="SH",
            quote_time=datetime(2026, 8, 18, 15, 0),  # naive → 必须拒绝
            fetched_at=datetime(2026, 8, 18, 15, 0),  # naive
            source="fake",
            price="10.00",
        )


def test_pydantic_accepts_aware_datetime():
    t = QuoteTick(
        symbol="600519.SH",
        market="SH",
        quote_time=datetime(2026, 8, 18, 15, 0, tzinfo=timezone.utc),
        fetched_at=datetime(2026, 8, 18, 15, 0, tzinfo=timezone.utc),
        source="fake",
        price="10.00",
    )
    assert t.price == 10  # Decimal 转换
