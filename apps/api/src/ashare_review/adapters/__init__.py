"""adapters 包：数据源适配器（base 接口 / fake / akshare）。"""

from __future__ import annotations

from ashare_review.adapters.akshare import AKShareDataSourceAdapter, map_daily_rows
from ashare_review.adapters.base import (
    AdapterError,
    AdapterFieldError,
    AdapterMeta,
    DailyBar,
    DataSourceAdapter,
    DelayLevel,
    QuoteTick,
)
from ashare_review.adapters.fake import FakeDataSourceAdapter

__all__ = [
    "AdapterError",
    "AdapterFieldError",
    "AdapterMeta",
    "AKShareDataSourceAdapter",
    "DailyBar",
    "DataSourceAdapter",
    "DelayLevel",
    "FakeDataSourceAdapter",
    "QuoteTick",
    "map_daily_rows",
]
