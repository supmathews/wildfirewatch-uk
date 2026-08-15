# Prevalence-corrected probability preview

This report demonstrates why case/control model scores should not be presented as
real-world wildfire probabilities. The ranking is unchanged, but probabilities are
corrected from the sampled positive prevalence to assumed rare-event prevalences.

## Source evaluation

- samples: 16
- positives: 4
- sample prevalence: 0.250000
- ROC-AUC: 0.916667
- PR-AUC: 0.770833

## Top out-of-sample rows with corrected probabilities

| sample_id | target | raw_score_pct | p@1.0000% | p@0.1000% |
|---|---|---|---|---|
| pershore-2026-08 | 1 | 83.762 | 0.135184 | 0.015254 |
| control-pershore-2026-08-temporal-30d | 0 | 56.282 | 0.037547 | 0.003851 |
| cannock-chase-sherbrook-valley-2026-08 | 1 | 42.882 | 0.022244 | 0.002249 |
| stoke-on-trent-2026-08 | 1 | 40.378 | 0.020110 | 0.002030 |
| control-pershore-2026-08-temporal-90d | 0 | 40.068 | 0.019857 | 0.002004 |
| rhandirmwyn-llandovery-2026-08 | 1 | 25.979 | 0.010523 | 0.001053 |
| control-stoke-on-trent-2026-08-temporal-30d | 0 | 25.636 | 0.010339 | 0.001034 |
| control-cannock-chase-sherbrook-valley-2026-08-temporal-90d | 0 | 20.702 | 0.007849 | 0.000783 |

## Interpretation

- The correction preserves rank order, so ROC-AUC/PR-AUC are unchanged.
- It prevents oversampled case/control outputs from being mistaken for real-world
  wildfire probabilities.
- The target prevalences here are illustrative until a proper cell/day sampling
  denominator exists.
