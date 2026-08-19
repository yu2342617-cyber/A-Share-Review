"""AKShareDataSourceAdapter：AKShare 最小日线/收盘行情入口。

设计约束（DECISIONS.md D-014）：
- akshare 延迟导入（lazy import）；未安装时抛明确 AdapterError。
- 不得假设 AKShare 字段永远不变：必填列缺失/改名 → AdapterFieldError。
- 保存原始值（raw）与标准化值；不使用搜索引擎摘要。
- 代码中不含 API Key / 代理 / Cookie / 用户凭证。

Phase 1 最小实现：A股股票（stock_zh_a_hist）与 ETF（fund_etf_hist_em）日线。
"""

from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from ashare_review.adapters.base import (
    AdapterError,
    AdapterFieldError,
    AdapterMeta,
    DailyBar,
    DataSourceAdapter,
    DelayLevel,
    QuoteTick,
)
from ashare_review.db.timeutils import market_close_datetime, utc_now

# eastmoney 日线接口的必填列（stock_zh_a_hist 与 fund_etf_hist_em 共用列名）
_REQUIRED_COLUMNS = ("日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额")


def _to_decimal(value: Any) -> Decimal | None:
    """把上游数值安全转 Decimal；NaN/None/空字符串 → None。"""
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    s = str(value).strip()
    if s == "" or s.lower() in ("nan", "none", "null", "-"):
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError) as exc:
        raise AdapterFieldError(f"无法把上游值转为 Decimal：{value!r}") from exc


def _is_etf_symbol(symbol: str, market: str) -> bool:
    """按证券代码判断是否 ETF（Phase 1 简化规则：沪 51x/56x/58x，深 15x/16x 开头）。"""
    code = symbol.split(".")[0]
    if market == "SH":
        return code.startswith(("51", "56", "58"))
    if market == "SZ":
        return code.startswith(("15", "16"))
    return False


def map_daily_rows(rows: list[dict[str, Any]], symbol: str, market: str, source: str) -> list[DailyBar]:
    """把上游日线行（dict 列表）映射为 DailyBar。

    独立静态函数，便于用本地 fixture 离线测试（不依赖 akshare/pandas）。
    rows 需按日期升序；必填列缺失/改名抛 AdapterFieldError。
    """
    if not rows:
        return []
    first = rows[0]
    missing = [c for c in _REQUIRED_COLUMNS if c not in first]
    if missing:
        raise AdapterFieldError(
            f"AKShare 上游字段缺失（可能已改名）：{missing}", missing=missing
        )

    bars: list[DailyBar] = []
    for row in rows:
        try:
            trade_date = datetime.strptime(str(row["日期"]).strip()[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError) as exc:
            raise AdapterFieldError(f"无法解析 日期 字段：{row.get('日期')!r}") from exc
        try:
            bar = DailyBar(
                symbol=symbol,
                market=market,
                trade_date=trade_date,
                quote_time=market_close_datetime(trade_date),
                fetched_at=utc_now(),
                source=source,
                open=_to_decimal(row["开盘"]),
                high=_to_decimal(row["最高"]),
                low=_to_decimal(row["最低"]),
                close=_to_decimal(row["收盘"]),
                volume=_to_decimal(row["成交量"]),
                amount=_to_decimal(row["成交额"]),
                adjustment="none",
                is_delayed=False,
                raw=dict(row),
            )
        except AdapterFieldError:
            raise
        except Exception as exc:  # 防御：其余字段问题也须显式暴露
            raise AdapterFieldError(f"AKShare 行映射失败：{exc}") from exc
        bars.append(bar)
    return bars


class AKShareDataSourceAdapter(DataSourceAdapter):
    id = "akshare"

    def _ak(self):
        try:
            import akshare as ak  # 延迟导入
        except ImportError as exc:
            raise AdapterError(
                "akshare 未安装。请执行：.venv\\Scripts\\python -m pip install -e \"apps/api[akshare]\""
            ) from exc
        return ak

    def meta(self) -> AdapterMeta:
        return AdapterMeta(
            id=self.id,
            name="AKShare (eastmoney 日线最小实现)",
            delay=DelayLevel.END_OF_DAY,
            supports=["stock", "etf"],
            limitations=(
                "Phase 1 最小实现：A股股票/ETF 日线（收盘后数据，非实时）；"
                "上游字段变化会抛 AdapterFieldError；成交量单位为手（上游约定）；"
                "不使用搜索引擎摘要；数据准确性以双源校验为准。"
            ),
        )

    def fetch_quote(self, symbol: str, market: str) -> QuoteTick:
        """最小实现：以最近一个交易日收盘价作为报价（end_of_day 语义）。"""
        bars = self.fetch_daily_history(symbol, market, date(2000, 1, 1), date.today())
        if not bars:
            raise AdapterError(f"AKShare 未取到 {symbol} 的任何日线，无法提供报价")
        last = bars[-1]
        return QuoteTick(
            symbol=symbol,
            market=market,
            quote_time=last.quote_time,
            fetched_at=last.fetched_at,
            source=self.id,
            price=last.close,
            price_type="close",
            adjustment=last.adjustment,
            is_delayed=False,
            raw_value=last.raw,
        )

    def fetch_daily_history(
        self, symbol: str, market: str, start_date: date, end_date: date
    ) -> list[DailyBar]:
        if market not in ("SH", "SZ"):
            raise AdapterError(f"市场 {market} 暂不支持（Phase 1 最小实现仅 A股 股票/ETF）")
        if start_date > end_date:
            raise ValueError("start_date 不得晚于 end_date")
        ak = self._ak()
        code = symbol.split(".")[0]
        fmt = lambda d: d.strftime("%Y%m%d")  # noqa: E731
        if _is_etf_symbol(symbol, market):
            frame = ak.fund_etf_hist_em(
                symbol=code, period="daily", start_date=fmt(start_date), end_date=fmt(end_date), adjust=""
            )
        else:
            frame = ak.stock_zh_a_hist(
                symbol=code, period="daily", start_date=fmt(start_date), end_date=fmt(end_date), adjust=""
            )
        if frame is None or len(frame) == 0:
            return []
        # 转 dict 列表（避免在离线测试中依赖 pandas 语义）
        rows = [dict(row) for row in frame.to_dict("records")]
        return map_daily_rows(rows, symbol, market, self.id)
