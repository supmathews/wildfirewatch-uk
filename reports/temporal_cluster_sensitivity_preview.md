# Temporal-control cluster sensitivity preview

This report evaluates whether the temporal-control signal is sensitive to the
two geographically and temporally close Cannock Chase positives flagged by the
incident independence audit. It reruns leave-one-incident-out evaluation after
dropping either member of the potential local cluster.

## Results

| scenario | excluded_group_ids | samples | positives | folds | ROC-AUC | PR-AUC | Recall |
|---|---|---:|---:|---:|---:|---:|---|
| all_model_ready | none | 20 | 5 | 5 | 0.946667 | 0.852857 | Top 10%: 0.400, Top 20%: 0.600, Top 50%: 1.000, Top 100%: 1.000 |
| drop_cannock_chase_30_july | cannock-chase-2026-08 | 16 | 4 | 4 | 0.916667 | 0.770833 | Top 10%: 0.250, Top 20%: 0.750, Top 50%: 1.000, Top 100%: 1.000 |
| drop_cannock_chase_5_august | cannock-chase-sherbrook-valley-2026-08 | 16 | 4 | 4 | 0.854167 | 0.667857 | Top 10%: 0.250, Top 20%: 0.500, Top 50%: 1.000, Top 100%: 1.000 |

## Interpretation

If metrics collapse when one local-cluster member is removed, the current signal
is likely too dependent on that cluster. If metrics remain directionally strong,
that is useful evidence that the temporal weather/dryness signal is not solely
carried by the paired Cannock Chase examples.

This remains a tiny diagnostic test: removing one incident leaves only four
positives, so the scenario metrics are intentionally treated as sensitivity
checks, not stable performance estimates.
