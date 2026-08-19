# TASKS.md — 任务清单与验收

> 每轮工作结束必须更新任务状态与验收结果。
> 状态标记：⏳ 待办 / 🔄 进行中 / ✅ 已完成 / ❌ 阻塞
> 最后更新：2026-08-19

## Phase 0：项目规划与基础目录

| 任务 | 状态 | 验收结果 |
| --- | --- | --- |
| 确认/切换工作目录为 D:\A-Share-Review | ✅ 已完成 | `Get-Location` 返回 D:\A-Share-Review |
| 检查现有文件，保留用户已有内容 | ✅ 已完成 | 根目录初始为空，无用户文件需要保留 |
| git init（不提交、不改全局配置） | ✅ 已完成 | 空仓库初始化成功，未执行 commit |
| 创建根文件（README / MASTER_PLAN / AGENTS / PROJECT_STATE / DECISIONS / TASKS / CHANGELOG / HANDOFF / .env.example / .gitignore） | ✅ 已完成 | 10 个文件全部创建 |
| 创建目录结构（apps / packages / config / data / docs / scripts / storage / tests） | ✅ 已完成 | 20 个目录全部创建 |
| 空目录添加 .gitkeep | ✅ 已完成 | 空目录均有 .gitkeep（含 gitignore 目录在内，本地结构完整） |
| MASTER_PLAN.md 写入技术方案 | ✅ 已完成 | 技术栈、适配层、核心模块、阶段规划齐全 |
| AGENTS.md + data-quality.md 写入数据准确性铁律 | ✅ 已完成 | 7 条铁律 + 行情记录字段完整落盘 |
| 隐私安全与 .gitignore 覆盖 | ✅ 已完成 | data/private、storage/db、storage/cache、storage/logs、.env、券商导出原件均被忽略，`git check-ignore` 验证通过 |
| positions.example.csv（仅字段+虚拟示例） | ✅ 已完成 | 3 行虚拟示例（A股/ETF/港股各一），无真实持仓 |
| data/private/README.md 私有说明（本地） | ✅ 已完成 | 待录入清单存于 gitignore 目录；通用格式移至 docs/private-data-format.md |
| docs/private-data-format.md 通用格式文档 | ✅ 已完成 | 仅字段说明 + 虚拟示例，无真实持仓 |
| Markdown 一致性 + UTF-8 检查 | ✅ 已完成 | 见下方检查项 |

## Phase 0 修正（2026-08-19）

| 任务 | 状态 | 验收结果 |
| --- | --- | --- |
| .gitignore：运行目录忽略内容、保留 .gitkeep（data/raw、data/processed、data/exports、data/private、storage/db、storage/cache、storage/logs） | ✅ 已完成 | `git check-ignore` 验证：普通文件被忽略、.gitkeep 不被忽略 |
| 创建 data/private/.gitkeep | ✅ 已完成 | 文件已创建，允许提交 |
| 通用格式整理到 docs/private-data-format.md | ✅ 已完成 | 仅字段 + 虚拟示例，无真实持仓 |
| data/private/README.md 保留本地信息且继续被忽略 | ✅ 已完成 | `git check-ignore` 命中，未删除本地数据 |
| 各文档引用统一指向 docs/private-data-format.md | ✅ 已完成 | README/MASTER_PLAN/PROJECT_STATE/TASKS/HANDOFF 一致 |
| 敏感信息搜索（API Key/密码/Token） | ✅ 已完成 | 未发现非空密钥内容（详见 HANDOFF） |

**Phase 0（含修正）验收结论：✅ 通过。** 未安装依赖，未生成业务实现代码，未执行 git commit。

## Git 首次提交与 GitHub 推送（2026-08-19）

| 任务 | 状态 | 验收结果 |
| --- | --- | --- |
| 工作目录确认 | ✅ 已完成 | D:\A-Share-Review |
| git status --short / --ignored 检查 | ✅ 已完成 | 仅 31 个预期候选文件；私有内容全部被忽略 |
| 待提交清单隐私核对（.env/数据库/缓存/日志/券商文件/运行数据/真实持仓） | ✅ 已完成 | 全部被忽略，候选无私有内容 |
| .gitkeep 可提交性 | ✅ 已完成 | 18 个 .gitkeep 全部可提交 |
| 仓库级 Git 身份设置 | ✅ 已完成 | 用户提供 uwang / yu2342617@gmail.com，写入 --local（未改 global） |
| git add . 与暂存区核对 | ✅ 已完成 | 31 文件暂存，PASS 无私有/敏感文件 |
| git commit | ✅ 已完成 | `9ca8648 chore: initialize A-Share-Review phase 0`（31 文件，828 行） |
| git branch -M main | ✅ 已完成 | 当前分支 main |
| gh CLI 检查 | ❌ 阻塞（改用方案A） | `gh` 未安装；用户改为手动建仓，走方案A推送 |
| 添加 origin 并推送 | ✅ 已完成 | origin=https://github.com/yu2342617-cyber/A-Share-Review.git；`git push -u origin main` 成功（GCM 授权后） |
| 推送后复核（远程 main、内容一致性） | ✅ 已完成 | 远程默认分支 main；远程 main = d35d122 = 本地 HEAD；已推送内容隐私核对 PASS |
| 仓库可见性为 Private | ✅ 已完成 | **用户已在 GitHub 网页人工确认 Private**（按用户指示，不再用 gh/未认证探测复验） |

