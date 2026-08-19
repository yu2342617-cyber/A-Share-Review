"""行情接口（Phase 2A：仅 Fake 数据源）。

- 数据来源固定为 FakeDataSourceAdapter（合成数据，仅离线确定性测试用）。
- 不访问 AKShare / 网络，不写数据库。
- 响应中的 source 字段恒为 "fake"，meta 明确标识；不得把 Fake 数据表述为真实行情。
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from ashare_review.adapters.base import AdapterMeta, DailyBar, QuoteTick
from ashare_review.adapters.fake import FakeDataSourceAdapter

router = APIRouter(prefix="/api/v1/market", tags=["market"])

MAX_DAILY_SPAN_DAYS = 366

_adapter = FakeDataSourceAdapter()


@router.get("/meta", response_model=AdapterMeta, summary="数据源元信息（fake）")
def market_meta() -> AdapterMeta:
    """返回 FakeDataSourceAdapter.meta()：id=fake，合成数据，不代表真实行情。"""
    return _adapter.meta()


@router.get("/quote", response_model=QuoteTick, summary="Fake 报价")
def market_quote(
    symbol: str = Query(..., min_length=1, description="证券代码，如 600519.SH"),
    market: str = Query(..., min_length=1, description="市场，如 SH"),
) -> QuoteTick:
    return _adapter.fetch_quote(symbol, market)


@router.get("/daily", response_model=list[DailyBar], summary="Fake 日线")
def market_daily(
    symbol: str = Query(..., min_length=1),
    market: str = Query(..., min_length=1),
    start_date: date = Query(..., description="起始交易日（含）"),
    end_date: date = Query(..., description="结束交易日（含）"),
) -> list[DailyBar]:
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date 不得晚于 end_date")
    if (end_date - start_date).days > MAX_DAILY_SPAN_DAYS:
        raise HTTPException(
            status_code=422, detail=f"日期区间最多 {MAX_DAILY_SPAN_DAYS} 天"
        )
    return _adapter.fetch_daily_history(symbol, market, start_date, end_date)
