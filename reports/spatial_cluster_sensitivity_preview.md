# Rough spatial-control cluster sensitivity preview

This report evaluates whether rough spatial-control performance is sensitive to
the two geographically and temporally close Cannock Chase positives flagged by
the incident independence audit. It reruns leave-one-incident-out evaluation
after dropping either member of the potential local cluster.

## Results

| scenario | excluded_group_ids | samples | positives | folds | ROC-AUC | PR-AUC | Recall |
|---|---|---:|---:|---:|---:|---:|---|
| all_model_ready | none | 30 | 5 | 5 | 0.608000 | 0.267451 | Top 10%: 0.000, Top 20%: 0.400, Top 50%: 0.600, Top 100%: 1.000 |
| drop_cannock_chase_30_july | cannock-chase-2026-08 | 24 | 4 | 4 | 0.575000 | 0.260073 | Top 10%: 0.250, Top 20%: 0.250, Top 50%: 0.500, Top 100%: 1.000 |
| drop_cannock_chase_5_august | cannock-chase-sherbrook-valley-2026-08 | 24 | 4 | 4 | 0.700000 | 0.371382 | Top 10%: 0.250, Top 20%: 0.500, Top 50%: 0.750, Top 100%: 1.000 |

## Interpretation

This sensitivity check applies to the rough regional-offset spatial controls.
It is intentionally separate from the temporal-control sensitivity report
because spatial controls answer a harder generalisation question.

If spatial metrics collapse when one local-cluster member is removed, the
current spatial signal should be treated as especially fragile. If metrics
remain similar, the rough spatial diagnostic is less dependent on the cluster,
but still weak because the controls are coarse and the positive count is tiny.
