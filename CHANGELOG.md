# CHANGELOG.md — 变更记录

> 只记录实际发生的变更（不是计划）。格式：日期 | 变更 | 涉及文件/范围。
> 最后更新：2026-08-19

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
