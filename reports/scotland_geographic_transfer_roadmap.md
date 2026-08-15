# Scotland geographic-transfer roadmap

## Source

This roadmap distils the uploaded landscape update:

- `WildfireWatch_UK_Landscape_Findings_Updated_15_Aug_2026.pdf`
- key addition: Scotland-specific ML wildfire occurrence/susceptibility work by CEDA / NCAS / University of St Andrews / DTU collaborators, presented at EGU 2026 and updated July 2026.

## Why this matters

The Scotland work is one of the closest UK-aligned references found so far because it targets wildfire occurrence/susceptibility rather than only post-ignition spread, burned-area mapping, detection, fuel ignitability, or severity.

It uses a long historical dataset combining:

- atmospheric variables
- land cover
- topography
- human-activity context
- ML models such as Random Forests and SVMs
- SHAP explainability
- national susceptibility maps
- forecast-weather likelihood inputs

The most important reported lesson is that Scottish wildfire drivers may differ from warmer European contexts: weather variables may be less dominant, while land-cover, vegetation, physical characteristics and muirburning context can matter more.

## Implication for WildfireWatch UK

WildfireWatch should treat Scotland as a first-class geographic-transfer and calibration experiment. A model trained on England/Wales incidents should not be assumed to transfer to Scottish conditions without testing.

## Proposed staged work

### Stage 1 — Data contract

Add explicit fields/features for geographic transfer experiments:

- nation / region label
- land-cover class
- terrain / topographic context
- human-activity proxy features
- provenance for region assignment and feature source

### Stage 2 — Scottish positive incidents

Build a Scotland-specific seed subset with the same data-quality rules used elsewhere:

- source-backed incidents only
- exact timestamps where possible
- approximate points allowed only as research points
- no guessed ignition times or perimeters
- blocked records excluded from modelling until readiness criteria are met

### Stage 3 — Feature ablations by geography

Run staged ablations separately by geographic grouping:

1. latest weather only
2. antecedent rainfall / dry-spell memory
3. land-cover / vegetation
4. terrain / topography
5. human context
6. combined model

### Stage 4 — Transfer tests

When enough positives exist, run explicit transfer diagnostics:

- train England/Wales, test Scotland
- train Scotland, test England/Wales
- train UK-wide, compare region-specific calibration
- compare PR-AUC and Recall@Top-X% by geography
- track false-alarm area by region

### Stage 5 — Explainability

Only after dataset size and controls improve, add model-family comparisons and explainability:

- Random Forest / gradient-boosting candidate
- SHAP-style feature contribution checks
- physical credibility review of learned drivers
- region-specific calibration review

## Near-term repo implications

The immediate next engineering/data-science work should prioritize:

1. more source-backed positive incidents with exact timestamps
2. land-cover features that are reproducible without live Overpass fragility
3. terrain/topography feature provider research
4. human-activity proxy feature provider research
5. explicit geographic grouping once enough incidents exist

## Caveats

- This roadmap is based on landscape review, not copied implementation.
- Current WildfireWatch data remains too small for Scotland transfer testing.
- The current temporal-control signal is promising but geographically narrow.
- The current rough spatial signal remains weak-to-diagnostic.
- This does not change the product safety position: WildfireWatch is still a retrospective validation PoC, not an operational warning system.
