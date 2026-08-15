# Calibrated diagnostic risk-band preview

This report bins calibrated case/control scores into monotonic diagnostic tiers.
The bands are for retrospective evaluation only; they are not public warning
levels or operational emergency guidance.

## Configuration

- source samples: 16
- positives: 4
- sample prevalence: 0.250000
- target prevalence assumption: 0.010000

## Band summary

| band | probability range | samples | positives | observed positive rate | description |
|---|---:|---:|---:|---:|---|
| very_low | [0.0000, 0.0010) | 2 | 0 | 0.000 | Lowest calibrated diagnostic tier; not zero risk. |
| low | [0.0010, 0.0100) | 7 | 0 | 0.000 | Low calibrated diagnostic tier. |
| elevated | [0.0100, 0.0500) | 6 | 3 | 0.500 | Elevated diagnostic tier for retrospective ranking review. |
| high | [0.0500, 1.0000) | 1 | 1 | 1.000 | Highest diagnostic tier; not an operational warning label. |

## Top calibrated rows

| sample_id | target | raw_score_pct | calibrated_probability | band |
|---|---:|---:|---:|---|
| pershore-2026-08 | 1 | 83.762 | 0.135184 | high |
| control-pershore-2026-08-temporal-30d | 0 | 56.282 | 0.037547 | elevated |
| cannock-chase-sherbrook-valley-2026-08 | 1 | 42.882 | 0.022244 | elevated |
| stoke-on-trent-2026-08 | 1 | 40.378 | 0.020110 | elevated |
| control-pershore-2026-08-temporal-90d | 0 | 40.068 | 0.019857 | elevated |
| rhandirmwyn-llandovery-2026-08 | 1 | 25.979 | 0.010523 | elevated |
| control-stoke-on-trent-2026-08-temporal-30d | 0 | 25.636 | 0.010339 | elevated |
| control-cannock-chase-sherbrook-valley-2026-08-temporal-90d | 0 | 20.702 | 0.007849 | low |

## Caveats

- The target prevalence is illustrative until a proper UK cell/day denominator exists.
- Bands are monotonic bins over calibrated diagnostic scores, not proof of calibrated
  operational probabilities.
- With only four positives, observed rates inside bands are unstable.
