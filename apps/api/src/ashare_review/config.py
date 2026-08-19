"""应用配置：路径、时区、双源阈值等。

- 配置来源：环境变量覆盖默认值（不读取 .env；密钥类配置不在此列）。
- 数据库默认落在 <项目根>/storage/db/ashare_review.db（gitignore）。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

# apps/api/src/ashare_review/config.py -> parents:
#   [0] ashare_review, [1] src, [2] api, [3] apps, [4] 项目根
PROJECT_ROOT = Path(__file__).resolve().parents[4]

DEFAULT_TIMEZONE = "Asia/Shanghai"


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    if not raw:
        return default
    p = Path(raw)
    return p if p.is_absolute() else (PROJECT_ROOT / p)


@dataclass(frozen=True)
class AppConfig:
    """运行配置（Phase 1 数据层）。"""

    project_root: Path = PROJECT_ROOT
    # 数据库文件（gitignore：storage/db/）
    db_path: Path = field(
        default_factory=lambda: _env_path("ASHARE_DB_PATH", PROJECT_ROOT / "storage" / "db" / "ashare_review.db")
    )
    # 时间
    timezone: str = os.environ.get("ASHARE_TIMEZONE", DEFAULT_TIMEZONE)
    # 双源冲突阈值（见 DECISIONS.md D-012）
    dual_source_rel_threshold: Decimal = Decimal(os.environ.get("ASHARE_DUAL_REL", "0.001"))
    dual_source_abs_threshold: Decimal = Decimal(os.environ.get("ASHARE_DUAL_ABS", "0.0001"))
    # 价格/数量精度（见 DECISIONS.md D-010）
    money_scale: int = 6
    quantity_scale: int = 4
    # 非法价格上界（防御性）
    max_price: Decimal = Decimal("1000000")


_config: AppConfig | None = None


def get_config() -> AppConfig:
    """进程级单例配置。"""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def set_config(cfg: AppConfig) -> None:
    """测试用：覆盖进程级配置。"""
    global _config
    _config = cfg
