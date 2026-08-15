# Incident UK-nation data contract preview

This report summarizes the first geographic-transfer data-contract field:
`uk_nation`. It supports future England/Wales/Scotland transfer and
calibration experiments without implying those experiments are ready yet.

## Counts by UK nation

| uk_nation | seed_incidents | model_ready_incidents |
|---|---:|---:|
| england | 7 | 4 |
| wales | 3 | 1 |

## Incident details

| incident_id | location | uk_nation | modelling_status |
|---|---|---|---|
| stourbridge-2026-08 | Stourbridge | england | blocked |
| pershore-2026-08 | Pershore | england | model_ready |
| new-forest-2026-08 | New Forest | england | blocked |
| llangynidr-reservoir-2026-08 | Llangynidr Reservoir | wales | blocked |
| cannock-chase-2026-08 | Cannock Chase | england | model_ready |
| cannock-chase-sherbrook-valley-2026-08 | Cannock Chase / Sherbrook Valley | england | model_ready |
| tamworth-2026-08 | Tamworth | england | blocked |
| stoke-on-trent-2026-08 | Stoke-on-Trent | england | model_ready |
| rhandirmwyn-llandovery-2026-08 | Rhandirmwyn / Llandovery | wales | model_ready |
| porth-2026-08 | Porth | wales | blocked |

## Interpretation

Current source-backed/model-ready positives cover England and Wales only.
Scotland transfer testing remains blocked until Scotland-specific source-backed
positive incidents are collected with the same strict timestamp/coordinate
readiness rules.
