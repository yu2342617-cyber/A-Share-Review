"""精确 Decimal 与 UTC DateTime 类型装饰器。

SQLite 没有原生 DECIMAL 类型（NUMERIC 亲和性会退化为 REAL 存储，
导致 0.649 之类的十进制值精度丢失）。为满足"数据准确性最高优先级"
（DECISIONS.md D-010），本装饰器在 SQLite 上以字符串存储精确保留
scale 位小数的 Decimal；在其他方言上回退为 NUMERIC(p, s)。

同时 SQLite 的 DateTime(timezone=True) 不保留时区（读回 naive），
违反 D-011；UTCDateTime 在 SQLite 上以带偏移的 ISO 字符串存储 UTC，
读取时还原为 timezone-aware 的 UTC datetime。

实现说明：直接覆写 bind_processor / result_processor，不依赖
TypeDecorator 默认的 impl 处理器链（该链会经过 Numeric 的
DecimalResultProcessor，导致尾零丢失等不可预测行为）。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

import sqlalchemy as sa
from sqlalchemy.types import TypeDecorator

from ashare_review.db.timeutils import UTC, ensure_aware


class ExactDecimal(TypeDecorator):
    """精确 Decimal 列。

    用法：price: Mapped[Decimal] = mapped_column(ExactDecimal(18, 6))
    """

    impl = sa.Numeric
    cache_ok = True

    def __init__(self, precision: int = 18, scale: int = 6):
        super().__init__(precision=precision, scale=scale, asdecimal=True)
        self.precision = precision
        self.scale = scale

    def load_dialect_impl(self, dialect) -> sa.types.TypeEngine:
        if dialect.name == "sqlite":
            # SQLite 以 TEXT 存储，保留精度
            return dialect.type_descriptor(sa.String(64))
        return dialect.type_descriptor(sa.Numeric(self.precision, self.scale))

    def bind_processor(self, dialect):
        """写入：Decimal → 定长 scale 位小数的字符串。"""

        def process(value):
            if value is None:
                return None
            if isinstance(value, Decimal):
                d = value
            elif isinstance(value, str):
                d = Decimal(value)
            else:
                raise TypeError(
                    f"ExactDecimal 只接受 Decimal/str，收到 {type(value).__name__}"
                )
            quantum = Decimal(1).scaleb(-self.scale)
            return str(d.quantize(quantum, rounding=ROUND_HALF_UP))

        return process

    def result_processor(self, dialect, coltype):
        """读取：数据库字符串 → Decimal（保留全部小数位）。"""

        def process(value):
            if value is None:
                return None
            return Decimal(str(value).strip())

        return process


class UTCDateTime(TypeDecorator):
    """UTC 时间列（DECISIONS.md D-011）。

    - SQLite 以带偏移 ISO 字符串存储 UTC（如 2026-08-18T07:00:00+00:00）。
    - 读取还原为 timezone-aware 的 UTC datetime。
    - naive 输入按 Asia/Shanghai 补时区（防御性；正常路径由适配层拦截）。
    """

    impl = sa.DateTime(timezone=True)
    cache_ok = True

    def load_dialect_impl(self, dialect) -> sa.types.TypeEngine:
        if dialect.name == "sqlite":
            return dialect.type_descriptor(sa.String(35))
        return dialect.type_descriptor(sa.DateTime(timezone=True))

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            if not isinstance(value, datetime):
                raise TypeError(f"UTCDateTime 只接受 datetime，收到 {type(value).__name__}")
            return ensure_aware(value).astimezone(UTC).isoformat()

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            dt = datetime.fromisoformat(str(value))
            # 自己写入的值必带 +00:00；防御性兜底：无偏移则视为 UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt

        return process
