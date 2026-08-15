# Calibrated diagnostic risk-band preview

This report bins calibrated case/control scores into monotonic diagnostic tiers.
The bands are for retrospective evaluation only; they are not public warning
levels or operational emergency guidance.

## Configuration

- source samples: 20
- positives: 5
- sample prevalence: 0.250000
- target prevalence assumption: 0.010000

## Band summary

| band | probability range | samples | positives | observed positive rate | description |
|---|---:|---:|---:|---:|---|
| very_low | [0.0000, 0.0010) | 3 | 0 | 0.000 | Lowest calibrated diagnostic tier; not zero risk. |
| low | [0.0010, 0.0100) | 9 | 0 | 0.000 | Low calibrated diagnostic tier. |
| elevated | [0.0100, 0.0500) | 6 | 3 | 0.500 | Elevated diagnostic tier for retrospective ranking review. |
| high | [0.0500, 1.0000) | 2 | 2 | 1.000 | Highest diagnostic tier; not an operational warning label. |

## Top calibrated rows

| sample_id | target | raw_score_pct | calibrated_probability | band |
|---|---:|---:|---:|---|
| pershore-2026-08 | 1 | 81.579 | 0.118321 | high |
| cannock-chase-sherbrook-valley-2026-08 | 1 | 73.157 | 0.076287 | high |
| control-pershore-2026-08-temporal-30d | 0 | 57.618 | 0.039567 | elevated |
| cannock-chase-2026-08 | 1 | 55.214 | 0.036013 | elevated |
| stoke-on-trent-2026-08 | 1 | 38.959 | 0.018974 | elevated |
| control-pershore-2026-08-temporal-90d | 0 | 33.074 | 0.014754 | elevated |
| rhandirmwyn-llandovery-2026-08 | 1 | 27.926 | 0.011605 | elevated |
| control-stoke-on-trent-2026-08-temporal-30d | 0 | 26.670 | 0.010901 | elevated |

## Caveats

- The target prevalence is illustrative until a proper UK cell/day denominator exists.
- Bands are monotonic bins over calibrated diagnostic scores, not proof of calibrated
  operational probabilities.
- With only four positives, observed rates inside bands are unstable.
