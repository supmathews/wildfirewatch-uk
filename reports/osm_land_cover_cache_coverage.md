# OSM land-cover cache coverage audit

This report checks whether current model-ready incident points have deterministic
coarse land-cover labels in the committed OSM cache. It does not call Overpass.

## Configuration

- cache_path: `data/processed/osm_land_cover_cache.json`
- point set: current model-ready seed incidents

## Summary

- model-ready points: 5
- classified points: 5
- cached null points: 0
- missing cache entries: 0
- classified coverage: 1.000

## Details

| incident_id | cache_key | status | land_cover_class |
|---|---|---|---|
| pershore-2026-08 | 52.113038,-2.084302 | classified | heath_or_grass |
| cannock-chase-2026-08 | 52.772597,-2.045833 | classified | heath_or_grass |
| cannock-chase-sherbrook-valley-2026-08 | 52.749620,-2.005353 | classified | heath_or_grass |
| stoke-on-trent-2026-08 | 53.001310,-2.106995 | classified | heath_or_grass |
| rhandirmwyn-llandovery-2026-08 | 52.077636,-3.775155 | classified | woodland |

## Interpretation

Full cache coverage means routine land-cover diagnostics for current model-ready
incidents can run without live Overpass calls. This does not make OSM-derived
classes authoritative, and it does not solve land-cover coverage for future
new incidents or generated controls.
