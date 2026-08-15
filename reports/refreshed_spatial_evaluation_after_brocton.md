# Refreshed spatial evaluation after 5-positive upgrade

## Context

PR #19 upgraded the 30 July Cannock Chase / Brocton incident to model-ready by adding source-backed approximate Brocton coordinates. This increased usable positives from 4 to 5.

This report refreshes the spatial-control evaluations after that upgrade.

## Rough spatial controls

Command:

```bash
uv run --extra dev python scripts/run_out_of_sample_baseline.py \
  --controls-per-incident 5 \
  --output reports/out_of_sample_logistic_baseline_preview.md
```

Result:

```text
samples=30 positives=5
roc_auc=0.608
pr_auc=0.267451
Recall@Top10%=0.0
Recall@Top20%=0.4
Recall@Top50%=0.6
Recall@Top100%=1.0
```

## OSM land-cover-matched spatial controls

Command:

```bash
uv run --extra dev python scripts/run_land_cover_matched_baseline.py \
  --controls-per-incident 1 \
  --max-attempts-per-control 80 \
  --radius-degrees 0.02 \
  --output reports/land_cover_matched_baseline_preview.md
```

Result:

```text
samples=10 positives=5
roc_auc=0.68
pr_auc=0.641667
Recall@Top10%=0.0
Recall@Top20%=0.2
Recall@Top50%=0.6
Recall@Top100%=1.0
```

## Interpretation

The land-cover-matched spatial diagnostic remains stronger than rough regional controls after the fifth positive is added:

- Rough spatial controls: ROC-AUC `0.608`, PR-AUC `0.267451`
- Land-cover-matched controls: ROC-AUC `0.68`, PR-AUC `0.641667`

This supports the control-quality hypothesis: matching land cover appears to produce a more meaningful spatial comparison than broad regional random offsets.

## Caveats

- Only five usable positives.
- Land-cover labels are coarse OSM-derived classes.
- Land-cover matched run currently uses one matched control per incident.
- Brocton coordinates are approximate geocoding, not an exact fire perimeter.
- These remain diagnostic model-development results, not concept proof or live prediction evidence.
