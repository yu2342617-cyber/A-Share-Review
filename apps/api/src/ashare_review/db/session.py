"""数据库引擎与会话工厂。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ashare_review.config import get_config


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def make_engine(db_path: Path | None = None, *, in_memory: bool = False, **kwargs) -> Engine:
    """创建引擎。db_path 缺省用配置；in_memory=True 用于测试（需配合 StaticPool）。"""
    cfg = get_config()
    if in_memory:
        url = "sqlite://"
    else:
        path = db_path or cfg.db_path
        path.parent.mkdir(parents=True, exist_ok=True)
        url = sqlite_url(path)
    return create_engine(url, **kwargs)


def make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)


def open_session(engine: Engine) -> Session:
    return make_session_factory(engine)()
