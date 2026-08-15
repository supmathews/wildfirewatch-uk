# Open Issues

## Incident data quality

- Find a durable source URL for the Tamworth case-study fire; it remains a placeholder record and must not be used for analysis yet.
- Confirm exact ignition/start times for Stourbridge, New Forest, Llangynidr Reservoir, Porth, and Tamworth.
- Replace approximate geocoded point locations with source-backed incident centroids or fire perimeters before serious spatial modelling.
- Continue expanding source-backed positive incidents with exact timestamps; current readiness audit shows 5 model-ready and 5 blocked seed incidents.

## Weather, land-cover and context features

- Replace the Open-Meteo archive fallback with authoritative UK rainfall/weather providers where licensing and historical coverage allow.
- Add reproducible land-cover features that do not depend on live Overpass availability for routine tests/reports.
- Research terrain/topography feature providers suitable for UK-wide retrospective modelling.
- Research human-activity proxy features, especially for Scotland/muirburning and access/ignition-opportunity context.
- Add a risk-decay-after-rainfall experiment: snapshot affected/high-risk locations daily for 1-2 weeks and verify risk scores fall credibly after meaningful rain, cooler temperatures, and higher humidity.

## Evaluation and positioning

- Before public-facing docs/demos, explicitly position WildfireWatch UK against FireInSite, Met Office/Natural England Fire Severity Index, EFFIS, ECMWF Probability of Fire, and the Scotland ML occurrence/susceptibility work without overstating capability.
- Treat Scotland as a formal geographic-transfer/calibration experiment once enough Scottish positives exist.
- Decide whether to use a 1 km UK grid or H3 cells for the first gridded case study.
