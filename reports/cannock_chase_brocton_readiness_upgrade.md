# Cannock Chase / Brocton modelling-readiness upgrade

## Updated incident

- Incident ID: `cannock-chase-2026-08`
- Existing source-backed timestamp: `2026-07-30T18:00:00+01:00`
- New coordinates: approximate Brocton geocoding, `52.7725969, -2.0458326`

## Source basis

Staffordshire County Council reports that crews from Staffordshire Fire and Rescue Service and West Midlands Fire Service were called to a large fire at the site in Brocton at 6pm on Thursday 30 July 2026. The same source reports that the fire scorched a football-pitch-sized area of heathland in Sherbrook Valley.

Geocoding provenance:

- https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&q=Brocton%20Staffordshire

## Modelling impact

The readiness audit now reports:

- total incidents: 10
- model-ready incidents: 5
- blocked incidents: 5

Feature generation now writes 5 usable positive rows:

```text
wrote 5 feature rows to data/processed/incident_weather_features.csv
```

Temporal-control leave-one-incident-out preview now reports:

```text
samples=20 positives=5
roc_auc=0.946667
pr_auc=0.852857
Recall@Top20%=0.6
Recall@Top50%=1.0
```

## Caveats

- Coordinates are approximate geocoding of Brocton, not a fire perimeter or exact burn centroid.
- This remains a small-sample diagnostic result.
- The July 30 Brocton/Sherbrook Valley fire remains separate from the August 5 Cannock Chase / Sherbrook Valley incident.
