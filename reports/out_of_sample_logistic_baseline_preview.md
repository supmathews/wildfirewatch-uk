# Leave-one-incident-out logistic baseline preview

This report is the first out-of-sample check for the retrospective wildfire-risk PoC.
Each fold holds out one positive incident and its generated controls, trains on the
remaining incident/control groups, and scores only the held-out group.

This is still **not** proof of concept: there are only 4 positive
incidents and controls are rough min-distance regional offsets. It is, however, a stricter
diagnostic than the earlier in-sample trainable baseline.

## Dataset

- Samples: 24
- Positive incident samples: 4
- Folds: 4

## Aggregated out-of-sample metrics

- ROC-AUC: 0.463
- PR-AUC / average precision: 0.206
- Recall@Top10%: 0.000
- Recall@Top20%: 0.250
- Recall@Top50%: 0.500
- Recall@Top100%: 1.000

## Fold diagnostics

| held_out_incident_id | train | test | positive rank | positive score | Recall@Top20% |
|---|---:|---:|---:|---:|---:|
| cannock-chase-sherbrook-valley-2026-08 | 18 | 6 | 5 | 6.012 | 0.000 |
| pershore-2026-08 | 18 | 6 | 1 | 16.970 | 1.000 |
| rhandirmwyn-llandovery-2026-08 | 18 | 6 | 3 | 15.308 | 0.000 |
| stoke-on-trent-2026-08 | 18 | 6 | 1 | 20.879 | 1.000 |

## Top out-of-sample scored rows

| rank | sample_id | target | held_out_risk_score |
|---:|---|---:|---:|
| 1 | control-cannock-chase-sherbrook-valley-2026-08-003 | 0 | 28.432 |
| 2 | control-cannock-chase-sherbrook-valley-2026-08-005 | 0 | 28.432 |
| 3 | control-cannock-chase-sherbrook-valley-2026-08-002 | 0 | 22.619 |
| 4 | stoke-on-trent-2026-08 | 1 | 20.879 |
| 5 | control-stoke-on-trent-2026-08-003 | 0 | 20.430 |
| 6 | control-stoke-on-trent-2026-08-002 | 0 | 20.422 |
| 7 | control-stoke-on-trent-2026-08-005 | 0 | 20.217 |
| 8 | control-stoke-on-trent-2026-08-004 | 0 | 19.026 |
| 9 | pershore-2026-08 | 1 | 16.970 |
| 10 | control-pershore-2026-08-001 | 0 | 16.859 |
| 11 | control-pershore-2026-08-005 | 0 | 16.437 |
| 12 | control-pershore-2026-08-003 | 0 | 16.365 |

## Interpretation

These metrics should be treated as a smoke test for model generalisation plumbing, not as
evidence of a deployable signal. The next meaningful data-science step is still to improve
control quality with land-cover/region matching and add more source-backed positive
incidents before making any go/no-go call.
