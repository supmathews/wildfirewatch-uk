# Temporal-control feature ablation preview

This report tests which feature families carry the same-location temporal-control
signal. Each feature family is evaluated with leave-one-incident-out validation
over the same temporal-control rows.

## Results

| feature_family | samples | positives | ROC-AUC | PR-AUC | Recall@Top20% | Recall@Top50% |
|---|---:|---:|---:|---:|---:|---:|
| all | 20 | 5 | 0.946667 | 0.852857 | 0.600 | 1.000 |
| latest_weather | 20 | 5 | 0.720000 | 0.522637 | 0.200 | 0.800 |
| rainfall_windows | 20 | 5 | 0.946667 | 0.852857 | 0.600 | 1.000 |
| dry_spell_memory | 20 | 5 | 0.773333 | 0.657143 | 0.400 | 0.800 |
| rainfall_and_dry_spell | 20 | 5 | 0.960000 | 0.902857 | 0.600 | 1.000 |

## Interpretation guide

- `latest_weather` tests temperature, humidity and wind near the target time.
- `rainfall_windows` tests antecedent rainfall totals only.
- `dry_spell_memory` tests days-since-rain style temporal memory only.
- `rainfall_and_dry_spell` combines rainfall totals with dry-spell memory.
- `all` uses the full current tabular weather/dryness feature set.

These are tiny diagnostic ablations, not stable feature-importance claims.
