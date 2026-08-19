# DECISIONS.md — 关键决策记录

> 记录影响架构或方向的关键决策：日期、决策内容、理由、状态。新决策必须先在此登记，再在 MASTER_PLAN.md 落实。
> 最后更新：2026-08-19

## D-001 本地优先架构

- **日期**：2026-08-19
- **决策**：所有数据、数据库、配置保存在本机；工具可离线运行。
- **理由**：持仓与资金行为属敏感数据；本地优先可避免第三方存储泄露风险，也便于无网络时复盘。
- **状态**：✅ 已采纳（Phase 0 固化于 MASTER_PLAN.md）

## D-002 技术栈

- **日期**：2026-08-19
- **决策**：前端 React + TypeScript + Vite + ECharts；后端 Python + FastAPI；数据库 SQLite；数据处理 Pandas；定时任务 APScheduler。
- **理由**：前后端类型共享、图表能力强、单文件数据库零运维、Pandas 适合行情数据处理、APScheduler 轻量易用。
- **状态**：✅ 已采纳

## D-003 统一数据源适配层

- **日期**：2026-08-19
- **决策**：建立统一适配器接口，先后接入 AKShare、Tushare、通达信本地导出及其他合法数据源。
- **理由**：单一数据源有停摆/限流风险；统一接口使切换数据源不改变上层逻辑，并为双源校验提供基础。
- **状态**：✅ 已采纳（Phase 1 落代码）

## D-004 大模型仅作辅助解读

- **日期**：2026-08-19
- **决策**：大模型适配层支持 DeepSeek / OpenAI / Ollama，但数值计算、成本计算和交易规则必须使用确定性代码。
- **理由**：大模型输出不可用于精确计算；LLM 幻觉会直接破坏"数据准确性最高优先级"。
- **状态**：✅ 已采纳

## D-005 数据准确性为最高优先级

- **日期**：2026-08-19
- **决策**：行情记录强制全字段（symbol/market/trade_date/quote_time/fetched_at/source/price_type/adjustment/is_delayed/raw_value/normalized_value）；关键收盘数据双源校验，冲突标记异常；缺失显式显示；页面显示来源与截至时间；适配器配套质量测试。
- **理由**：复盘、成本、回测全部依赖行情数据；错误数据会传导为错误结论与决策。
- **状态**：✅ 已采纳（AGENTS.md + docs/data-sources/data-quality.md 固化）

## D-006 交易制度按证券代码配置

- **日期**：2026-08-19
- **决策**：A股股票默认 T+1；ETF 交易制度（T+0/T+1）按证券代码配置；做T辅助区分底仓与机动仓。
- **理由**：做T可用数量计算依赖准确的交易制度；ETF 存在 T+0 品种，不能一刀切。
- **状态**：✅ 已采纳

## D-007 "负成本"语义约束

- **日期**：2026-08-19
- **决策**："负成本"仅表示累计已实现收益超过剩余持仓账面成本，输出必须伴随风险提示（仍然存在市场风险）。
- **理由**：避免用户将"负成本"误解为无风险。
- **状态**：✅ 已采纳

## D-008 隐私红线

- **日期**：2026-08-19
- **决策**：不自动登录券商、不保存券商密码；不采集短信验证码与交易密钥；真实持仓只允许进入 data/private/（gitignore）；券商导出原件不入库。
- **理由**：工具定位是数据、复盘、预警、计划；保存凭证会引入巨大安全风险。
- **状态**：✅ 已采纳

## D-009 无交割单也能运行

- **日期**：2026-08-19
- **决策**：持仓与交易记录支持手工录入 + CSV 导入 + 通达信导出导入，不依赖券商交割单。
- **理由**：降低使用门槛，用户当前没有脱敏后的券商交割单。
- **状态**：✅ 已采纳

## D-010 金额精度方案（Decimal/NUMERIC）

- **日期**：2026-08-19
- **决策**：涉及价格、成本、费用的字段使用 `NUMERIC(18,6)` 存储，数量使用 `NUMERIC(18,4)`；Python 侧一律 `decimal.Decimal` 计算，禁止用 float 参与金额/价格计算。展示精度按 instrument_trade_rules.price_precision 配置（A股 0.01，ETF 0.001 等）。
- **理由**：float 二进制误差会污染成本、回测与做T计算；"数据准确性最高优先级"要求确定性的十进制运算。
- **状态**：✅ 已采纳（Phase 1 落地，见 D-015 的 SQLite 实现说明）

