# PROJECT_STATE.md — 项目状态

> 每轮工作结束必须更新：当前阶段、已完成、进行中、下一步、已验证命令。
> 最后更新：2026-08-19（Phase 0）

## 当前阶段

**Phase 0：项目规划与基础目录（含 Phase 0 修正）—— 已完成，等待用户确认后进入 Phase 1。**

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

## 进行中

- **无。** Phase 0（含 Git/GitHub 收尾）全部完成，等待用户确认后进入 Phase 1。
  - Git/GitHub 收尾：首次提交 `9ca8648` 与后续交接文档提交均已推送至 `origin/main`；远程默认分支 `main`；**用户已在 GitHub 网页人工确认仓库可见性为 Private**（按用户指示，不再用 gh/未认证探测复验）。
  - 环境注记：本机 schannel TLS 栈故障导致 git/.NET/curl 直连 GitHub 失败；已在本仓库设置 `http.sslBackend=openssl` 与 `http(s).proxy=http://127.0.0.1:7890`（仓库级 --local）后推送成功。

## 下一步（等待用户确认后执行）

1. **Phase 1（数据层）**：SQLite schema 设计、数据源适配层骨架（AKShare 优先）、数据质量测试（tests/data/）。
2. 用户将在本地私有数据中录入真实持仓（私有数据通用格式见 docs/private-data-format.md；待录入清单见 data/private/README.md，该目录 gitignore、不入库）。
3. 用户确认后更新本文件与 MASTER_PLAN.md 的 Phase 1 规划。

## 已验证命令

| 命令 | 结果 |
| --- | --- |
| `git init`（D:\A-Share-Review） | 成功，空仓库初始化，未提交 |
| 目录创建（New-Item -Force） | 20 个目录全部创建成功 |
| 文件写入（UTF-8） | 全部成功，编码检查通过 |
| `git check-ignore`（Phase 0 修正复查） | 私有数据/运行目录内容被忽略、.gitkeep 不被忽略，全部符合预期 |
| 敏感信息搜索（Phase 0 修正） | 未发现非空密钥/密码/Token 内容 |

## 环境要求

- 当前未安装任何依赖（Phase 0 明确不安装）。
- 未来需要：Node.js（前端）、Python 3.11+（后端）、AKShare/Tushare（数据源，可选）。
- 已安装但未获访问权限：TradingView、通达信（不得假设已获得账户、本地文件或软件数据访问权限）。
