# Action / Position Proxy Report

- sampled leaders: 210
- leader_top_k param: 260

## Proxy Definitions
- action_intensity = log1p(fill_count) * log1p(symbol_count)
- position_turnover_proxy = log1p(avg_abs_fill_size) * log1p(fill_count)
- execution_consistency_proxy = active_day_count / active_span_days

## Coverage
- leaders with non-empty fills: 169
- total sampled fills: 151730

## Notes
- This is proxy-level analysis from public fills, not full private position ledger.
- API-side pagination/retention limits may cap historical depth for some leaders.