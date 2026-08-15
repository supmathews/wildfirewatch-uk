# Trainable logistic baseline preview

This is the first trainable baseline for the retrospective wildfire-risk PoC. It uses the
same currently usable incident/control rows as the heuristic baseline, but fits a small,
dependency-free logistic regression model over normalized weather and dry-spell features.

This is **not** proof of signal yet: there are only 4 positive
incident samples, controls are still rough min-distance regional offsets, and this report
uses in-sample ranking only. It is a wiring milestone before a larger Logistic Regression /
LightGBM evaluation with proper train/test splits.

## Dataset

- Samples: 24
- Positive incident samples: 4
- Control samples: 20

## Metrics

- ROC-AUC: 0.688
- PR-AUC / average precision: 0.287
- Recall@Top10%: 0.000
- Recall@Top20%: 0.250
- Recall@Top50%: 0.750
- Recall@Top100%: 1.000

## Learned coefficients

| feature | coefficient |
|---|---:|
| temperature_2m_c_norm | 0.220007 |
| low_relative_humidity_norm | 0.280143 |
| wind_speed_10m_mps_norm | 0.234583 |
| wind_gust_10m_mps_norm | 0.355009 |
| rain_7d_dryness_norm | 0.192538 |
| rain_30d_dryness_norm | -0.263933 |
| rain_60d_dryness_norm | -0.699892 |
| days_since_meaningful_rain_norm | -0.603225 |

Model bias: `-1.277023`

## Top ranked samples

| rank | sample_id | target | trained_risk_score |
|---:|---|---:|---:|
| 1 | control-cannock-chase-sherbrook-valley-2026-08-003 | 0 | 21.192 |
| 2 | control-cannock-chase-sherbrook-valley-2026-08-005 | 0 | 21.192 |
| 3 | control-rhandirmwyn-llandovery-2026-08-004 | 0 | 20.772 |
| 4 | stoke-on-trent-2026-08 | 1 | 20.529 |
| 5 | control-stoke-on-trent-2026-08-003 | 0 | 19.875 |
| 6 | pershore-2026-08 | 1 | 19.832 |
| 7 | control-stoke-on-trent-2026-08-002 | 0 | 19.827 |
| 8 | control-stoke-on-trent-2026-08-005 | 0 | 19.736 |
| 9 | control-cannock-chase-sherbrook-valley-2026-08-002 | 0 | 19.245 |
| 10 | rhandirmwyn-llandovery-2026-08 | 1 | 18.887 |
| 11 | control-pershore-2026-08-005 | 0 | 18.785 |
| 12 | control-stoke-on-trent-2026-08-004 | 0 | 18.348 |

## Interpretation

This proves the repository can now train and score a logistic baseline from the generated
retrospective feature table. Treat the numbers as diagnostic only until the positive dataset
is much larger and controls are land-cover/region matched.
