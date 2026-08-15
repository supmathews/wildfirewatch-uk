# Temporal-control leave-one-incident-out baseline preview

This report uses same-location temporal controls: each incident location is compared with
weather/dryness at prior non-fire reference dates. Each fold holds out one incident group
and trains on the remaining groups.

This answers a narrower question than spatial controls: did each location look more risky
near ignition than it did at earlier reference dates? It should not replace spatial matched
controls, but it is a cleaner early diagnostic of weather/dryness signal.

## Dataset

- Samples: 20
- Positive incident samples: 5
- Folds: 5

## Aggregated out-of-sample metrics

- ROC-AUC: 0.947
- PR-AUC / average precision: 0.853
- Recall@Top10%: 0.400
- Recall@Top20%: 0.600
- Recall@Top50%: 1.000
- Recall@Top100%: 1.000

## Fold diagnostics

| held_out_incident_id | train | test | positive rank | positive score | Recall@Top20% |
|---|---:|---:|---:|---:|---:|
| cannock-chase-2026-08 | 16 | 4 | 1 | 55.214 | 1.000 |
| cannock-chase-sherbrook-valley-2026-08 | 16 | 4 | 1 | 73.157 | 1.000 |
| pershore-2026-08 | 16 | 4 | 1 | 81.579 | 1.000 |
| rhandirmwyn-llandovery-2026-08 | 16 | 4 | 1 | 27.926 | 1.000 |
| stoke-on-trent-2026-08 | 16 | 4 | 1 | 38.959 | 1.000 |

## Interpretation

This is still a small-sample diagnostic, but strong temporal-control performance would be
a useful sign that pre-ignition weather/dryness features are directionally meaningful. The
next proof step remains more positives and land-cover/region-matched spatial controls.
