"""AKShare 联网 smoke 测试（可选，默认排除：pytest -m smoke）。

普通测试（pytest）默认不联网、不执行本文件；
显式运行：.venv\\Scripts\\python -m pytest apps/api -m smoke
网络失败不得导致普通测试失败（本文件默认被 addopts 排除）。
"""

from __future__ import annotations

from datetime import date

import pytest

pytestmark = pytest.mark.smoke


@pytest.fixture(scope="module")
def akshare_adapter():
    pytest.importorskip("akshare", reason="未安装 akshare，跳过 smoke 测试")
    from ashare_review.adapters.akshare import AKShareDataSourceAdapter

    return AKShareDataSourceAdapter()


def test_akshare_stock_daily_smoke(akshare_adapter):
    bars = akshare_adapter.fetch_daily_history("600519.SH", "SH", date(2024, 1, 2), date(2024, 1, 10))
    assert bars, "未取到贵州茅台日线（网络/上游问题）"
    assert all(b.close > 0 for b in bars)


def test_akshare_etf_daily_smoke(akshare_adapter):
    bars = akshare_adapter.fetch_daily_history("510300.SH", "SH", date(2024, 1, 2), date(2024, 1, 10))
    assert bars, "未取到沪深300ETF日线（网络/上游问题）"


def test_akshare_quote_smoke(akshare_adapter):
    tick = akshare_adapter.fetch_quote("600519.SH", "SH")
    assert tick.price > 0
    assert tick.price_type == "close"
