# OSM coarse land-cover classification preview

Generated with:

```bash
uv run --extra dev python scripts/classify_incident_land_cover.py \
  --csv data/processed/incident_weather_features.csv \
  --radius-degrees 0.02
```

## Live OSM/Overpass output

| incident_id | latitude | longitude | osm_coarse_land_cover |
|---|---:|---:|---|
| pershore-2026-08 | 52.1130376 | -2.0843023 | heath_or_grass |
| cannock-chase-sherbrook-valley-2026-08 | 52.7496197 | -2.0053533 | heath_or_grass |
| stoke-on-trent-2026-08 | 53.00131 | -2.1069951 | heath_or_grass |
| rhandirmwyn-llandovery-2026-08 | 52.0776364 | -3.7751552 | woodland |

## Interpretation

This is useful enough to keep as the first open-data land-cover provider prototype:

- all 4 currently usable positive incident points received a coarse OSM-derived class;
- 3/4 are tagged as `heath_or_grass`;
- 1/4 is tagged as `woodland`;
- the classes are plausible for wildfire-susceptible environments.

## Caveats

- OSM is unevenly tagged and not authoritative.
- A 0.02-degree search radius was needed for reliable live coverage.
- Public Overpass endpoints can rate-limit or time out; this provider should be cached before large control runs.
- These labels are coarse context features/matching labels, not fire perimeters or formal land-cover products.

## Next step

Use these classes to generate land-cover-matched spatial controls with caching/throttling, then rerun spatial leave-one-incident-out evaluation. If metrics improve versus the current spatial-control baseline, that would be a stronger proof signal.
