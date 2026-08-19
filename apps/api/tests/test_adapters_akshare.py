"""AKShare 适配器测试：全部离线，使用本地 fixture（不联网、不依赖 akshare）。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ashare_review.adapters.akshare import (
    AKShareDataSourceAdapter,
    _is_etf_symbol,
    map_daily_rows,
)
from ashare_review.adapters.base import AdapterError, AdapterFieldError, DelayLevel

FIXTURE_ROWS = [
    {
        "日期": "2026-08-17",
        "开盘": "10.01",
        "收盘": "10.05",
        "最高": "10.10",
        "最低": "9.98",
        "成交量": "120000",
        "成交额": "120600000.00",
        "振幅": "1.20%",
        "涨跌幅": "0.50%",
        "涨跌额": "0.05",
        "换手率": "0.35%",
    },
    {
        "日期": "2026-08-18",
        "开盘": "10.06",
        "收盘": "10.12",
        "最高": "10.15",
        "最低": "10.02",
        "成交量": "135000",
        "成交额": "136620000.00",
        "振幅": "1.29%",
        "涨跌幅": "0.70%",
        "涨跌额": "0.07",
        "换手率": "0.39%",
    },
]


def test_map_daily_rows_normal():
    bars = map_daily_rows(FIXTURE_ROWS, "600519.SH", "SH", "akshare")
    assert len(bars) == 2
    b = bars[0]
    assert b.symbol == "600519.SH"
    assert b.market == "SH"
    assert b.trade_date == date(2026, 8, 17)
    assert b.open == Decimal("10.010000")
    assert b.close == Decimal("10.050000")
    assert b.high == Decimal("10.100000")
    assert b.low == Decimal("9.980000")
    assert b.volume == Decimal("120000")
    assert b.amount == Decimal("120600000.00")
    assert b.source == "akshare"
    assert b.adjustment == "none"
    assert b.is_delayed is False
    assert b.quote_time.tzinfo is not None  # aware（D-011）
    # 原始值保留
    assert b.raw["涨跌幅"] == "0.50%"


def test_map_daily_rows_missing_column_raises():
    rows = [{k: v for k, v in FIXTURE_ROWS[0].items() if k != "开盘"}]
    with pytest.raises(AdapterFieldError) as ei:
        map_daily_rows(rows, "600519.SH", "SH", "akshare")
    assert "开盘" in ei.value.missing


def test_map_daily_rows_renamed_column_raises():
    """上游改名（如 开盘 → Open）等价于旧列缺失，必须报错。"""
    rows = [dict(FIXTURE_ROWS[0])]
    rows[0]["Open"] = rows[0].pop("开盘")
    with pytest.raises(AdapterFieldError):
        map_daily_rows(rows, "600519.SH", "SH", "akshare")


def test_map_daily_rows_bad_date_raises():
    rows = [dict(FIXTURE_ROWS[0], 日期="2026/08/17")]  # 格式不符
    with pytest.raises(AdapterFieldError):
        map_daily_rows(rows, "600519.SH", "SH", "akshare")


def test_map_daily_rows_empty():
    assert map_daily_rows([], "600519.SH", "SH", "akshare") == []


@pytest.mark.parametrize(
    ("symbol", "market", "expected"),
    [
        ("510300.SH", "SH", True),
        ("512100.SH", "SH", True),
        ("600519.SH", "SH", False),
        ("159915.SZ", "SZ", True),
        ("000001.SZ", "SZ", False),
        ("00700.HK", "HK", False),
    ],
)
def test_is_etf_symbol(symbol, market, expected):
    assert _is_etf_symbol(symbol, market) is expected


def test_akshare_meta():
    meta = AKShareDataSourceAdapter().meta()
    assert meta.id == "akshare"
    assert meta.delay == DelayLevel.END_OF_DAY
    assert "stock" in meta.supports and "etf" in meta.supports


def test_akshare_unsupported_market_raises_without_network():
    """HK 等市场在联网前即报错（Phase 1 最小实现仅 A股），无需网络/akshare。"""
    adapter = AKShareDataSourceAdapter()
    with pytest.raises(AdapterError):
        adapter.fetch_daily_history("00700.HK", "HK", date(2026, 1, 1), date(2026, 1, 10))


def test_akshare_lazy_import_behavior():
    """akshare 未安装时必须给出明确错误（不静默）。"""
    import importlib.util

    adapter = AKShareDataSourceAdapter()
    if importlib.util.find_spec("akshare") is None:
        with pytest.raises(AdapterError):
            adapter._ak()
    else:
        assert adapter._ak() is not None
