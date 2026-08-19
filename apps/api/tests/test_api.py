"""Phase 2A FastAPI 接口测试（完全离线，Fake 数据源，不访问网络/数据库）。"""

from __future__ import annotations

from fastapi.testclient import TestClient

from ashare_review.api.app import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "project": "A-Share-Review", "phase": "2A"}


def test_market_meta_identifies_fake():
    r = client.get("/api/v1/market/meta")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "fake"
    assert "合成数据" in body["limitations"]  # 明确不表述为真实行情


def test_market_quote_fields():
    r = client.get("/api/v1/market/quote", params={"symbol": "600519.SH", "market": "SH"})
    assert r.status_code == 200
    body = r.json()
    assert body["symbol"] == "600519.SH"
    assert body["market"] == "SH"
    assert body["source"] == "fake"
    assert float(body["price"]) > 0
    assert body["quote_time"]  # 时间字段存在
    assert body["fetched_at"]
    assert body["price_type"] == "close"


def test_market_quote_deterministic():
    r1 = client.get("/api/v1/market/quote", params={"symbol": "000001.SZ", "market": "SZ"})
    r2 = client.get("/api/v1/market/quote", params={"symbol": "000001.SZ", "market": "SZ"})
    assert r1.status_code == 200
    assert r1.json()["price"] == r2.json()["price"]


def test_market_quote_missing_param_422():
    r = client.get("/api/v1/market/quote")
    assert r.status_code == 422


def test_market_daily_normal_span():
    r = client.get(
        "/api/v1/market/daily",
        params={
            "symbol": "510300.SH",
            "market": "SH",
            "start_date": "2026-08-17",
            "end_date": "2026-08-21",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 5  # 周一到周五 5 个工作日
    assert body[0]["symbol"] == "510300.SH"
    assert body[0]["source"] == "fake"
    assert float(body[0]["close"]) > 0


def test_market_daily_inverted_dates_422():
    r = client.get(
        "/api/v1/market/daily",
        params={
            "symbol": "510300.SH",
            "market": "SH",
            "start_date": "2026-08-21",
            "end_date": "2026-08-17",
        },
    )
    assert r.status_code == 422


def test_market_daily_span_over_366_days_422():
    r = client.get(
        "/api/v1/market/daily",
        params={
            "symbol": "510300.SH",
            "market": "SH",
            "start_date": "2026-01-01",
            "end_date": "2027-02-01",  # > 366 天
        },
    )
    assert r.status_code == 422


def test_market_daily_exactly_366_days_ok():
    r = client.get(
        "/api/v1/market/daily",
        params={
            "symbol": "510300.SH",
            "market": "SH",
            "start_date": "2026-01-01",
            "end_date": "2027-01-01",  # 365 天差
        },
    )
    assert r.status_code == 200
