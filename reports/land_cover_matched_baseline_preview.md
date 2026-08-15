# Land-cover-matched spatial logistic baseline preview

This diagnostic uses OSM-derived coarse land-cover classes to sample spatial controls
with the same class as the matched incident point, then evaluates the trainable
logistic baseline with leave-one-incident-out validation.

## Configuration

- controls_per_incident: 1
- land-cover source: OSM / Overpass coarse tag classification
- evaluation: leave-one-incident-out

## Metrics

- samples: 10
- positives: 5
- folds: 5
- ROC-AUC: 0.68
- PR-AUC / average precision: 0.641667
- Recall: Top 10%: 0.000, Top 20%: 0.200, Top 50%: 0.600, Top 100%: 1.000

## Fold diagnostics

| held_out_incident_id | test_samples | positive_rank | positive_score | recall |
|---|---:|---:|---:|---|
| cannock-chase-2026-08 | 2 | 1 | 37.202 | Top 10%: 1.000, Top 20%: 1.000, Top 50%: 1.000, Top 100%: 1.000 |
| cannock-chase-sherbrook-valley-2026-08 | 2 | 2 | 31.855 | Top 10%: 0.000, Top 20%: 0.000, Top 50%: 0.000, Top 100%: 1.000 |
| pershore-2026-08 | 2 | 1 | 57.518 | Top 10%: 1.000, Top 20%: 1.000, Top 50%: 1.000, Top 100%: 1.000 |
| rhandirmwyn-llandovery-2026-08 | 2 | 2 | 79.575 | Top 10%: 0.000, Top 20%: 0.000, Top 50%: 0.000, Top 100%: 1.000 |
| stoke-on-trent-2026-08 | 2 | 1 | 71.922 | Top 10%: 1.000, Top 20%: 1.000, Top 50%: 1.000, Top 100%: 1.000 |

## Caveats

- OSM land-cover labels are coarse and unevenly tagged.
- The sample remains tiny: four usable positives.
- Public Overpass endpoints can rate-limit; the classifier uses a local cache.
- This is still diagnostic evidence, not production wildfire prediction.
