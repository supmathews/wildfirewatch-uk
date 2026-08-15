# Incident independence / cluster audit

This report flags model-ready positive incidents that are geographically and
temporally close enough to be treated as a potential local cluster rather than
fully independent evidence. It does not merge or remove records; it documents
an evaluation caveat for tiny-sample metrics.

## Configuration

- distance threshold: 10.0 km
- day threshold: 14 days

## Summary

- model-ready incidents: 5
- potential cluster pairs: 1

## Potential cluster pairs

| incident_id_a | incident_id_b | distance_km | days_apart | reason |
|---|---|---:|---:|---|
| cannock-chase-2026-08 | cannock-chase-sherbrook-valley-2026-08 | 3.73 | 6 | within_10.0km_and_14d |

## Interpretation

Potential cluster pairs should be treated cautiously in model interpretation:
they may represent distinct incidents, but they are not as independent as
events separated across wider geography and time. With only five usable
positives, even one local cluster can make point estimates look more stable
than they really are.
