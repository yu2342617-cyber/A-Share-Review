# PROJECT_STATE.md — 项目状态

> 每轮工作结束必须更新：当前阶段、已完成、进行中、下一步、已验证命令。
> 最后更新：2026-08-19（Phase 0）

## 当前阶段

**Phase 2A：FastAPI 最小骨架 + Fake 行情接口 —— 实现完成，等待评审（2026-08-19）。** 分支 `feat/phase-2a-api-skeleton`，未合并 main。

## 已完成

- [x] 项目根目录确认为 `D:\A-Share-Review`（工作目录已切换并验证）
- [x] Git 仓库初始化（`git init`，未提交、未修改全局配置）
- [x] 创建 10 个根文件：README.md、MASTER_PLAN.md、AGENTS.md、PROJECT_STATE.md、DECISIONS.md、TASKS.md、CHANGELOG.md、HANDOFF.md、.env.example、.gitignore
- [x] 创建 20 个基础目录（apps/web、apps/api、packages/shared、config、data/*、docs/*、scripts、storage/*、tests/*），空目录已添加 .gitkeep
- [x] 写入总体技术方案（React+TS+Vite+ECharts / Python+FastAPI / SQLite / Pandas / APScheduler / 统一数据源适配层 / 大模型适配层）
- [x] 写入数据准确性铁律（AGENTS.md + docs/data-sources/data-quality.md）
- [x] 建立 AI 交接制度（六文档阅读顺序 + 四文档每轮更新）
- [x] 隐私安全：.gitignore 覆盖 data/private、storage/db、storage/cache、storage/logs、.env、券商导出原件
- [x] 创建 data/imports/positions.example.csv（仅字段与虚拟示例）
- [x] 创建 data/private/README.md（本地私有说明与待录入清单；该目录 gitignore，内容绝不入库）
- [x] 创建 docs/private-data-format.md（可提交的私有持仓通用格式说明，仅字段与虚拟示例）
- [x] 验收：gitignore 覆盖检查、UTF-8 编码检查、Markdown 一致性检查

## Phase 0 修正（2026-08-19）

- [x] .gitignore 改为"目录忽略实际内容、保留并允许提交 .gitkeep"：data/raw、data/processed、data/exports、data/private、storage/db、storage/cache、storage/logs
- [x] 创建 data/private/.gitkeep（真实私有数据仍被忽略）
- [x] 通用私有格式说明从 data/private/README.md 整理到可提交文档 docs/private-data-format.md（不含真实持仓）
- [x] data/private/README.md 保留本地真实持仓信息，继续被忽略，未删除用户本地数据
- [x] README/MASTER_PLAN/TASKS/HANDOFF 等文档的格式引用统一指向 docs/private-data-format.md
- [x] 复查：真实持仓代码未出现在任何可提交文件中

## Phase 2A 完成清单（2026-08-19，分支 feat/phase-2a-api-skeleton）

- [x] 依赖：pyproject 增加 fastapi / uvicorn（httpx 进 dev extra）；venv 内安装（fastapi 0.141.1 / uvicorn 0.52.4 / httpx 0.28.1）
- [x] `api/app.py`：`create_app()` + 模块级 `app`；路由 health / market
- [x] `GET /health` → `{"status":"ok","project":"A-Share-Review","phase":"2A"}`
- [x] `GET /api/v1/market/meta` → FakeDataSourceAdapter.meta()（id=fake，明确合成数据）
- [x] `GET /api/v1/market/quote?symbol=&market=` → Fake fetch_quote（Pydantic 结构化）
- [x] `GET /api/v1/market/daily?symbol=&market=&start_date=&end_date=` → Fake fetch_daily_history；倒置日期 422、>366 天 422
- [x] 接口测试 9 项（离线）；**73 passed, 0 failed**（64 原有 + 9 新增；smoke 默认跳过）
- [x] 不启动常驻服务（仅测试验证）；不访问 AKShare/网络；不写数据库

**当前明确状态**：只有 Fake 行情 API；没有接入真实行情；没有启动 APScheduler；没有进入前端开发；没有合并 main（Phase 1 分支 `feat/phase-1-data-layer` 亦未合并）。

## 进行中

- **无。** Phase 2A 实现完成，等待评审。
- 待用户决策：Phase 1 与 Phase 2A 分支是否合入 main（本轮均未合并、未 force push）。

## Phase 1 完成清单（2026-08-19）

- [x] SQLite schema（SQLAlchemy 2.x）：9 张业务表 + 唯一约束/索引；Alembic 初始迁移 `d68db143309f`
- [x] 统一行情模型：market_data_points 11 字段 + quality_status
- [x] 数据源适配器：DataSourceAdapter 接口（meta/fetch_quote/fetch_daily_history）+ Fake（离线确定性）+ AKShare（A股股票/ETF 日线，lazy import，字段变化抛 AdapterFieldError）
- [x] 数据质量服务：9 项检查 + 双源阈值可配置（默认 rel 0.001 / abs 0.0001）+ manual_verified 优先 + stale/missing 判定
- [x] Decimal/NUMERIC 精度与 UTC 时间（ExactDecimal / UTCDateTime，DECISIONS D-010/D-011/D-015）
- [x] 离线测试套件（64 项）+ AKShare 联网 smoke（3 项，默认排除）
- [x] 数据库初始化命令（alembic upgrade head / ashare-db-init）+ scripts/db-init.ps1、run-tests.ps1
- [x] 隐私检查：无 .env/.venv/db/缓存/密钥/真实持仓代码/运行数据入库

## 下一步（等待用户确认后执行）

1. **评审 Phase 1 与 Phase 2A**：确认测试与审查 ZIP 后，由用户决定分支合入 main 的时机。
2. **Phase 2B（后端 API 扩展）**：真实行情接口（AKShare）、持仓/交易接口、APScheduler 定时任务（用户指示 Phase 2A 不开发）。
3. 用户将在本地私有数据中录入真实持仓（私有数据通用格式见 docs/private-data-format.md；待录入清单见 data/private/README.md，该目录 gitignore、不入库）。
4. 用户确认后更新本文件与 MASTER_PLAN.md 的对应规划。

## 已验证命令

| 命令 | 结果 |
| --- | --- |
| `git init`（D:\A-Share-Review） | 成功，空仓库初始化，未提交 |
| 目录创建（New-Item -Force） | 20 个目录全部创建成功 |
| 文件写入（UTF-8） | 全部成功，编码检查通过 |
| `git check-ignore`（Phase 0 修正复查） | 私有数据/运行目录内容被忽略、.gitkeep 不被忽略，全部符合预期 |
| 敏感信息搜索（Phase 0 修正） | 未发现非空密钥/密码/Token 内容 |
| `.venv\Scripts\python -m pytest apps/api` | **64 passed, 0 failed**（Phase 1，1.58s，离线；smoke 默认排除） |
| `.venv\Scripts\python -m pytest apps/api -m smoke` | **3 passed**（AKShare 真实联网验证通过） |
| `alembic -c apps/api/alembic.ini upgrade head` | 成功，storage/db/ashare_review.db 建 10 表（9 业务表 + alembic_version） |
| `.venv\Scripts\python -m pytest apps/api`（Phase 2A 后） | **73 passed, 0 failed**（64 原有 + 9 API 新增，1.25s，离线） |
| `pip install -e "apps/api[akshare,dev]"`（Phase 2A 依赖） | ✅ fastapi 0.141.1 / uvicorn 0.52.4 / httpx 0.28.1（venv 内） |

## 环境要求

- 数据层：Python 3.11.9（本机已有）+ `.venv`（项目根，gitignore）；依赖 sqlalchemy 2.0.52 / alembic 1.19.1 / pydantic 2.13.4 / pytest 9.1.1 / akshare 1.18.92（可选 extra）。
- 网络注记：本机 GitHub/PyPI 直连不稳定，pip 安装需 `--proxy http://127.0.0.1:7890`（必要时加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`）；git 已配 openssl 后端 + 代理（--local）。
- 未获访问权限：TradingView、通达信（不得假设已获得账户、本地文件或软件数据访问权限）。
