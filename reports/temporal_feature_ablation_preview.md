# Temporal-control feature ablation preview

This report tests which feature families carry the same-location temporal-control
signal. Each feature family is evaluated with leave-one-incident-out validation
over the same temporal-control rows.

## Results

| feature_family | samples | positives | ROC-AUC | PR-AUC | Recall@Top20% | Recall@Top50% |
|---|---:|---:|---:|---:|---:|---:|
| all | 16 | 4 | 0.916667 | 0.770833 | 0.750 | 1.000 |
| latest_weather | 16 | 4 | 0.687500 | 0.534659 | 0.250 | 0.750 |
| rainfall_windows | 16 | 4 | 0.916667 | 0.770833 | 0.750 | 1.000 |
| dry_spell_memory | 16 | 4 | 0.729167 | 0.565909 | 0.250 | 0.750 |
| rainfall_and_dry_spell | 16 | 4 | 0.916667 | 0.816667 | 0.500 | 1.000 |

## Interpretation guide

- `latest_weather` tests temperature, humidity and wind near the target time.
- `rainfall_windows` tests antecedent rainfall totals only.
- `dry_spell_memory` tests days-since-rain style temporal memory only.
- `rainfall_and_dry_spell` combines rainfall totals with dry-spell memory.
- `all` uses the full current tabular weather/dryness feature set.

These are tiny diagnostic ablations, not stable feature-importance claims.
