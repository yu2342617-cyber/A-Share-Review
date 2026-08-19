"""时间处理统一方案（DECISIONS.md D-011）。

- 数据库存储 UTC（timezone-aware）。
- trade_date 为对应市场本地交易日（date，无时区歧义）。
- 展示统一按 Asia/Shanghai。
- 禁止 naive datetime 进入数据库（适配器层由 Pydantic 校验拦截）。
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from ashare_review.config import DEFAULT_TIMEZONE

UTC = timezone.utc


def zone(tz_name: str | None = None) -> ZoneInfo:
    return ZoneInfo(tz_name or DEFAULT_TIMEZONE)


def ensure_aware(dt: datetime, tz_name: str | None = None) -> datetime:
    """naive 时间视为 tz_name（默认 Asia/Shanghai）并补时区；aware 原样返回。"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=zone(tz_name))
    return dt


def to_utc(dt: datetime) -> datetime:
    """任意 aware 时间转 UTC。naive 输入先按 Asia/Shanghai 补时区。"""
    return ensure_aware(dt).astimezone(UTC)


def as_shanghai(dt: datetime) -> datetime:
    """任意 aware 时间转 Asia/Shanghai。"""
    return ensure_aware(dt).astimezone(zone())


def market_date_of(dt: datetime) -> date:
    """时间在其市场时区（默认 Asia/Shanghai）下的日期，用作 trade_date。"""
    return as_shanghai(dt).date()


def utc_now() -> datetime:
    return datetime.now(UTC)


def shanghai_now() -> datetime:
    return datetime.now(zone())


def market_close_datetime(trade_date: date, tz_name: str | None = None) -> datetime:
    """A股/ETF 默认收盘时刻 15:00（Asia/Shanghai），返回 aware 时间。

    港股等市场的收盘时刻在后续 Phase 按市场配置扩展。
    """
    return datetime.combine(trade_date, time(15, 0, 0), tzinfo=zone(tz_name))
