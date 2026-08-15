# Temporal-control leave-one-incident-out baseline preview

This report uses same-location temporal controls: each incident location is compared with
weather/dryness at prior non-fire reference dates. Each fold holds out one incident group
and trains on the remaining groups.

This answers a narrower question than spatial controls: did each location look more risky
near ignition than it did at earlier reference dates? It should not replace spatial matched
controls, but it is a cleaner early diagnostic of weather/dryness signal.

## Dataset

- Samples: 16
- Positive incident samples: 4
- Folds: 4

## Aggregated out-of-sample metrics

- ROC-AUC: 0.917
- PR-AUC / average precision: 0.771
- Recall@Top10%: 0.250
- Recall@Top20%: 0.750
- Recall@Top50%: 1.000
- Recall@Top100%: 1.000

## Fold diagnostics

| held_out_incident_id | train | test | positive rank | positive score | Recall@Top20% |
|---|---:|---:|---:|---:|---:|
| cannock-chase-sherbrook-valley-2026-08 | 12 | 4 | 1 | 42.882 | 1.000 |
| pershore-2026-08 | 12 | 4 | 1 | 83.762 | 1.000 |
| rhandirmwyn-llandovery-2026-08 | 12 | 4 | 1 | 25.979 | 1.000 |
| stoke-on-trent-2026-08 | 12 | 4 | 1 | 40.378 | 1.000 |

## Interpretation

This is still a small-sample diagnostic, but strong temporal-control performance would be
a useful sign that pre-ignition weather/dryness features are directionally meaningful. The
next proof step remains more positives and land-cover/region-matched spatial controls.
