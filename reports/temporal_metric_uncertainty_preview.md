# Temporal metric uncertainty preview

This report adds deterministic bootstrap intervals around current out-of-sample
temporal-control metrics. It is intended to make the tiny-sample uncertainty
visible rather than hiding it behind point estimates.

## Configuration

- samples: 20
- positives: 5
- confidence level: 90%

## Bootstrap intervals

| metric | point estimate | interval | valid resamples | skipped resamples |
|---|---:|---:|---:|---:|
| roc_auc | 0.946667 | [0.831333, 1.000000] | 495 | 5 |
| pr_auc | 0.852857 | [0.500833, 1.000000] | 495 | 5 |

## Interpretation

- Wide intervals are expected with only four positives.
- Skipped resamples occur when a bootstrap draw lacks both positive and negative
  samples, making ROC-AUC or PR-AUC undefined.
- These intervals are diagnostic uncertainty summaries, not formal proof of
  deployment readiness.
