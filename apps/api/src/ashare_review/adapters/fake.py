"""FakeDataSourceAdapter：完全离线的确定性测试适配器。

同一 (symbol, market, 日期区间) 输入始终产生相同输出（确定性），
不依赖网络与任何外部库。
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, time
from decimal import Decimal

from ashare_review.adapters.base import (
    AdapterMeta,
    DailyBar,
    DataSourceAdapter,
    DelayLevel,
    QuoteTick,
)
from ashare_review.db.timeutils import to_utc, utc_now

_BASE_PRICES = {
    "SH": Decimal("10.00"),
    "SZ": Decimal("10.00"),
    "HK": Decimal("50.00"),
}


def _seed(symbol: str, market: str) -> int:
    h = hashlib.md5(f"{market}:{symbol}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


class FakeDataSourceAdapter(DataSourceAdapter):
    id = "fake"

    def meta(self) -> AdapterMeta:
        return AdapterMeta(
            id=self.id,
            name="FakeDataSource (offline deterministic)",
            delay=DelayLevel.END_OF_DAY,
            supports=["stock", "etf", "index", "hk"],
            limitations="合成数据，仅用于离线确定性测试；不代表真实行情。",
        )

    def _base_price(self, symbol: str, market: str) -> Decimal:
        seed = _seed(symbol, market)
        base = _BASE_PRICES.get(market, Decimal("10.00"))
        # 确定性波动：base + (seed % 500) / 100
        return base + Decimal(seed % 500) / Decimal(100)

    def fetch_quote(self, symbol: str, market: str) -> QuoteTick:
        price = self._base_price(symbol, market)
        now = utc_now()
        return QuoteTick(
            symbol=symbol,
            market=market,
            quote_time=to_utc(datetime.combine(now.astimezone().date(), time(15, 0))),
            fetched_at=now,
            source=self.id,
            price=price,
            price_type="close",
            adjustment="none",
            is_delayed=False,
            raw_value={"generator": "fake", "symbol": symbol, "market": market},
        )

    def fetch_daily_history(
        self, symbol: str, market: str, start_date: date, end_date: date
    ) -> list[DailyBar]:
        if start_date > end_date:
            raise ValueError("start_date 不得晚于 end_date")
        base = self._base_price(symbol, market)
        bars: list[DailyBar] = []
        day_index = 0
        d = start_date
        while d <= end_date:
            if d.weekday() < 5:  # 仅工作日
                close = base + Decimal(day_index) * Decimal("0.01")
                bar = DailyBar(
                    symbol=symbol,
                    market=market,
                    trade_date=d,
                    quote_time=to_utc(datetime.combine(d, time(15, 0))),
                    fetched_at=utc_now(),
                    source=self.id,
                    open=close - Decimal("0.02"),
                    high=close + Decimal("0.03"),
                    low=close - Decimal("0.05"),
                    close=close,
                    volume=Decimal(1000 + (day_index * 37) % 1000),
                    amount=close * Decimal(1000 + (day_index * 37) % 1000),
                    adjustment="none",
                    is_delayed=False,
                    raw={"generator": "fake", "symbol": symbol, "day_index": day_index},
                )
                bars.append(bar)
                day_index += 1
            d = date.fromordinal(d.toordinal() + 1)
        return bars
