"""数据质量服务测试（9 项检查，全部离线）。"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ashare_review.db.timeutils import market_close_datetime, utc_now
from ashare_review.models import MarketDataPoint
from ashare_review.quality.service import QualityService

D = date(2026, 8, 18)


def _point(**overrides) -> MarketDataPoint:
    base = {
        "symbol": "600519.SH",
        "market": "SH",
        "trade_date": D,
        "quote_time": market_close_datetime(D),
        "fetched_at": utc_now(),
        "source": "akshare",
        "price_type": "close",
        "adjustment": "none",
        "is_delayed": False,
        "raw_value": "1435.50",
        "normalized_value": Decimal("1435.50"),
        "quality_status": "ok",
    }
    base.update(overrides)
    return MarketDataPoint(**base)


def test_required_fields_missing(session):
    q = QualityService()
    p = _point(normalized_value=None)
    issues = q.check_required_fields(p)
    assert any(i.issue_type == "missing_required_field" for i in issues)
    assert "normalized_value" in issues[0].evidence


def test_null_value_detection():
    q = QualityService()
    p = _point(raw_value="")
    issues = q.check_null_values(p)
    assert any(i.issue_type == "null_value" and "raw_value" in i.evidence for i in issues)


def test_invalid_price_negative():
    q = QualityService()
    assert q.check_invalid_price_quantity(_point(normalized_value=Decimal("-1")))
    assert q.check_invalid_price_quantity(_point(normalized_value=Decimal("0")))


def test_invalid_quantity_negative():
    q = QualityService()
    issues = q.check_invalid_price_quantity(
        _point(price_type="volume", normalized_value=Decimal("-100"))
    )
    assert any(i.issue_type == "invalid_quantity" for i in issues)


def test_trade_date_quote_time_mismatch():
    q = QualityService()
    p = _point(quote_time=market_close_datetime(date(2026, 8, 19)))  # 与 trade_date 不一致
    issues = q.check_trade_date_quote_time_consistency(p)
    assert any(i.issue_type == "trade_date_quote_time_mismatch" for i in issues)


def test_delayed_marking_missing():
    q = QualityService()
    p = _point(is_delayed=False)
    issues = q.check_delayed_marking(p, expected_delayed=True)
    assert any(i.issue_type == "delayed_marking_missing" for i in issues)
    assert q.check_delayed_marking(p, expected_delayed=False) == []


def test_upstream_field_change_detection():
    q = QualityService()
    rows = [{"日期": "2026-08-18", "收盘": "1.0"}]  # 缺少 开盘/最高/最低/成交量/成交额
    issues = q.detect_field_change(rows, ("日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额"))
    assert any(i.issue_type == "upstream_field_change" for i in issues)
    assert "开盘" in issues[0].evidence


def test_dual_source_consistent():
    q = QualityService()
    points = [
        _point(source="akshare", normalized_value=Decimal("10.000")),
        _point(source="tushare", normalized_value=Decimal("10.002")),
    ]
    assert q.check_dual_source_conflict(points) == []


@pytest.mark.parametrize(
    ("a", "b", "expect_conflict"),
    [
        (Decimal("10.000"), Decimal("10.009"), False),  # 差 0.009 < rel(0.01)
        (Decimal("10.000"), Decimal("10.010"), False),  # 恰在临界 0.01，非严格大于 → 不冲突
        (Decimal("10.000"), Decimal("10.011"), True),   # 差 0.011 > 0.01 → 冲突
        (Decimal("0.300"), Decimal("0.310"), True),     # 低价：abs 0.01 > max(0.0001, 0.0003) → 冲突
        (Decimal("0.300"), Decimal("0.3003"), False),   # 低价：差 0.0003 未超过 rel(0.0003) → 不冲突
        (Decimal("0.300"), Decimal("0.3004"), True),    # 低价：差 0.0004 > 0.0003 → 冲突
    ],
)
def test_dual_source_conflict_threshold_boundary(a, b, expect_conflict):
    q = QualityService()
    points = [
        _point(source="akshare", normalized_value=a),
        _point(source="tushare", normalized_value=b),
    ]
    issues = q.check_dual_source_conflict(points)
    assert (len(issues) > 0) == expect_conflict


def test_manual_verified_priority_and_evidence_retained():
    q = QualityService()
    auto = _point(source="akshare", normalized_value=Decimal("10.000"))
    manual = _point(source="manual_verified", normalized_value=Decimal("10.010"))
    chosen, issues = q.resolve_with_manual_verified([auto, manual])
    assert chosen is manual
    assert any(i.issue_type == "manual_verified_override" and i.source == "akshare" for i in issues)
    # 冲突证据保留：问题记录中携带被覆盖来源的值
    override = next(i for i in issues if i.issue_type == "manual_verified_override")
    assert "10.010" in override.evidence and "10.000" in override.evidence


def test_manual_verified_absent_uses_first():
    q = QualityService()
    a = _point(source="akshare", normalized_value=Decimal("10.000"))
    b = _point(source="tushare", normalized_value=Decimal("10.001"))
    chosen, issues = q.resolve_with_manual_verified([a, b])
    assert chosen is a
    assert issues == []


def test_cache_resolve_ok_stale_missing():
    q = QualityService()
    today = _point()
    old = _point(trade_date=date(2026, 8, 17))
    assert q.resolve_cache([today], D).status == "ok"
    assert q.resolve_cache([old], D).status == "stale"
    assert q.resolve_cache([old], D).found_trade_date == date(2026, 8, 17)
    assert q.resolve_cache([], D).status == "missing"
    # stale 结果绝不返回 point 冒充当天数据
    assert q.resolve_cache([old], D).point is None


def test_assess_point_status():
    q = QualityService()
    status, issues = q.assess_point(_point())
    assert status == "ok"
    assert issues == []
    bad = _point(normalized_value=Decimal("-5"))
    status2, _ = q.assess_point(bad)
    assert status2 == "suspect"


def test_quality_issue_persist(session):
    from ashare_review.repositories import QualityRepository

    q = QualityService()
    issues = q.check_invalid_price_quantity(_point(normalized_value=Decimal("-1")))
    assert issues
    repo = QualityRepository(session)
    repo.add_issues(issues)
    rows = repo.list_issues(issue_type="invalid_price")
    assert len(rows) == 1
    assert rows[0].severity == "error"
    assert rows[0].status == "open"
