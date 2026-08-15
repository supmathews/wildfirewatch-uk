# Retrospective incident weather feature preview

Generated with:

```bash
uv run --extra dev python scripts/build_incident_weather_features.py \
  --output data/processed/incident_weather_features.csv
```

Provider: Open-Meteo historical archive fallback (`open-meteo-archive`).

This is an early proof-of-concept feature extraction run, not the final modelling dataset. It only includes seed incidents with both a source-backed timestamp and approximate coordinates.

## Included incidents

| incident_id | target_timestamp UTC | temp C | RH % | wind m/s | gust m/s | rain_24h mm | rain_7d mm | rain_30d mm | rain_60d mm | days_since_rain | days_since_meaningful_rain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pershore-2026-08 | 2026-08-13T15:17:00Z | 36.5 | 21 | 5.472 | 11.0 | 0.0 | 0.0 | 6.4 | 28.1 | 9 | 9 |
| cannock-chase-sherbrook-valley-2026-08 | 2026-08-05T13:30:00Z | 20.3 | 45 | 7.75 | 16.611 | 1.6 | 4.3 | 5.4 | 61.6 | 0 | 31 |
| stoke-on-trent-2026-08 | 2026-08-09T15:30:00Z | 25.6 | 37 | 5.722 | 12.194 | 0.0 | 6.1 | 11.1 | 52.1 | 4 | 5 |
| rhandirmwyn-llandovery-2026-08 | 2026-08-12T11:45:00Z | 27.4 | 48 | 2.75 | 6.5 | 0.0 | 0.8 | 24.2 | 73.6 | 7 | 8 |

## Excluded for now

- Stourbridge: approximate coordinates exist, but exact/source-backed ignition time is unresolved.
- New Forest: approximate coordinates exist, but exact/source-backed ignition time is unresolved.
- Cannock Chase 30 July: source-backed call time exists, but coordinates are intentionally unset pending a better source-backed centroid/perimeter.
- Tamworth: remains unverified.
- Porth: approximate coordinates exist, but exact/source-backed ignition time is unresolved.

## Interpretation

This first run shows the code path can collect repeatable pre-incident weather/rainfall features and calculate dry-spell windows without using post-ignition data. It is not enough to prove the concept yet; next we need better matched non-fire controls and enough verified positives to train Logistic Regression / LightGBM baselines.
