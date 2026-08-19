"""数据质量服务（AGENTS.md 铁律 2-6；MASTER_PLAN §11.5）。

9 项检查：
1. 必填字段校验      2. 空值检测         3. 非法价格/数量
4. trade_date↔quote_time 一致性  5. 延迟数据标记  6. 上游字段变化检测
7. 双源冲突检测（阈值可配置，D-012）
8. manual_verified 人工确认数据优先（保留冲突证据，不删除）
9. stale/missing 缓存判定（旧缓存不得冒充当天数据）

结果可持久化到 data_quality_issues（repositories.quality）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Literal

from pydantic import BaseModel, Field

from ashare_review.config import AppConfig
from ashare_review.constants import PRICE_TYPES
from ashare_review.db.timeutils import as_shanghai
from ashare_review.models.market_data import MarketDataPoint

# 11 字段（铁律 2）
REQUIRED_FIELDS = (
    "symbol",
    "market",
    "trade_date",
    "quote_time",
    "fetched_at",
    "source",
    "price_type",
    "adjustment",
    "is_delayed",
    "raw_value",
    "normalized_value",
)

# 属于"价格"的 price_type（必须 > 0 且 <= max_price）
PRICE_LIKE_TYPES = ("open", "high", "low", "close", "prev_close", "last")
# 属于"数量/金额"的 price_type（必须 >= 0）
QUANTITY_LIKE_TYPES = ("volume", "amount")


class QualityIssue(BaseModel):
    """一次质量问题的结构化描述（可持久化）。"""

    issue_type: str
    severity: Literal["info", "warning", "error", "critical"] = "warning"
    source: str | None = None
    symbol: str | None = None
    market: str | None = None
    trade_date: date | None = None
    evidence: str = ""


@dataclass(frozen=True)
class CacheLookupResult:
    """stale/missing 判定结果（检查 9）。"""

    status: Literal["ok", "stale", "missing"]
    requested_trade_date: date
    found_trade_date: date | None = None
    point: MarketDataPoint | None = None


class QualityService:
    def __init__(self, config: AppConfig | None = None):
        from ashare_review.config import get_config

        self.config = config or get_config()

    # ---------- 1/2. 必填字段与空值 ----------
    def check_required_fields(self, point: MarketDataPoint) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        missing = [f for f in REQUIRED_FIELDS if getattr(point, f, None) is None]
        if missing:
            issues.append(
                QualityIssue(
                    issue_type="missing_required_field",
                    severity="error",
                    source=point.source,
                    symbol=point.symbol,
                    market=point.market,
                    trade_date=point.trade_date,
                    evidence=f"缺少字段：{missing}",
                )
            )
        return issues

    def check_null_values(self, point: MarketDataPoint) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for f in REQUIRED_FIELDS:
            v = getattr(point, f, None)
            if v is None or (isinstance(v, str) and v.strip() == ""):
                issues.append(
                    QualityIssue(
                        issue_type="null_value",
                        severity="warning",
                        source=point.source,
                        symbol=point.symbol,
                        market=point.market,
                        trade_date=point.trade_date,
                        evidence=f"字段 {f} 为空",
                    )
                )
        return issues

    # ---------- 3. 非法价格/数量 ----------
    def check_invalid_price_quantity(self, point: MarketDataPoint) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        value = point.normalized_value
        if value is None:
            return issues
        if point.price_type in PRICE_LIKE_TYPES:
            if value <= 0:
                issues.append(self._issue(point, "invalid_price", "error", f"价格必须 > 0：{value}"))
            elif value > self.config.max_price:
                issues.append(
                    self._issue(point, "invalid_price", "error", f"价格超出上界 {self.config.max_price}：{value}")
                )
        elif point.price_type in QUANTITY_LIKE_TYPES:
            if value < 0:
                issues.append(self._issue(point, "invalid_quantity", "error", f"数量/金额必须 >= 0：{value}"))
        return issues

    # ---------- 4. trade_date 与 quote_time 一致性 ----------
    def check_trade_date_quote_time_consistency(self, point: MarketDataPoint) -> list[QualityIssue]:
        qd = as_shanghai(point.quote_time).date()
        if qd != point.trade_date:
            return [
                self._issue(
                    point,
                    "trade_date_quote_time_mismatch",
                    "error",
                    f"quote_time 市场日期 {qd} 与 trade_date {point.trade_date} 不一致",
                )
            ]
        return []

    # ---------- 5. 延迟数据标记 ----------
    def check_delayed_marking(self, point: MarketDataPoint, expected_delayed: bool | None = None) -> list[QualityIssue]:
        """expected_delayed 为 None 时不校验（由适配器 meta 提供）。"""
        if expected_delayed is None:
            return []
        if point.is_delayed != expected_delayed:
            return [
                self._issue(
                    point,
                    "delayed_marking_missing",
                    "warning",
                    f"is_delayed={point.is_delayed}，预期 {expected_delayed}",
                )
            ]
        return []

    # ---------- 6. 上游字段变化检测 ----------
    def detect_field_change(self, rows: list[dict], required_columns: Iterable[str]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not rows:
            return issues
        missing = [c for c in required_columns if c not in rows[0]]
        if missing:
            issues.append(
                QualityIssue(
                    issue_type="upstream_field_change",
                    severity="error",
                    source="upstream",
                    evidence=f"上游字段缺失（可能已改名）：{missing}",
                )
            )
        return issues

    # ---------- 7. 双源冲突检测 ----------
    def check_dual_source_conflict(self, points: Iterable[MarketDataPoint]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        by_key: dict[tuple, list[MarketDataPoint]] = {}
        for p in points:
            if p.normalized_value is None:
                continue
            key = (p.symbol, p.market, p.trade_date, p.price_type, p.adjustment)
            by_key.setdefault(key, []).append(p)
        for key, group in by_key.items():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    a, b = group[i], group[j]
                    if a.source == b.source:
                        continue
                    if self._is_conflict(a.normalized_value, b.normalized_value):
                        issues.append(
                            QualityIssue(
                                issue_type="dual_source_conflict",
                                severity="error",
                                source=f"{a.source} vs {b.source}",
                                symbol=key[0],
                                market=key[1],
                                trade_date=key[2],
                                evidence=(
                                    f"price_type={key[3]} adjustment={key[4]} "
                                    f"{a.source}={a.normalized_value} vs {b.source}={b.normalized_value} "
                                    f"(rel>{self.config.dual_source_rel_threshold} "
                                    f"abs>{self.config.dual_source_abs_threshold})"
                                ),
                            )
                        )
        return issues

    def _is_conflict(self, a: Decimal, b: Decimal) -> bool:
        abs_t = self.config.dual_source_abs_threshold
        rel_t = self.config.dual_source_rel_threshold
        return abs(a - b) > max(abs_t, rel_t * max(abs(a), abs(b)))

    # ---------- 8. manual_verified 优先（保留冲突证据） ----------
    def resolve_with_manual_verified(
        self, points: list[MarketDataPoint]
    ) -> tuple[MarketDataPoint | None, list[QualityIssue]]:
        """同组点中：manual_verified 优先；其余点作为冲突证据保留（不删除）。

        返回 (选定点, 问题列表)。
        """
        issues: list[QualityIssue] = []
        manual = [p for p in points if p.source == "manual_verified"]
        if not manual:
            return (points[0] if points else None), issues
        chosen = manual[0]
        others = [p for p in points if p is not chosen and p.normalized_value is not None]
        for o in others:
            issues.append(
                QualityIssue(
                    issue_type="manual_verified_override",
                    severity="info",
                    source=o.source,
                    symbol=chosen.symbol,
                    market=chosen.market,
                    trade_date=chosen.trade_date,
                    evidence=(
                        f"manual_verified 优先：{chosen.normalized_value}；"
                        f"被覆盖来源 {o.source} 记录保留 {o.normalized_value}（证据未删除）"
                    ),
                )
            )
        return chosen, issues

    # ---------- 9. stale / missing 判定 ----------
    def resolve_cache(
        self, points: list[MarketDataPoint], requested_trade_date: date
    ) -> CacheLookupResult:
        """旧缓存不得冒充当天数据：只匹配 requested_trade_date 当天，否则 stale/missing。"""
        for p in points:
            if p.trade_date == requested_trade_date:
                return CacheLookupResult(
                    status="ok", requested_trade_date=requested_trade_date,
                    found_trade_date=p.trade_date, point=p,
                )
        if points:
            latest = max(p.trade_date for p in points)
            return CacheLookupResult(
                status="stale",
                requested_trade_date=requested_trade_date,
                found_trade_date=latest,
                point=None,
            )
        return CacheLookupResult(
            status="missing", requested_trade_date=requested_trade_date, found_trade_date=None, point=None
        )

    # ---------- 汇总：单点质量评估 ----------
    def assess_point(
        self, point: MarketDataPoint, expected_delayed: bool | None = None
    ) -> tuple[str, list[QualityIssue]]:
        """返回 (quality_status, issues)。"""
        issues: list[QualityIssue] = []
        issues += self.check_required_fields(point)
        issues += self.check_null_values(point)
        issues += self.check_invalid_price_quantity(point)
        issues += self.check_trade_date_quote_time_consistency(point)
        issues += self.check_delayed_marking(point, expected_delayed)
        if any(i.severity in ("error", "critical") for i in issues):
            status = "conflict" if any(i.issue_type == "dual_source_conflict" for i in issues) else "suspect"
        elif issues:
            status = "suspect"
        else:
            status = "ok"
        return status, issues

    @staticmethod
    def _issue(point: MarketDataPoint, issue_type: str, severity: str, evidence: str) -> QualityIssue:
        return QualityIssue(
            issue_type=issue_type,
            severity=severity,  # type: ignore[arg-type]
            source=point.source,
            symbol=point.symbol,
            market=point.market,
            trade_date=point.trade_date,
            evidence=evidence,
        )
