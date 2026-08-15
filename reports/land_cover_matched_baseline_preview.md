# Land-cover-matched spatial logistic baseline preview

This diagnostic uses OSM-derived coarse land-cover classes to sample spatial controls
with the same class as the matched incident point, then evaluates the trainable
logistic baseline with leave-one-incident-out validation.

## Configuration

- controls_per_incident: 1
- land-cover source: OSM / Overpass coarse tag classification
- evaluation: leave-one-incident-out

## Metrics

- samples: 8
- positives: 4
- folds: 4
- ROC-AUC: 0.625
- PR-AUC / average precision: 0.622024
- Recall: Top 10%: 0.000, Top 20%: 0.250, Top 50%: 0.750, Top 100%: 1.000

## Fold diagnostics

| held_out_incident_id | test_samples | positive_rank | positive_score | recall |
|---|---:|---:|---:|---|
| cannock-chase-sherbrook-valley-2026-08 | 2 | 1 | 9.401 | Top 10%: 1.000, Top 20%: 1.000, Top 50%: 1.000, Top 100%: 1.000 |
| pershore-2026-08 | 2 | 1 | 62.541 | Top 10%: 1.000, Top 20%: 1.000, Top 50%: 1.000, Top 100%: 1.000 |
| rhandirmwyn-llandovery-2026-08 | 2 | 2 | 70.824 | Top 10%: 0.000, Top 20%: 0.000, Top 50%: 0.000, Top 100%: 1.000 |
| stoke-on-trent-2026-08 | 2 | 1 | 69.51 | Top 10%: 1.000, Top 20%: 1.000, Top 50%: 1.000, Top 100%: 1.000 |

## Caveats

- OSM land-cover labels are coarse and unevenly tagged.
- The sample remains tiny: four usable positives.
- Public Overpass endpoints can rate-limit; the classifier uses a local cache.
- This is still diagnostic evidence, not production wildfire prediction.
