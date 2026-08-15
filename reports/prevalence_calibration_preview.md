# Prevalence-corrected probability preview

This report demonstrates why case/control model scores should not be presented as
real-world wildfire probabilities. The ranking is unchanged, but probabilities are
corrected from the sampled positive prevalence to assumed rare-event prevalences.

## Source evaluation

- samples: 20
- positives: 5
- sample prevalence: 0.250000
- ROC-AUC: 0.946667
- PR-AUC: 0.852857

## Top out-of-sample rows with corrected probabilities

| sample_id | target | raw_score_pct | p@1.0000% | p@0.1000% |
|---|---|---|---|---|
| pershore-2026-08 | 1 | 81.579 | 0.118321 | 0.013125 |
| cannock-chase-sherbrook-valley-2026-08 | 1 | 73.157 | 0.076287 | 0.008118 |
| control-pershore-2026-08-temporal-30d | 0 | 57.618 | 0.039567 | 0.004066 |
| cannock-chase-2026-08 | 1 | 55.214 | 0.036013 | 0.003689 |
| stoke-on-trent-2026-08 | 1 | 38.959 | 0.018974 | 0.001913 |
| control-pershore-2026-08-temporal-90d | 0 | 33.074 | 0.014754 | 0.001482 |
| rhandirmwyn-llandovery-2026-08 | 1 | 27.926 | 0.011605 | 0.001162 |
| control-stoke-on-trent-2026-08-temporal-30d | 0 | 26.670 | 0.010901 | 0.001091 |

## Interpretation

- The correction preserves rank order, so ROC-AUC/PR-AUC are unchanged.
- It prevents oversampled case/control outputs from being mistaken for real-world
  wildfire probabilities.
- The target prevalences here are illustrative until a proper cell/day sampling
  denominator exists.