## D-011 时间处理统一方案

- **日期**：2026-08-19
- **决策**：数据库存储 **UTC（timezone-aware DateTime）**；`trade_date` 为对应市场本地交易日（date 类型，无时区歧义）；所有展示按 Asia/Shanghai 换算；禁止存储无时区含义的模糊时间（naive datetime）。
- **理由**：跨市场（A股/港股）与定时任务需要统一时间基准；naive 时间会在夏令时/时区换算中产生歧义。
- **状态**：✅ 已采纳（Phase 1 落地，timeutils 提供 to_utc / as_shanghai / market_date）

## D-012 双源冲突阈值

- **日期**：2026-08-19
- **决策**：双源价格冲突判定默认：相对偏差 > 0.1%（0.001）**且**绝对差 > 0.0001 即判冲突：`|a-b| > max(abs_threshold, rel_threshold * max(|a|,|b|))`。阈值可在 config 中覆盖；测试覆盖临界值与临界外。
- **理由**：收盘价双源校验需要可配置、可测试的确定性阈值；单一相对阈值对低价品种（如 ETF 0.3x 元）过松。
- **状态**：✅ 已采纳（Phase 1 落地）

## D-013 行情唯一性与词汇

- **日期**：2026-08-19
- **决策**：market_data_points 唯一约束 = (symbol, market, trade_date, quote_time, source, price_type, adjustment, is_delayed)；`price_type` 词汇：open/high/low/close/prev_close/last/volume/amount；`adjustment`：none/qfq/hfq；不同复权方式数据禁止混算。
- **理由**：同一行情点重复抓取不应产生重复行；词汇受控避免脏数据。
- **状态**：✅ 已采纳（Phase 1 落地）

## D-014 适配器设计约束

- **日期**：2026-08-19
- **决策**：AKShare 适配器 lazy import（未安装时抛明确错误）；akshare 列为 optional extra（`[akshare]`）；上游字段缺失/改名必须抛 `AdapterFieldError`，禁止静默容忍；输出必须通过 Pydantic 模型校验；不写死 API Key/代理/Cookie。
- **理由**：离线测试不依赖 akshare 安装；上游字段变化必须显式暴露，符合"字段变化测试"铁律。
- **状态**：✅ 已采纳（Phase 1 落地）

## D-015 SQLite 存储实现说明（ExactDecimal / UTCDateTime）

- **日期**：2026-08-19
- **决策**：SQLite 无原生 DECIMAL 且 `DateTime(timezone=True)` 不保留时区（实测读回 naive）。因此自定义两个类型装饰器（`ashare_review.db.types`）：
  - `ExactDecimal(p, s)`：写入时 Decimal → 定长 scale 位小数字符串（如 `0.649000`）存 TEXT；读取时还原 Decimal。DDL 语义保持 `NUMERIC(p, s)`（非 SQLite 方言用真实 NUMERIC）。
  - `UTCDateTime`：写入时 aware datetime → UTC ISO 字符串（带 `+00:00` 偏移）存 TEXT；读取时还原为 aware UTC datetime。naive 输入按 Asia/Shanghai 补时区（防御）。
  - 两者直接覆写 `bind_processor`/`result_processor`，不依赖 TypeDecorator 默认 impl 处理器链（该链经 Numeric 的 DecimalResultProcessor 会丢尾零）。
- **理由**：数据准确性最高优先级要求跨方言可移植的确定性格局；实测暴露的精度/时区丢失必须由类型层兜住。
- **状态**：✅ 已采纳（Phase 1 落地，迁移 `d68db143309f`）

## 待决策（Phase 1 前需要）

- ~~数据源启用顺序与默认主/备数据源~~ → ✅ 已定：AKShare 为主（Phase 1 首个实现），Tushare 为备（后续 Phase 接入）。
- ~~SQLite schema 的具体表结构与字段类型~~ → ✅ 已定：见 MASTER_PLAN.md §11.2/§11.3 与本文件 D-010~D-013。
