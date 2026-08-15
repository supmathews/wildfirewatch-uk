# Incident modelling-readiness audit

This report lists which source-backed seed incidents are currently usable by the
weather-feature/model pipeline and which are blocked. It is intentionally strict:
missing timestamps or coordinates exclude incidents to preserve leakage discipline.

## Summary

- total incidents: 10
- model-ready incidents: 5
- blocked incidents: 5

## Blocker counts

- missing_latitude: 1
- missing_longitude: 1
- missing_start_timestamp: 5
- needs_verification: 1
- placeholder_source: 1

## Incident details

| incident_id | location | status | blockers |
|---|---|---|---|
| stourbridge-2026-08 | Stourbridge | blocked | missing_start_timestamp |
| pershore-2026-08 | Pershore | model_ready | none |
| new-forest-2026-08 | New Forest | blocked | missing_start_timestamp |
| llangynidr-reservoir-2026-08 | Llangynidr Reservoir | blocked | missing_start_timestamp |
| cannock-chase-2026-08 | Cannock Chase | model_ready | none |
| cannock-chase-sherbrook-valley-2026-08 | Cannock Chase / Sherbrook Valley | model_ready | none |
| tamworth-2026-08 | Tamworth | blocked | needs_verification, missing_start_timestamp, missing_latitude, missing_longitude, placeholder_source |
| stoke-on-trent-2026-08 | Stoke-on-Trent | model_ready | none |
| rhandirmwyn-llandovery-2026-08 | Rhandirmwyn / Llandovery | model_ready | none |
| porth-2026-08 | Porth | blocked | missing_start_timestamp |

## Interpretation

A blocked incident can still be source-backed and valuable, but it should not feed
the weather-feature model until the blockers are resolved. The highest-value next
research task is finding durable exact timestamps for source-backed incidents that
already have coordinates.
