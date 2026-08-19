# CHANGELOG.md — 变更记录

> 只记录实际发生的变更（不是计划）。格式：日期 | 变更 | 涉及文件/范围。
> 最后更新：2026-08-19

## 2026-08-19 — Phase 1：数据层（分支 feat/phase-1-data-layer，未合并）

### 新增
- `apps/api/` 数据层工程：pyproject.toml（src 布局，包 `ashare_review`）、alembic.ini、alembic/（env.py、script.py.mako、初始迁移 `d68db143309f`）
- `src/ashare_review/`：config.py、constants.py、cli.py（ashare-db-init）
  - db/：base、session、timeutils（UTC/Asia-Shanghai）、types（ExactDecimal / UTCDateTime）
  - models/：9 张业务表（instruments、instrument_trade_rules、market_data_points、source_fetch_runs、data_quality_issues、positions、trades、companies、events）
  - adapters/：DataSourceAdapter 接口（Pydantic 校验）+ FakeDataSourceAdapter + AKShareDataSourceAdapter（lazy import、字段变化报错）
  - quality/：QualityService（9 项检查、双源阈值可配置、manual_verified 优先、stale/missing 判定）
  - repositories/：MarketDataRepository、QualityRepository
- `apps/api/tests/`：14 个测试文件（模型/精度/迁移/仓库/质量/适配器/时间/smoke）
- `scripts/db-init.ps1`、`scripts/run-tests.ps1`
- README.md「数据层开发环境（Windows PowerShell）」章节

### 变更
- MASTER_PLAN.md §11（Phase 1 数据层设计）；DECISIONS.md D-010~D-015；PROJECT_STATE.md、TASKS.md、CHANGELOG.md（本文件）

### 测试
- 离线：64 passed, 0 failed（1.58s）；AKShare 联网 smoke：3 passed（可选，默认排除）

### 说明
- 未进入 Phase 2；未安装 FastAPI/前端/Docker/LLM 依赖；未合并 main、未 force push；数据库/缓存/日志/.venv 均未入库。

## 2026-08-19 — 收尾：用户网页确认仓库 Private

### 变更
- PROJECT_STATE.md / TASKS.md / HANDOFF.md：可见性状态改为「用户已在 GitHub 网页人工确认 Private」，Git/GitHub 环节标记完成
- 提交 `docs: confirm private GitHub repository` 并推送

### 说明
- 未进入 Phase 1；未安装依赖；未修改代理、证书或全局 Git 配置；未使用 gh CLI。

## 2026-08-19 — GitHub 首次推送完成（可见性待修正为 Private）

### 变更
- 用户手动创建仓库 https://github.com/yu2342617-cyber/A-Share-Review
- 添加 origin（HTTPS）并推送成功：`git push -u origin main`；远程默认分支 main；远程 main = `d35d122`（含两个 commit：`9ca8648` 初始化、`d35d122` 交接文档）
- 环境处理：本机 schannel TLS 故障导致直连失败，仓库级配置 `http.sslBackend=openssl` + `http(s).proxy=http://127.0.0.1:7890`（--local）后推送成功
- 已推送内容隐私核对 PASS（无 .env、无真实持仓、私有目录仅 .gitkeep、无密钥）
- ⚠️ 可见性复核：仓库当前为 **Public**，需用户在 GitHub 网页改为 Private（暂未修正）

### 说明
- 未进入 Phase 1，未安装项目依赖，未修改全局 Git 配置，未使用 gh。

## 2026-08-19 — Git 首次提交完成（GitHub 推送阻塞于 gh CLI 缺失）

### 变更
- 仓库级 Git 身份设置（用户提供，仅 --local）：`user.name=uwang`、`user.email=yu2342617@gmail.com`（global 配置未改动）
- 首次提交：`9ca8648 chore: initialize A-Share-Review phase 0`（31 文件，828 行）
- 分支改名为 `main`
- 检查 `gh --version`：**gh 未安装** → 按规则不擅自安装，推送步骤暂停，等待用户安装 gh 或手动创建 Private 仓库

### 说明
- 未进入 Phase 1，未安装项目依赖，未修改全局 Git 配置。

## 2026-08-19 — Git/GitHub 首次提交准备（未提交，阻塞于身份缺失）

### 检查（无文件内容变更）
- 工作目录确认、`git status --short` / `git status --ignored` 核对通过
- 待提交清单隐私核对通过（.env、数据库、缓存、日志、券商文件、运行数据、data/private 真实文件均被忽略）
- 18 个 .gitkeep 可提交性确认
- 仓库级 Git 身份检查：user.name 与 user.email 均缺失 → **阻塞**，用户选择自行配置，本轮未 commit、未创建仓库、未推送

### 变更
- PROJECT_STATE.md、TASKS.md 记录阻塞状态与解除方式（HANDOFF.md 同步更新）

## 2026-08-19 — Phase 0 修正（gitignore / 私有格式文档）

### 变更
- `.gitignore`：运行目录（data/raw、data/processed、data/exports、data/private、storage/db、storage/cache、storage/logs）改为"忽略实际内容、保留并允许提交 .gitkeep"（`目录/*` + `!目录/.gitkeep`）
- 新增 `data/private/.gitkeep`（私有真实数据仍被忽略）
- 新增 `docs/private-data-format.md`：私有持仓通用格式说明（仅字段 + 虚拟示例，无真实持仓）
- `data/private/README.md`：通用格式说明移至 docs/private-data-format.md，保留本地待录入清单（仍被忽略，未删除本地数据）
- README.md、MASTER_PLAN.md、PROJECT_STATE.md、TASKS.md、HANDOFF.md：私有数据格式引用统一指向 docs/private-data-format.md

### 说明
- 未安装依赖；未生成业务代码；未执行 git commit。

## 2026-08-19 — Phase 0：项目规划与基础目录

### 新增
- 创建根文档：README.md、MASTER_PLAN.md、AGENTS.md、PROJECT_STATE.md、DECISIONS.md、TASKS.md、CHANGELOG.md、HANDOFF.md
- 创建配置文件模板与忽略规则：.env.example、.gitignore
- 创建 20 个基础目录，空目录添加 .gitkeep
- 创建数据格式文件：data/imports/positions.example.csv、data/private/README.md、docs/data-sources/data-quality.md

### 变更
- 无（根目录初始为空，本轮全部为新增）

### 删除
- 无

### 说明
- 未安装任何依赖；未生成业务代码；未执行 git commit。