**说明**：
- 环境注记：本机 schannel TLS 栈故障（git/.NET/curl 直连 GitHub 失败）；仓库级已配置 `http.sslBackend=openssl` + `http(s).proxy=http://127.0.0.1:7890`（--local）。
- 可见性：用户已在 GitHub 网页人工确认 **Private**。Git/GitHub 环节完成，无阻塞。

## Phase 1：数据层（2026-08-19，实现完成待评审，分支 feat/phase-1-data-layer）

| 任务 | 状态 | 验收结果 |
| --- | --- | --- |
| 设计登记（MASTER_PLAN §11、DECISIONS D-010~D-015） | ✅ 已完成 | 精度/时间/阈值/唯一约束/适配器约束/SQLite 实现说明 |
| 工程骨架：apps/api（pyproject、src 布局、.venv、依赖安装） | ✅ 已完成 | sqlalchemy 2.0.52 / alembic 1.19.1 / pydantic 2.13.4 / pytest 9.1.1 / akshare 1.18.92 |
| SQLAlchemy 2.x 模型（9 张业务表） | ✅ 已完成 | 唯一约束、索引、ExactDecimal/UTCDateTime；迁移 d68db143309f 建 10 表 |
| timeutils（UTC 存储 + Asia/Shanghai 展示 + market_date） | ✅ 已完成 | naive 时间在 Pydantic 层拒绝（测试覆盖） |
| 数据源适配器：接口 + Fake（离线确定性） | ✅ 已完成 | meta/fetch_quote/fetch_daily_history；Pydantic 校验 |
| AKShare 适配器最小实现 | ✅ 已完成 | A股股票/ETF 日线；lazy import；字段缺失/改名抛 AdapterFieldError；保存 raw+normalized |
| 数据质量服务（9 项检查 + 阈值可配置） | ✅ 已完成 | 双源冲突默认 rel 0.001/abs 0.0001，临界值测试覆盖 |
| repositories（行情读写、问题记录） | ✅ 已完成 | 正常写入/重复约束/查询过滤测试通过 |
| Alembic（ini/env/初始迁移） | ✅ 已完成 | upgrade head / downgrade base / 再 upgrade 往返通过 |
| 离线测试套件 | ✅ 已完成 | **64 passed, 0 failed**（1.58s） |
| AKShare 联网 smoke（可选） | ✅ 已完成 | **3 passed**（真实联网验证，默认排除） |
| 隐私检查 | ✅ 已完成 | 无 .env/.venv/db/缓存/密钥/真实持仓代码/运行数据 |
| README 更新（PowerShell 命令）+ 六文档更新 | 🔄 进行中 | 提交推送分支（不合并 main、不 force push） |
| 生成 git archive 安全审查 ZIP | ⏳ 待办 | D:\A-Share-Review-Phase1-review.zip |

**Phase 1 验收结论（待用户确认）：** 离线测试 64/64 通过，AKShare smoke 3/3 通过；数据库初始化与迁移验证通过；隐私检查通过。

## Phase 2A：FastAPI 最小骨架 + Fake 行情接口（2026-08-19，实现完成，分支 feat/phase-2a-api-skeleton）

| 任务 | 状态 | 验收结果 |
| --- | --- | --- |
| 依赖：pyproject 增加 fastapi/uvicorn，dev 增加 httpx | ✅ 已完成 | venv 安装成功（fastapi 0.141.1 / uvicorn 0.52.4 / httpx 0.28.1） |
| api 包结构（app.py + routes/health、market） | ✅ 已完成 | `create_app()` + 模块级 `app` |
| GET /health | ✅ 已完成 | 200 + 固定字段 status/project/phase |
| GET /api/v1/market/meta | ✅ 已完成 | 返回 FakeDataSourceAdapter.meta()，id=fake，明确合成数据 |
| GET /api/v1/market/quote | ✅ 已完成 | Fake fetch_quote；Pydantic 结构化；source=fake |
| GET /api/v1/market/daily | ✅ 已完成 | Fake fetch_daily_history；倒置日期 422；>366 天 422 |
| API 离线测试（9 项） | ✅ 已完成 | health/meta/quote/daily/倒置/超区间/确定性/缺参/366 边界 |
| 完整测试回归 | ✅ 已完成 | **73 passed, 0 failed**（64 原有 + 9 新增；smoke 默认跳过） |
| 不启动常驻服务、不访问网络、不写数据库 | ✅ 已完成 | 仅测试验证（TestClient） |

**Phase 2A 结论：✅ 通过。** 当前只有 Fake 行情 API；没有接入真实行情；没有启动 APScheduler；没有进入前端开发；未合并 main、未 force push。

## Phase 2B+（规划中，待评审后启动）
