# Leave-one-incident-out logistic baseline preview

This report is the first out-of-sample check for the retrospective wildfire-risk PoC.
Each fold holds out one positive incident and its generated controls, trains on the
remaining incident/control groups, and scores only the held-out group.

This is still **not** proof of concept: there are only 5 positive
incidents and controls are rough min-distance regional offsets. It is, however, a stricter
diagnostic than the earlier in-sample trainable baseline.

## Dataset

- Samples: 30
- Positive incident samples: 5
- Folds: 5

## Aggregated out-of-sample metrics

- ROC-AUC: 0.608
- PR-AUC / average precision: 0.267
- Recall@Top10%: 0.000
- Recall@Top20%: 0.400
- Recall@Top50%: 0.600
- Recall@Top100%: 1.000

## Fold diagnostics

| held_out_incident_id | train | test | positive rank | positive score | Recall@Top20% |
|---|---:|---:|---:|---:|---:|
| cannock-chase-2026-08 | 24 | 6 | 1 | 13.939 | 1.000 |
| cannock-chase-sherbrook-valley-2026-08 | 24 | 6 | 3 | 10.803 | 0.000 |
| pershore-2026-08 | 24 | 6 | 1 | 21.696 | 1.000 |
| rhandirmwyn-llandovery-2026-08 | 24 | 6 | 2 | 18.465 | 1.000 |
| stoke-on-trent-2026-08 | 24 | 6 | 2 | 22.832 | 1.000 |

## Top out-of-sample scored rows

| rank | sample_id | target | held_out_risk_score |
|---:|---|---:|---:|
| 1 | control-cannock-chase-sherbrook-valley-2026-08-003 | 0 | 38.118 |
| 2 | control-cannock-chase-sherbrook-valley-2026-08-005 | 0 | 34.382 |
| 3 | control-stoke-on-trent-2026-08-003 | 0 | 27.056 |
| 4 | stoke-on-trent-2026-08 | 1 | 22.832 |
| 5 | pershore-2026-08 | 1 | 21.696 |
| 6 | control-stoke-on-trent-2026-08-005 | 0 | 21.366 |
| 7 | control-stoke-on-trent-2026-08-001 | 0 | 20.664 |
| 8 | control-pershore-2026-08-005 | 0 | 20.561 |
| 9 | control-pershore-2026-08-001 | 0 | 18.918 |
| 10 | control-rhandirmwyn-llandovery-2026-08-002 | 0 | 18.500 |
| 11 | rhandirmwyn-llandovery-2026-08 | 1 | 18.465 |
| 12 | control-rhandirmwyn-llandovery-2026-08-001 | 0 | 16.602 |

## Interpretation

These metrics should be treated as a smoke test for model generalisation plumbing, not as
evidence of a deployable signal. The next meaningful data-science step is still to improve
control quality with land-cover/region matching and add more source-backed positive
incidents before making any go/no-go call.
