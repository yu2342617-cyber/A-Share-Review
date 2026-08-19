"""FastAPI 应用工厂（Phase 2A）。

仅提供 Fake 行情接口：/health、/api/v1/market/*。
不访问 AKShare、不写数据库、不启动定时任务、不提供真实行情。
启动：.venv\\Scripts\\python.exe -m uvicorn ashare_review.api.app:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI

from ashare_review.api.routes import health, market


def create_app() -> FastAPI:
    app = FastAPI(
        title="A-Share-Review API",
        version="0.2.0",
        description="Phase 2A：FastAPI 最小骨架 + Fake 行情接口（合成数据，不代表真实行情）",
    )
    app.include_router(health.router)
    app.include_router(market.router)
    return app


app = create_app()
