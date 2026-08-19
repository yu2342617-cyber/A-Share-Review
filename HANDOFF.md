# HANDOFF.md — 交接说明

> 每轮工作结束必须更新：修改文件、运行命令、测试结果、已知问题、环境要求、下一位 AI 的明确起点。
> 最后更新：2026-08-19（Phase 2A：FastAPI 最小骨架 + Fake 行情接口，实现完成待评审）

## 本轮修改的文件

**新增（6 个）**
- `apps/api/src/ashare_review/api/__init__.py`
- `apps/api/src/ashare_review/api/app.py`（`create_app()` + 模块级 `app`；启动：`python -m uvicorn ashare_review.api.app:app --host 127.0.0.1 --port 8000`）
- `apps/api/src/ashare_review/api/routes/__init__.py`
- `apps/api/src/ashare_review/api/routes/health.py`（GET /health）
- `apps/api/src/ashare_review/api/routes/market.py`（GET /api/v1/market/meta、quote、daily）
- `apps/api/tests/test_api.py`（9 项离线测试）

**修改（5 个）**：`apps/api/pyproject.toml`（fastapi/uvicorn/httpx）、MASTER_PLAN.md（§12）、PROJECT_STATE.md、TASKS.md、CHANGELOG.md

## 新增接口

| 接口 | 说明 |
| --- | --- |
| GET /health | `{"status":"ok","project":"A-Share-Review","phase":"2A"}` |
| GET /api/v1/market/meta | FakeDataSourceAdapter.meta()（id=fake，limitations 明确"合成数据"） |
| GET /api/v1/market/quote?symbol=&market= | Fake fetch_quote（QuoteTick，source=fake） |
| GET /api/v1/market/daily?symbol=&market=&start_date=&end_date= | Fake fetch_daily_history（DailyBar 列表）；倒置日期 422；区间 >366 天 422 |

**当前明确状态**：只有 Fake 行情 API；没有接入真实行情；没有启动 APScheduler；没有进入前端开发；未合并 main（Phase 1 与 Phase 2A 分支均未合并、未 force push）。

## 运行过的命令与结果

| 命令 | 结果 |
| --- | --- |
| `pip install -e "apps/api[akshare,dev]"`（代理 7890 + 清华镜像 + 激进参数） | ✅ fastapi 0.141.1 / uvicorn 0.52.4 / httpx 0.28.1 |
| `.venv\Scripts\python -m pytest apps/api` | ✅ **73 passed, 0 failed**（1.25s，离线；smoke 默认跳过） |
| 常驻服务 | 未启动（仅 TestClient 验证，符合要求） |

## 安装依赖（本轮新增，仅 venv 内）

fastapi、uvicorn（运行时）；httpx（dev，测试用）。未修改系统 Python / 全局配置。

## 已知问题

1. 仅 Fake 行情 API：真实行情（AKShare 接入）、持仓/交易接口、APScheduler 均属 Phase 2B+，未实现。
2. StarletteDeprecationWarning（TestClient 使用 httpx 的提示）来自 fastapi/starlette 上游，非本项目代码，不影响测试。
3. `market_data_points` 唯一约束含 quote_time（防重复设计，Phase 1 遗留说明）；SQLite 存储实现说明（ExactDecimal/UTCDateTime）见 DECISIONS D-015。
4. 本机网络：pip 需代理 7890 + 清华镜像 + `--timeout 10 --retries 30`；git 推送需 danger-full-access（沙箱限制，GCM 凭据已缓存）。
5. 真实持仓仍未录入（清单在 gitignore 的 data/private/README.md）。

## 环境要求

- Python 3.11.9 + `.venv`；数据层命令见 README；API 启动命令见 MASTER_PLAN §12.2。
- 数据库默认 `storage/db/ashare_review.db`（gitignore）；本轮 API 不读写数据库。
- 未获访问权限：TradingView、通达信（不得假设可用）。

## 下一位 AI 的明确起点

1. **先阅读**：AGENTS.md → MASTER_PLAN.md → PROJECT_STATE.md → DECISIONS.md → TASKS.md → HANDOFF.md（本文件）。
2. **等待用户评审 Phase 1 + Phase 2A**；用户决定分支合入 main 的时机（当前 `feat/phase-1-data-layer` 与 `feat/phase-2a-api-skeleton` 均未合并）。
3. 评审要点：73 项离线测试 + smoke 3 项 + 审查 ZIP（Phase1：`D:\A-Share-Review-Phase1-review.zip`；Phase2A：`D:\A-Share-Review-Phase2A-review.zip`）。
4. 合入后进入 Phase 2B（真实行情接口 AKShare、持仓/交易接口、APScheduler）；动手前先更新 MASTER_PLAN/DECISIONS/TASKS 登记设计。
5. 操作纪律：不读取/导出 GCM 凭据；不修改全局 Git/代理/证书配置；pip 按上文代理参数；测试默认离线；不合并 main、不 force push、不重写历史。
