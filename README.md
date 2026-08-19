# A-Share-Review

本地优先的 A股 / 港股 / ETF 自动复盘、持仓分析、做T辅助、优质公司长期跟踪与资金行为研判工具。

> **定位**：只提供数据、复盘、预警和计划。
> **红线**：不自动登录券商、不保存券商密码、不自动下单。

## 设计原则

1. **本地优先**：数据、数据库、配置全部留在本机，不依赖云端服务即可运行。
2. **数据准确性是最高优先级**：双源校验、来源与时间戳全量标注、缺失即显缺失，绝不用缓存伪装当天数据。
3. **确定性计算**：数值计算、成本计算和交易规则一律使用确定性代码；大模型只做辅助解读，不参与计算。
4. **隐私安全**：券商密码、短信验证码、交易密钥一律不采集、不读取、不保存。

## 核心模块

| # | 模块 | 内容 |
| --- | --- | --- |
| 1 | 每日市场复盘 | 指数、涨跌家数、成交额、行业主题、ETF强弱、重要消息、持仓贡献、次日观察条件 |
| 2 | 持仓与交易记录 | 手工录入、CSV导入、通达信导出导入；无券商交割单也能运行 |
| 3 | 做T辅助 | 底仓与机动仓、可用数量、手续费、滑点、调整成本、交易制度（A股默认T+1，ETF按证券代码配置） |
| 4 | 优质公司长期跟踪 | 基本面、估值、分红、相对强弱、回撤、重要事件 |
| 5 | 资金行为研判 | 量价、相对强弱、异常成交、融资融券、大宗交易、股东变化等证据，输出置信度与反证 |
| 6 | 回测与风险 | 收益率、最大回撤、胜率、盈亏比、费用、滑点、组合集中度 |

> 说明：模块3中"负成本"仅表示累计已实现收益超过剩余持仓账面成本，**仍然存在市场风险**；资金行为研判输出的是证据与置信度，不声称能够看穿真实"主力意图"。

## 技术方案

| 层 | 选型 |
| --- | --- |
| 前端 | React + TypeScript + Vite + ECharts |
| 后端 | Python + FastAPI |
| 数据库 | SQLite |
| 数据处理 | Pandas |
| 定时任务 | APScheduler |
| 数据源适配层 | AKShare / Tushare / 通达信本地导出 / 其他合法数据源（统一接口） |
| 大模型适配层 | DeepSeek / OpenAI / Ollama（仅辅助解读） |

完整技术方案见 [MASTER_PLAN.md](MASTER_PLAN.md)。

## 目录结构

```
D:\A-Share-Review\
├── apps\             # 前端 web（React+Vite）与后端 api（FastAPI）
├── packages\shared   # 前后端共享定义（字段、枚举、校验）
├── config\           # 运行配置（不进版本库的密钥走 .env）
├── data\             # raw 原始数据 / processed 处理后 / imports 导入区 / exports 导出 / private 私有持仓（忽略）
├── docs\             # architecture 架构 / data-sources 数据源 / review-rules 复盘规则 / handoff 交接
├── scripts\          # 运维与一次性脚本
├── storage\          # db 数据库 / cache 缓存 / logs 日志（均忽略）
└── tests\            # frontend / backend / data 测试
```

> 私有持仓 CSV 的通用格式说明（字段 + 虚拟示例）见 [docs/private-data-format.md](docs/private-data-format.md)；真实持仓只存放于被忽略的 `data/private/`，绝不入库。

## 文档索引（AI 交接制度）

任何 AI 修改本项目前，**必须依次阅读**：

1. [AGENTS.md](AGENTS.md)
2. [MASTER_PLAN.md](MASTER_PLAN.md)
3. [PROJECT_STATE.md](PROJECT_STATE.md)
4. [DECISIONS.md](DECISIONS.md)
5. [TASKS.md](TASKS.md)
6. [HANDOFF.md](HANDOFF.md)

每轮工作结束，必须同步更新 `PROJECT_STATE.md`、`TASKS.md`、`CHANGELOG.md`、`HANDOFF.md`。

## 当前状态

- **Phase 0（项目规划与基础目录）已完成**（2026-08-19）。
- 未安装任何依赖，未生成业务实现；等待用户确认后进入 Phase 1。
- 详见 [PROJECT_STATE.md](PROJECT_STATE.md)。
