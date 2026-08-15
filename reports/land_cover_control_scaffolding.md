# Land-cover-aware control scaffolding

This note documents the next spatial-control improvement after PR #8.

## Why this matters

The current spatial-control evaluation is deliberately hard but still noisy: controls are
regional random offsets with minimum-distance safeguards. They may accidentally compare a
fire-prone heath/grass/woodland point against an urban, water, or otherwise irrelevant
control point.

That can make out-of-sample metrics look weak for the wrong reason: the control set may be
answering a geography/artifact question rather than a like-for-like ignition-risk question.

## Added in this branch

- A provider-agnostic land-cover control sampler.
- A `LandCoverClassifier` protocol so OSM, UKCEH, or another provider can be added later.
- A deterministic `StaticLandCoverClassifier` for tests and development.
- A `LandCoverMatchedControlLocation` model with `land_cover_class` provenance.
- Tests proving controls are only accepted when their class matches the incident class.

## What this does not claim

This branch does not yet improve model metrics, because it intentionally avoids using a fake
or guessed land-cover provider for the real case-study report. The next branch should wire an
authoritative or at least clearly-labelled provider and rerun the spatial out-of-sample
evaluation.

## Next provider options

1. OpenStreetMap / Overpass coarse tags: quick open-data prototype, uneven coverage.
2. UKCEH Land Cover Map: more authoritative, but licensing/access must be checked.
3. Hybrid: OSM for early OSS prototype, UKCEH/other authoritative data as documented future replacement.
