# ashare-review-api（数据层）

A-Share-Review 数据层：SQLite schema（SQLAlchemy 2.x + Alembic）、统一行情模型、
数据源适配器（Fake / AKShare 最小实现）、数据质量服务、离线测试。

- 开发环境与命令见项目根 [README.md](../../README.md)「数据层开发环境」一节。
- 设计与决策：MASTER_PLAN.md §11、DECISIONS.md D-010~D-014。
- 安装：`pip install -e ".[akshare,dev]"`（akshare 为可选 extra）。
