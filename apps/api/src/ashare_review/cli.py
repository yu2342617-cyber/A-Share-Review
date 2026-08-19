"""命令行入口：数据库初始化。

用法：
  ashare-db-init                 # 确保数据库目录存在
  ashare-db-init --tables        # 直接用 create_all 建表（不走 Alembic，仅快速开发用）
  alembic -c apps/api/alembic.ini upgrade head   # 推荐：Alembic 迁移
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ashare_review.config import get_config
from ashare_review.db.session import make_engine


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ashare-db-init", description="A-Share-Review 数据库初始化")
    parser.add_argument("--db-path", default=None, help="覆盖数据库路径")
    parser.add_argument(
        "--tables",
        action="store_true",
        help="直接用 create_all 建表（开发用；生产路径请用 alembic upgrade head）",
    )
    args = parser.parse_args(argv)

    cfg = get_config()
    path = Path(args.db_path) if args.db_path else cfg.db_path
    path.parent.mkdir(parents=True, exist_ok=True)

    if args.tables:
        from ashare_review.models import Base

        engine = make_engine(path)
        Base.metadata.create_all(engine)
        print(f"[ok] 已用 create_all 建表：{path}")
    else:
        print(f"[ok] 数据库目录就绪：{path.parent}")
        print("     下一步：alembic -c apps/api/alembic.ini upgrade head")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
