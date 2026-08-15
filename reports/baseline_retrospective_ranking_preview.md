# Baseline retrospective ranking preview

This is an early heuristic baseline using currently usable incidents and generated regional
controls. Controls use the `regional_offset_min_distance_v2` sampler, which keeps them at
least 20 km from all known incident points. It is **not** the final proof of concept: the
positive dataset is still tiny, controls are rough regional offsets, and the scoring
function is a transparent heuristic rather than a trained model.

## Dataset

- Samples: 24
- Positive incident samples: 4
- Control samples: 20

## Ranking metrics

- Recall@Top10%: 0.000
- Recall@Top20%: 0.250
- Recall@Top50%: 0.500
- Recall@Top100%: 1.000

## Top ranked samples

| rank | sample_id | target | risk_score |
|---:|---|---:|---:|
| 1 | control-pershore-2026-08-004 | 0 | 87.953 |
| 2 | control-pershore-2026-08-003 | 0 | 86.205 |
| 3 | control-pershore-2026-08-002 | 0 | 85.677 |
| 4 | control-pershore-2026-08-001 | 0 | 83.008 |
| 5 | pershore-2026-08 | 1 | 82.434 |
| 6 | control-pershore-2026-08-005 | 0 | 78.283 |
| 7 | control-stoke-on-trent-2026-08-001 | 0 | 77.160 |
| 8 | control-rhandirmwyn-llandovery-2026-08-005 | 0 | 76.494 |
| 9 | control-cannock-chase-sherbrook-valley-2026-08-004 | 0 | 75.582 |
| 10 | cannock-chase-sherbrook-valley-2026-08 | 1 | 72.982 |

## Interpretation

This run verifies the end-to-end path: incident features, matched control generation,
control weather retrieval, combined dataset assembly, and baseline ranking. The next
iteration should increase verified positive incidents, replace rough min-distance controls
with land-cover/region-matched controls, and train Logistic Regression / LightGBM once the
dataset is large enough.
