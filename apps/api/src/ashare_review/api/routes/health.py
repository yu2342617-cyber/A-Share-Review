"""健康检查接口。"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="健康检查")
def health() -> dict:
    return {"status": "ok", "project": "A-Share-Review", "phase": "2A"}
