"""统一数据源适配器接口（DECISIONS.md D-003 / D-014）。

- 所有适配器输出必须经过 Pydantic 模型校验（QuoteTick / DailyBar）。
- 不允许 naive datetime（D-011）：quote_time / fetched_at 必须带时区。
- 上游字段缺失或变化必须抛 AdapterFieldError，禁止静默容忍。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DelayLevel(str, Enum):
    REALTIME = "realtime"
    DELAYED = "delayed"
    END_OF_DAY = "end_of_day"
    UNKNOWN = "unknown"


class AdapterError(Exception):
    """适配器通用错误。"""


class AdapterFieldError(AdapterError):
    """上游字段缺失或变化。"""

    def __init__(self, message: str, missing: list[str] | None = None, unexpected: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.missing = missing or []
        self.unexpected = unexpected or []


class AdapterMeta(BaseModel):
    """适配器元信息：延迟级别、支持范围、限制说明。"""

    id: str
    name: str
    delay: DelayLevel
    supports: list[str] = Field(default_factory=list)
    limitations: str = ""


class _AwareModel(BaseModel):
    """带 aware-datetime 校验的基类。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("quote_time", "fetched_at", "event_time", check_fields=False)
    @classmethod
    def _require_aware(cls, v: datetime) -> datetime:
        if v is None or v.tzinfo is None:
            raise ValueError("datetime 必须带时区（禁止 naive 时间，见 DECISIONS.md D-011）")
        return v


class QuoteTick(_AwareModel):
    """单点报价（实时/收盘）。"""

    symbol: str
    market: str
    quote_time: datetime
    fetched_at: datetime
    source: str
    price: Decimal
    price_type: str = "last"
    adjustment: str = "none"
    is_delayed: bool = False
    raw_value: Any = None


class DailyBar(_AwareModel):
    """标准化日线（原始值与标准化值同存）。"""

    symbol: str
    market: str
    trade_date: date
    quote_time: datetime
    fetched_at: datetime
    source: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None
    amount: Decimal | None = None
    adjustment: str = "none"
    is_delayed: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class DataSourceAdapter(ABC):
    """统一适配器接口。"""

    id: str

    @abstractmethod
    def meta(self) -> AdapterMeta:
        """返回延迟级别、支持范围、限制说明。"""

    @abstractmethod
    def fetch_quote(self, symbol: str, market: str) -> QuoteTick:
        """获取最新报价。"""

    @abstractmethod
    def fetch_daily_history(
        self, symbol: str, market: str, start_date: date, end_date: date
    ) -> list[DailyBar]:
        """获取日线历史（含原始值）。"""
