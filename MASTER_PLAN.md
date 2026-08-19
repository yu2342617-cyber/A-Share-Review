# MASTER_PLAN.md — A-Share-Review 总体技术方案

> 本文档是本项目的技术权威来源。任何实现决策必须先与本文档保持一致；不一致时，先改本文档并记录到 DECISIONS.md，再动代码。
> 最后更新：2026-08-19（Phase 0）

## 1. 项目定位

本地优先的 A股 / 港股 / ETF 自动复盘、持仓分析、做T辅助、优质公司长期跟踪与资金行为研判工具。

- **提供**：数据、复盘、预警、计划。
- **不提供**：自动登录券商、保存券商密码、自动下单。

## 2. 非目标（明确不做）

- 不接入任何券商交易接口，不做自动下单。
- 不采集、不存储券商密码 / 短信验证码 / 交易密钥。
- 不以任何形式承诺"预测主力意图"或保证收益。
- 不把搜索引擎摘要当作精确实时价或收盘价。

## 3. 技术选型

| 层 | 选型 | 说明 |
| --- | --- | --- |
| 前端 | React + TypeScript + Vite + ECharts | SPA，本地运行；ECharts 负责行情图表 |
| 后端 | Python + FastAPI | REST API + 后台任务 |
| 数据库 | SQLite | 单文件本地库 `storage/db/ashare_review.db`，零运维 |
| 数据处理 | Pandas | 行情清洗、指标计算、回测 |
| 定时任务 | APScheduler | 交易日定时抓取与复盘任务，支持 Asia/Shanghai 时区 |
| 数据源适配层 | AKShare / Tushare / 通达信本地导出 / 其他合法数据源 | 统一适配器接口，见 §5 |
| 大模型适配层 | DeepSeek / OpenAI / Ollama | 仅辅助解读，见 §6 |
| 测试 | pytest（后端/数据）、Vitest（前端） | 数据适配器必须配套测试，见 §8 |

## 4. 总体架构与目录

```
D:\A-Share-Review\
├── apps\web          # 前端：React + TS + Vite + ECharts
├── apps\api          # 后端：FastAPI 应用、路由、APScheduler 任务
├── packages\shared   # 前后端共享：symbol/market/price_type 等枚举与校验（单一事实来源）
├── config\           # 运行配置（默认值 + .env 覆盖）
├── data\
│   ├── raw\          # 数据源原始落盘（下载原文，不加工）
│   ├── processed\    # 清洗/标准化后的中间数据
│   ├── imports\      # 用户导入区（CSV、通达信导出）；券商导出原件在此落地
│   ├── exports\      # 工具生成的导出结果（复盘报告、CSV 等）
│   └── private\      # 私有持仓数据（被 gitignore，绝不可提交）
├── docs\
│   ├── architecture\ # 架构设计
│   ├── data-sources\ # 数据源说明与数据质量规范
│   ├── review-rules\ # 复盘/做T/研判规则定义
│   └── handoff\      # 交接记录归档
├── scripts\          # 运维与一次性脚本
├── storage\
│   ├── db\           # SQLite 文件（gitignore）
│   ├── cache\        # 缓存（gitignore）
│   └── logs\         # 日志（gitignore）
└── tests\
    ├── frontend\     # 前端测试
    ├── backend\      # 后端/API 测试
    └── data\         # 数据适配器与数据质量测试
```

## 5. 数据层设计（数据准确性最高优先级）

### 5.1 统一行情记录字段（每条行情记录必须包含）

```
symbol           证券代码（含后缀，如 600519.SH / 00700.HK）
market           市场（SH / SZ / HK / ...）
trade_date       交易日（YYYY-MM-DD）
quote_time       报价/行情时间
fetched_at       抓取入库时间（本地 UTC+8）
source           数据来源（akshare / tushare / tdximp / manual_verified / ...）
price_type       价格类型（open / high / low / close / prev_close / ...）
adjustment       复权（none 不复权 / qfq 前复权 / hfq 后复权）
is_delayed       是否延时行情（0/1）
raw_value        原始值（适配器原样返回）
normalized_value 标准化后的数值（统一单位、去异常）
```

### 5.2 数据准确性铁律（同时写入 AGENTS.md 与 docs/data-sources/data-quality.md）

1. 禁止把搜索引擎摘要当作精确实时价或收盘价。
2. 每条行情记录必须带齐 §5.1 的全部字段，缺一不可。
3. 关键收盘数据尽量进行双源校验；来源冲突时标记异常，不输出确定性结论。
4. 用户通过通达信或券商终端人工确认的价格记录标记为 `manual_verified`。
5. 数据缺失时明确显示缺失，不能用历史缓存伪装成当天数据。
6. 所有行情页面必须显示数据来源和截至时间。
7. 为数据适配器编写延迟、空值、字段变化和来源冲突测试。

