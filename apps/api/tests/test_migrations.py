"""数据库初始化与 Alembic 迁移测试（临时 SQLite，不触碰真实 storage/db）。"""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from ashare_review import cli

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"

EXPECTED_TABLES = {
    "instruments",
    "instrument_trade_rules",
    "market_data_points",
    "source_fetch_runs",
    "data_quality_issues",
    "positions",
    "trades",
    "companies",
    "events",
}


def _alembic_cfg(tmp_path: Path) -> tuple[Config, Path]:
    cfg = Config(str(ALEMBIC_INI))
    db = tmp_path / "migration_test.db"
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db.as_posix()}")
    return cfg, db


def _tables(db: Path) -> set[str]:
    eng = create_engine(f"sqlite:///{db.as_posix()}")
    try:
        return set(inspect(eng).get_table_names())
    finally:
        eng.dispose()


def test_alembic_upgrade_creates_all_tables(tmp_path):
    cfg, db = _alembic_cfg(tmp_path)
    command.upgrade(cfg, "head")
    assert EXPECTED_TABLES <= _tables(db)


def test_alembic_downgrade_roundtrip(tmp_path):
    cfg, db = _alembic_cfg(tmp_path)
    command.upgrade(cfg, "head")
    assert EXPECTED_TABLES <= _tables(db)
    command.downgrade(cfg, "base")
    remaining = _tables(db)
    # 业务表应全部删除；alembic_version 表保留属 Alembic 正常行为
    assert remaining.isdisjoint(EXPECTED_TABLES), f"仍有业务表残留: {remaining & EXPECTED_TABLES}"
    command.upgrade(cfg, "head")  # 可再次升级
    assert EXPECTED_TABLES <= _tables(db)


def test_db_init_cli_creates_tables(tmp_path):
    db = tmp_path / "cli_test.db"
    rc = cli.main(["--db-path", str(db), "--tables"])
    assert rc == 0
    assert EXPECTED_TABLES <= _tables(db)


def test_db_init_cli_prepares_directory(tmp_path):
    db = tmp_path / "sub" / "cli_dir_only.db"
    rc = cli.main(["--db-path", str(db)])
    assert rc == 0
    assert db.parent.is_dir()
    assert not db.exists()  # 未建表
