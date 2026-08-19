# HANDOFF.md — 交接说明

> 每轮工作结束必须更新：修改文件、运行命令、测试结果、已知问题、环境要求、下一位 AI 的明确起点。
> 最后更新：2026-08-19（Phase 1 数据层实现完成，分支 feat/phase-1-data-layer，未合并）

## 本轮修改的文件

**新增（apps/api 数据层，41 个候选文件）**
- 工程：`apps/api/pyproject.toml`、`apps/api/README.md`、`apps/api/alembic.ini`、`apps/api/alembic/env.py`、`apps/api/alembic/script.py.mako`、`apps/api/alembic/versions/d68db143309f_initial_schema.py`
- 包 `apps/api/src/ashare_review/`：`__init__.py`、`config.py`、`constants.py`、`cli.py`
  - `db/`：base.py、session.py、timeutils.py、types.py（ExactDecimal / UTCDateTime）
  - `models/`：__init__.py、instruments.py、market_data.py、source_runs.py、quality.py、portfolio.py、companies.py
  - `adapters/`：__init__.py、base.py（接口 + Pydantic 模型）、fake.py、akshare.py
  - `quality/`：__init__.py、service.py
  - `repositories/`：__init__.py、market_data.py
- 测试 `apps/api/tests/`：conftest.py + test_models / test_migrations / test_repository_market_data / test_quality / test_adapters_fake / test_adapters_akshare / test_timeutils / test_smoke_akshare_network
- 脚本：`scripts/db-init.ps1`、`scripts/run-tests.ps1`

**修改（5 个）**：README.md（数据层开发命令章节）、MASTER_PLAN.md（§11）、DECISIONS.md（D-010~D-015）、PROJECT_STATE.md、TASKS.md；CHANGELOG.md 追加本条

## 数据库表（9 张业务表 + alembic_version）

| 表 | 关键字段/约束 |
| --- | --- |
| instruments | (symbol,market) 唯一；security_type/currency/price_tick/trade_status |
| instrument_trade_rules | (symbol,market) 唯一（ETF 按代码配置 T+0/T+1）；min_trade_unit/price_precision |
| market_data_points | 11 字段铁律 + quality_status；唯一约束 (symbol,market,trade_date,quote_time,source,price_type,adjustment,is_delayed) + 4 索引 |
| source_fetch_runs | source/started_at/finished_at/status/records_count/error_summary/data_date |
| data_quality_issues | issue_type/severity/evidence/status + 3 索引 |
| positions | (symbol,market) 唯一；quantity NUMERIC(18,4)/cost_price NUMERIC(18,6)（本轮只建结构） |
| trades | side/quantity/price/fee/amount/settlement_rule |
| companies | (symbol,market) 唯一；company_name/industry/listing_date |
| events | event_type/title/content/source/source_url/event_time（aware） |

价格/成本/费用：ExactDecimal(18,6)；数量 ExactDecimal(18,4)；时间：UTCDateTime（UTC 存储）。

## 运行过的命令与结果

| 命令 | 结果 |
| --- | --- |
| `python -m venv .venv` | ✅ |
| `pip install -e "apps/api[akshare,dev]"`（经代理 7890 + 清华镜像，--timeout 10 --retries 30 --no-build-isolation） | ✅ 87 包；关键版本 sqlalchemy 2.0.52 / alembic 1.19.1 / pydantic 2.13.4 / pytest 9.1.1 / akshare 1.18.92 |
| `alembic revision --autogenerate -m "initial schema"`（临时 DB） | ✅ 迁移 d68db143309f |
| `alembic -c apps/api/alembic.ini upgrade head` | ✅ 真实 DB storage/db/ashare_review.db 建 10 表 |
| `.venv\Scripts\python -m pytest apps/api` | ✅ **64 passed, 0 failed**（1.58s，离线） |
| `.venv\Scripts\python -m pytest apps/api -m smoke` | ✅ **3 passed**（AKShare 真实联网：股票/ETF 日线 + 报价） |
| 隐私检查（git check-ignore / 敏感模式 / 真实持仓代码） | ✅ 全部通过 |

## 安装依赖（本轮新增，仅 venv 内）

sqlalchemy、alembic、pydantic（+ 可选 akshare、dev pytest）；未安装 FastAPI/前端/Docker/LLM 依赖。

## 网络/代理问题（重要）

1. **本机 schannel TLS 故障**（git/.NET/curl 直连 GitHub 失败）；git 已配 `http.sslBackend=openssl` + 代理（--local）。
2. **pip 直连 files.pythonhosted.org 间歇性停滞**（首个请求成功、后续连接挂起）；解决方案：`--proxy http://127.0.0.1:7890 -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 10 --retries 30`；如遇构建元数据失败加 `--no-build-isolation`（venv 内 setuptools 84 / wheel 已装）。
3. AKShare 联网 smoke 测试实际运行通过（1.9s），但网络不稳定，普通测试默认排除 smoke。

## 已知问题

1. SQLite 存储实现：ExactDecimal 存 TEXT、UTCDateTime 存 ISO 字符串（见 DECISIONS D-015）——迁移 DDL 为 VARCHAR(35/64)，跨方言移植时注意（非目标）。
2. `market_data_points` 唯一约束含 `quote_time`：同一天多次抓取同一行情点若 quote_time 一致会冲突——设计如此（防重复），后续 Phase 如需 upsert 语义再扩展（登记 DECISIONS 后实施）。
3. AKShare 适配器为最小实现：仅 A股股票（stock_zh_a_hist）与 ETF（fund_etf_hist_em）日线；港股/指数/实时行情未实现；成交量单位为手（上游约定，meta 中注明）。
4. smoke 测试依赖网络与 akshare；离线环境跳过（`pytest.importorskip` + 默认 `-m "not smoke"`）。
5. 真实持仓仍未录入（待录入清单在 data/private/README.md，gitignore）。

## 环境要求

- Python 3.11.9（本机）；`.venv` 在项目根；数据层命令见 README「数据层开发环境」。
- 数据库默认 `storage/db/ashare_review.db`（gitignore）；`ASHARE_DB_PATH` 可覆盖。
- 未获访问权限：TradingView、通达信（不得假设可用）。

## 下一位 AI 的明确起点

1. **先阅读**：AGENTS.md → MASTER_PLAN.md → PROJECT_STATE.md → DECISIONS.md → TASKS.md → HANDOFF.md（本文件）。
2. **等待用户评审 Phase 1**；用户确认后决定是否合并 `feat/phase-1-data-layer` 到 main（本轮不合并、不 force push）。
3. 评审要点：64 项离线测试 + 3 项 smoke + 安全审查 ZIP `D:\A-Share-Review-Phase1-review.zip`（仅含 git 跟踪文件）。
4. 合入后进入 Phase 2（FastAPI 基础 API + APScheduler）；动手前先更新 MASTER_PLAN/DECISIONS/TASKS 登记设计。
5. 操作纪律：不读取/导出 GCM 凭据；不修改全局 Git/代理/证书配置；pip 安装按上文代理参数；测试默认离线。
