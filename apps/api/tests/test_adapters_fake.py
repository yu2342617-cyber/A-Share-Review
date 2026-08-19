"""Fake 适配器测试：完全离线、确定性。"""

from __future__ import annotations

from datetime import date

import pytest

from ashare_review.adapters.base import DailyBar, DelayLevel, QuoteTick
from ashare_review.adapters.fake import FakeDataSourceAdapter


def test_fake_meta():
    meta = FakeDataSourceAdapter().meta()
    assert meta.id == "fake"
    assert meta.delay == DelayLevel.END_OF_DAY


def test_fake_quote_deterministic_offline():
    adapter = FakeDataSourceAdapter()
    q1 = adapter.fetch_quote("600519.SH", "SH")
    q2 = adapter.fetch_quote("600519.SH", "SH")
    assert isinstance(q1, QuoteTick)
    assert q1.price == q2.price
    assert q1.quote_time.tzinfo is not None
    assert q1.source == "fake"
    # 不同代码应产生不同价格（确定性散列）
    q3 = adapter.fetch_quote("000001.SZ", "SZ")
    assert q3.price != q1.price


def test_fake_daily_history_offline_deterministic():
    adapter = FakeDataSourceAdapter()
    start, end = date(2026, 8, 17), date(2026, 8, 21)  # 周一到周五
    bars1 = adapter.fetch_daily_history("510300.SH", "SH", start, end)
    bars2 = adapter.fetch_daily_history("510300.SH", "SH", start, end)
    assert len(bars1) == 5  # 5 个工作日
    assert all(isinstance(b, DailyBar) for b in bars1)
    assert [(b.trade_date, b.close) for b in bars1] == [(b.trade_date, b.close) for b in bars2]
    # 周末应跳过
    weekend_span = adapter.fetch_daily_history("510300.SH", "SH", date(2026, 8, 15), date(2026, 8, 16))
    assert weekend_span == []


def test_fake_daily_history_invalid_range():
    adapter = FakeDataSourceAdapter()
    with pytest.raises(ValueError):
        adapter.fetch_daily_history("510300.SH", "SH", date(2026, 8, 21), date(2026, 8, 17))
