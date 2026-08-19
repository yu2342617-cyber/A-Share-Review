"""Alembic 迁移环境。

- 目标 metadata：ashare_review.models（完整 9 表）。
- sqlalchemy.url：优先取 alembic.ini 已配置值（测试可覆盖）；否则来自 AppConfig
  （默认 storage/db/ashare_review.db，ASHARE_DB_PATH 可覆盖）。
- SQLite 使用 render_as_batch（后续 ALTER 兼容）。
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from ashare_review.config import get_config
from ashare_review.db.base import Base
from ashare_review.db.session import sqlite_url

# 确保全部模型注册到 metadata（自动生成迁移时表完整）
import ashare_review.models  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configured_url = config.get_main_option("sqlalchemy.url")
if not configured_url:
    cfg = get_config()
    configured_url = sqlite_url(cfg.db_path)
    config.set_main_option("sqlalchemy.url", configured_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
