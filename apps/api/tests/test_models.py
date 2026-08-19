"""数据模型测试：字段完整性、Decimal 精度、唯一约束、ETF 规则按代码配置。"""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from ashare_review.db.types import ExactDecimal
from ashare_review.models import (
    Instrument,
    InstrumentTradeRule,
    MarketDataPoint,
    Position,
    Trade,
)
from ashare_review.quality.service import REQUIRED_FIELDS


def test_market_data_point_has_all_11_required_fields():
    cols = set(MarketDataPoint.__table__.columns.keys())
    for f in REQUIRED_FIELDS:
        assert f in cols, f"缺少必填字段 {f}"


def test_market_data_point_roundtrip(session, make_point):
    p = make_point()
    session.add(p)
    session.commit()
    session.expire_all()  # 强制真实 DB 往返（避免身份映射返回原对象）
    got = session.get(MarketDataPoint, p.id)
    assert got.symbol == "600519.SH"
    assert got.market == "SH"
    assert got.trade_date == p.trade_date
    assert got.quote_time.tzinfo is not None
    assert got.fetched_at.tzinfo is not None
    assert got.source == "akshare"
    assert got.price_type == "close"
    assert got.adjustment == "none"
    assert got.is_delayed is False
    assert got.raw_value == "1435.50"
    assert got.normalized_value == Decimal("1435.500000")
    assert got.quality_status == "ok"


@pytest.mark.parametrize(
    ("price", "expected_scale"),
    [
        ("38.69", -6),      # 招商银行风格成本价
        ("0.649", -6),      # 低价 ETF 风格
        ("10.00", -6),
        ("0.380", -6),
    ],
)
def test_decimal_precision_exact(session, make_point, price, expected_scale):
    p = make_point(normalized_value=Decimal(price))
    session.add(p)
    session.commit()
    session.expire_all()  # 真实 DB 往返
    got = session.get(MarketDataPoint, p.id)
    assert got.normalized_value == Decimal(price)
    assert got.normalized_value.as_tuple().exponent == expected_scale


def test_decimal_no_float_error_propagation():
    # Decimal 精确性：0.1 + 0.2 == 0.3（float 无法保证）
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")
    # 往返无损：0.649 不会被浮点化（经 bind/result 处理器）
    d = ExactDecimal(18, 6)
    bp = d.bind_processor("sqlite")
    rp = d.result_processor("sqlite", None)
    assert bp(Decimal("0.649")) == "0.649000"
    assert rp("0.649000") == Decimal("0.649000")


def test_duplicate_instrument_rejected(session):
    session.add(Instrument(symbol="600519.SH", market="SH", name="贵州茅台"))
    session.flush()
    session.add(Instrument(symbol="600519.SH", market="SH", name="重复"))
    with pytest.raises(IntegrityError):
        session.flush()


def test_duplicate_market_data_point_rejected(session, make_point):
    session.add(make_point())
    session.flush()
    session.add(make_point())
    with pytest.raises(IntegrityError):
        session.flush()


def test_duplicate_point_same_value_different_source_allowed(session, make_point):
    # 双源校验的前提：不同 source 同点可并存
    session.add(make_point(source="akshare"))
    session.flush()
    session.add(make_point(source="tushare"))
    session.flush()


def test_etf_trade_rules_configured_per_symbol(session):
    """ETF 交易制度必须按证券代码配置（D-006）：同为 ETF 可分别 T+0 / T+1。"""
    ins_a = Instrument(symbol="512100.SH", market="SH", name="ETF-A", security_type="etf")
    ins_b = Instrument(symbol="510300.SH", market="SH", name="ETF-B", security_type="etf")
    session.add_all([ins_a, ins_b])
    session.flush()
    session.add_all(
        [
            InstrumentTradeRule(
                instrument_id=ins_a.id, symbol="512100.SH", market="SH",
                trade_cycle="T+0", min_trade_unit=Decimal("100"), price_precision=3,
            ),
            InstrumentTradeRule(
                instrument_id=ins_b.id, symbol="510300.SH", market="SH",
                trade_cycle="T+1", min_trade_unit=Decimal("100"), price_precision=3,
            ),
        ]
    )
    session.flush()
    rules = {r.symbol: r.trade_cycle for r in session.query(InstrumentTradeRule).all()}
    assert rules["512100.SH"] == "T+0"
    assert rules["510300.SH"] == "T+1"


def test_duplicate_trade_rule_rejected(session):
    ins = Instrument(symbol="600519.SH", market="SH", name="贵州茅台")
    session.add(ins)
    session.flush()
    session.add(InstrumentTradeRule(instrument_id=ins.id, symbol="600519.SH", market="SH"))
    session.flush()
    session.add(InstrumentTradeRule(instrument_id=ins.id, symbol="600519.SH", market="SH"))
    with pytest.raises(IntegrityError):
        session.flush()


def test_position_decimal_roundtrip(session):
    pos = Position(
        symbol="601398.SH", market="SH", name="工商银行（测试）",
        quantity=Decimal("600"), cost_price=Decimal("38.69"), currency="CNY",
    )
    session.add(pos)
    session.commit()
    session.expire_all()  # 真实 DB 往返
    got = session.get(Position, pos.id)
    assert got.quantity == Decimal("600.0000")
    assert got.cost_price == Decimal("38.690000")


def test_trade_decimal_roundtrip(session):
    t = Trade(
        symbol="510300.SH", market="SH", trade_date=__import__("datetime").date(2026, 8, 18),
        side="buy", quantity=Decimal("25800"), price=Decimal("0.649"),
        fee=Decimal("0.50"), amount=Decimal("16744.20"), currency="CNY",
    )
    session.add(t)
    session.commit()
    session.expire_all()  # 真实 DB 往返
    got = session.get(Trade, t.id)
    assert got.price == Decimal("0.649000")
    assert got.fee == Decimal("0.500000")
    assert got.amount == Decimal("16744.200000")