### 5.3 数据源适配层

统一接口（示意，Phase 1 落代码）：

```
interface DataSourceAdapter {
  id: str                    # 'akshare' | 'tushare' | 'tdximp' | ...
  fetch_quote(...)           # 实时/收盘报价
  fetch_daily_history(...)   # 历史日线
  fetch_etf_list / fetch_index_list / fetch_financials / ...
  meta()                     # 返回延迟级别、可用范围、限流说明
}
```

- 每个适配器独立实现、独立测试；切换数据源不改变上层接口。
- 适配器返回原始值（`raw_value`）+ 标准化值（`normalized_value`），异常与空值显式表达。
- 双源校验：对关键收盘数据（指数收盘、重点持仓收盘）执行交叉比对，冲突即标记异常。

### 5.4 通达信导出导入

- 支持通达信导出的行情/自选股/交割单类文件，统一落入 `data/imports/`。
- 导出原件属于敏感文件，必须被 .gitignore 覆盖（见 .gitignore）。
- 解析适配器：`tdximp`，负责字段映射与编码处理，配套字段变化测试。

## 6. 大模型适配层（仅辅助解读）

- 支持 DeepSeek / OpenAI / Ollama，通过统一适配器接口接入，API Key 只放 `.env`（gitignore）。
- **硬性边界**：数值计算、成本计算、交易规则必须使用确定性代码，大模型输出不得进入计算链路。
- 大模型的合法用途：重要消息摘要、复盘文案生成、研判报告的辅助表达（基于确定性指标结果）。

## 7. 核心模块设计

### 7.1 每日市场复盘
- 指数（上证/深证/创业板/恒生等）、涨跌家数、两市/板块成交额、行业与主题强度、ETF 强弱榜、重要消息。
- 持仓贡献拆解：当日持仓涨跌对组合收益的贡献。
- 次日观察条件：基于规则生成（确定性），供用户人工确认。

### 7.2 持仓与交易记录
- 手工录入 + CSV 导入 + 通达信导出导入；**没有券商交割单也能运行**（手工记账优先）。
- 导入模板：`data/imports/positions.example.csv`（仅字段与虚拟示例）；私有持仓 CSV 通用格式见 `docs/private-data-format.md`；真实数据入 `data/private/`（gitignore）。
- 交易记录用于成本跟踪与做T辅助，不做自动下单依据。

### 7.3 做T辅助
- 底仓与机动仓分离、可用数量（T+1 规则）、手续费、滑点、调整成本。
- A股股票默认 T+1；ETF 交易制度按证券代码配置（可 T+0）。
- "负成本"仅表示累计已实现收益超过剩余持仓账面成本，**仍然存在市场风险**，界面必须展示风险提示。

### 7.4 优质公司长期跟踪
- 基本面（财务摘要）、估值（PE/PB/股息率）、分红记录、相对强弱、历史最大回撤、重要事件时间线。

### 7.5 资金行为研判
- 证据维度：量价、相对强弱、异常成交、融资融券、大宗交易、股东变化。
- 输出：证据列表 + 置信度 + 反证；明确声明不声称能够看穿真实"主力意图"。

### 7.6 回测与风险
- 指标：收益率、最大回撤、胜率、盈亏比；计入费用、滑点；组合集中度提示。

## 8. 测试策略

- `tests/data/`：数据适配器测试（延迟、空值、字段变化、来源冲突、双源校验）。
- `tests/backend/`：API 与计算逻辑测试（成本、T+1 规则、回测指标）。
- `tests/frontend/`：组件与页面测试。
- 数据质量测试是项目级硬门槛，适配器合入前必须通过。

## 9. 隐私与安全

- gitignore 覆盖：`data/private/`、`storage/db/`、`storage/cache/`、`storage/logs/`、`.env`、券商导出原件。
- 不得索要、读取或保存券商密码、短信验证码和交易密钥。
- 真实持仓只允许出现在 `data/private/`（gitignore），不得写入任何可提交文件；私有持仓通用格式见 `docs/private-data-format.md`（仅字段与虚拟示例）。

## 10. 阶段规划

| 阶段 | 内容 | 状态 |
| --- | --- | --- |
| Phase 0 | 项目规划与基础目录（本文档、AGENTS、交接制度、目录骨架） | ✅ 已完成（2026-08-19） |
| Phase 1 | 数据层：SQLite schema、数据源适配层骨架（AKShare 优先）、数据质量测试 | ✅ 实现完成（2026-08-19，待评审；分支 feat/phase-1-data-layer） |
| Phase 2 | 后端 API：FastAPI 基础、行情/持仓接口、APScheduler 定时任务 | ⏳ 待启动 |
| Phase 3 | 前端骨架：Vite + React + ECharts，行情看板 | ⏳ 待启动 |
| Phase 4 | 模块功能逐个落地（复盘 / 持仓 / 做T / 跟踪 / 研判 / 回测） | ⏳ 待启动 |
| Phase 5 | 预警与计划、导入导出闭环、全面测试与验收 | ⏳ 待启动 |

