"""受控词汇常量（单一事实来源，与 DECISIONS.md D-013 一致）。"""

from __future__ import annotations

# price_type 词汇（market_data_points.price_type）
PRICE_TYPES = ("open", "high", "low", "close", "prev_close", "last", "volume", "amount")

# adjustment 词汇（不复权 / 前复权 / 后复权）；不同复权数据禁止混算
ADJUSTMENTS = ("none", "qfq", "hfq")

# 质量状态（market_data_points.quality_status）
QUALITY_STATUS = ("ok", "suspect", "conflict", "missing")

# 质量问题严重程度（data_quality_issues.severity）
SEVERITIES = ("info", "warning", "error", "critical")

# 问题类型
ISSUE_TYPES = (
    "missing_required_field",
    "null_value",
    "invalid_price",
    "invalid_quantity",
    "trade_date_quote_time_mismatch",
    "delayed_marking_missing",
    "upstream_field_change",
    "dual_source_conflict",
    "manual_verified_override",
    "stale_data",
    "other",
)

# 交易周期（instrument_trade_rules.trade_cycle）
TRADE_CYCLES = ("T+0", "T+1")

# 证券类型
SECURITY_TYPES = ("stock", "etf", "fund", "index", "bond", "other")

# 交易状态
TRADE_STATUSES = ("active", "suspended", "delisted", "pending")

# 抓取运行状态（source_fetch_runs.status）
FETCH_STATUSES = ("running", "success", "partial", "failed")

# 事件类型（events.event_type）
EVENT_TYPES = ("announcement", "news", "policy", "corporate", "other")

# 质量问题处理状态
ISSUE_STATUSES = ("open", "acknowledged", "resolved")
