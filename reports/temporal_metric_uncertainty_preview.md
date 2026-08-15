# Temporal metric uncertainty preview

This report adds deterministic bootstrap intervals around current out-of-sample
temporal-control metrics. It is intended to make the tiny-sample uncertainty
visible rather than hiding it behind point estimates.

## Configuration

- samples: 16
- positives: 4
- confidence level: 90%

## Bootstrap intervals

| metric | point estimate | interval | valid resamples | skipped resamples |
|---|---:|---:|---:|---:|
| roc_auc | 0.916667 | [0.766212, 1.000000] | 498 | 2 |
| pr_auc | 0.770833 | [0.409968, 1.000000] | 498 | 2 |

## Interpretation

- Wide intervals are expected with only four positives.
- Skipped resamples occur when a bootstrap draw lacks both positive and negative
  samples, making ROC-AUC or PR-AUC undefined.
- These intervals are diagnostic uncertainty summaries, not formal proof of
  deployment readiness.