> 每个 Phase 的验收：先更新本文档与 PROJECT_STATE.md，再实现；实现后更新 TASKS.md / CHANGELOG.md / HANDOFF.md。

## 11. Phase 1 数据层设计（2026-08-19 登记）

### 11.1 技术栈与工程结构

- Python 3.11+；SQLAlchemy 2.x（Mapped/mapped_column 声明式）；Alembic 迁移；Pydantic 2.x 适配器输出校验；pytest 测试。
- 工程位于 `apps/api/`，src 布局：`apps/api/src/ashare_review/`，包名 `ashare_review`（editable 安装）。
- 模块职责分离：`config`（配置）、`db`（engine/session/时间工具）、`models`（ORM）、`repositories`（数据访问）、`adapters`（数据源）、`quality`（质量服务）。
- 本地虚拟环境 `.venv`（项目根，gitignore）；只装本轮必要依赖，不装 FastAPI/前端/Docker/LLM。

### 11.2 数据库（SQLite，文件在 storage/db，gitignore）

| 表 | 用途 | 关键点 |
| --- | --- | --- |
| instruments | 证券档案 | 代码/市场/名称/类型/币种/最小变动单位/交易状态；(symbol,market) 唯一 |
| instrument_trade_rules | 交易制度 | T+0/T+1、最小交易单位、价格精度、市场规则；**ETF 按证券代码配置** |
| market_data_points | 行情点 | 11 字段全量 + quality_status；唯一约束与索引见 §11.3 |
| source_fetch_runs | 抓取任务 | 来源/起止/状态/记录数/错误摘要/数据日期 |
| data_quality_issues | 质量问题 | 类型/严重度/来源/证券/交易日/证据/处理状态 |
| positions | 持仓 | 只建结构，不导入真实持仓 |
| trades | 交易 | 方向/数量/价格/费用/日期/结算规则 |
| companies | 公司档案 | 基础结构 |
| events | 事件 | 公告/新闻/政策/公司事件 + 来源与时间 |

- 价格/成本/费用：`NUMERIC(18,6)`；数量：`NUMERIC(18,4)`；计算一律 `decimal.Decimal`，禁用 float（见 DECISIONS.md D-010）。
- 时间：DB 存 **UTC（timezone-aware）**；`trade_date` 为市场本地交易日（date）；展示统一 Asia/Shanghai；禁止无时区含义的模糊时间（见 D-011）。

### 11.3 market_data_points 约束

- 唯一约束：(symbol, market, trade_date, quote_time, source, price_type, adjustment, is_delayed)。
- 索引：(symbol, market, trade_date)、(trade_date, price_type)、(source, fetched_at)、(quality_status)。
- `raw_value` 存原文（Text，可追溯）；`normalized_value` 存 NUMERIC 标准化值；`quality_status`：ok / suspect / conflict / missing。

### 11.4 数据源适配层（接口与实现）

- 接口 `DataSourceAdapter`（ABC）：`meta()`、`fetch_quote()`、`fetch_daily_history()`；输出经 Pydantic 模型校验（`QuoteTick`、`DailyBar`、`AdapterMeta`）。
- `FakeDataSourceAdapter`：完全离线、确定性，供测试。
- `AKShareDataSourceAdapter`：最小日线/收盘入口（A股 `stock_zh_a_hist`、ETF `fund_etf_hist_em`）；**lazy import** akshare（未安装时给出明确错误）；字段缺失/变化必须抛 `AdapterFieldError`；保存 raw 与 normalized；不使用搜索引擎摘要。
- 双源冲突阈值：相对 0.1%（0.001）且绝对 0.0001，可配置（见 D-012）。

### 11.5 数据质量服务（quality）

9 项检查：必填字段、空值、非法价格/数量、trade_date↔quote_time 一致性、延迟标记、上游字段变化、双源冲突、manual_verified 优先（保留冲突证据不删除）、stale/missing 缓存判定（禁止用旧缓存冒充当天）。问题写入 `data_quality_issues`。

### 11.6 测试策略（离线优先）

- 普通测试全部离线：Fake 适配器 + 本地 fixture + 临时 SQLite（内存/临时文件）。
- AKShare 联网测试标记 `smoke`，默认排除（`addopts = -m "not smoke"`）；网络失败不影响普通测试。
- 覆盖：模型字段完整性、Decimal 精度、DB 初始化与迁移、正常写入、重复约束、空值、延迟、字段变化、双源一致/冲突（含阈值临界值）、manual_verified 优先、stale 判定、Fake 离线、AKShare fixture 映射。
