PLAN.md — WildfireWatch UK
1. Project Goal
Build an AI-assisted UK wildfire risk and situational-intelligence platform that
can:
  1. Estimate wildfire ignition risk for small geographic areas across the
     UK.
  2. Show potential fire severity using weather, rainfall deficit, vegeta-
     tion/fuel dryness, wind, terrain, and land-use context.
  3. Detect possible active fires from satellite thermal anomalies and oﬀicial
     incident reports.
  4. Explain why a location is high risk in plain English.
  5. Provide a retrospective analysis mode to answer:
      Could recent UK wildfire locations have been ranked as high risk
      before the fires started?
The first deliverable is a proof of concept, not a public emergency-warning
system.



2. Working Product Name
WildfireWatch UK
Positioning:
     AI-assisted wildfire risk and situational intelligence for the UK.
Do not position the MVP as:
     AI predicts exactly where a wildfire will happen.



3. MVP Objective
The MVP should score known wildfire locations and comparable non-fire loca-
tions using historical environmental conditions.
Initial case-study locations:
  • Stourbridge
  • Pershore
  • New Forest
  • Cannock Chase
  • Tamworth
  • Stoke-on-Trent
  • Rhandirmwyn / Llandovery


                                       1
  • Porth
For each fire, reconstruct conditions during:
  • Previous 24 hours
  • Previous 7 days
  • Previous 30 days
  • Previous 60 days
  • Previous 90 days where data permits
Then compare these locations against at least 100 control locations where no
wildfire was recorded during the same period.
Primary research question:
     Were wildfire locations unusually high-risk relative to comparable
     UK locations before ignition?




4. Success Criteria
The first PoC is successful if it can produce:
  • A repeatable dataset for fire and control locations.
  • A risk score between 0–100.
  • A ranked table of UK locations.
  • An explanation of the top contributing factors.
  • A map showing fire and non-fire locations.
  • A retrospective result showing whether recent wildfire locations ranked
    unusually high.
  • A simple model that performs materially better than random classification.
  • Full provenance for every input feature.
The PoC is not required to:
  • Predict exact ignition time.
  • Predict exact fire spread.
  • Issue public emergency alerts.
  • Replace Met Oﬀice / Fire & Rescue Service guidance.
  • Operate at national production scale.




5. Recommended Tech Stack
Backend
  • Python 3.12+
  • FastAPI


                                        2
  • Pydantic
  • Pandas or Polars
  • SQLAlchemy
  • PostgreSQL
  • PostGIS

ML
Start with:
  • LightGBM
  • XGBoost
  • Logistic Regression baseline
  • SHAP for explainability
Do not start with deep learning unless the structured-data baseline clearly jus-
tifies it.

Geospatial
  • GeoPandas
  • Shapely
  • Rasterio
  • H3 or a 1 km UK grid
  • PostGIS

Frontend
MVP options:
  • Streamlit for fastest PoC
  • Or React + MapLibre / Leaflet for a more product-like UI
Recommended starting point:
Streamlit + MapLibre/pydeck, then migrate later if warranted.

LLM Layer
Use an LLM only for:
  • Incident report extraction
  • Data-quality summaries
  • Risk explanations
  • Natural-language incident briefings
Do not use the LLM as the numerical wildfire-risk model.




                                       3
6. Target Architecture
                     WEATHER
          Met Office / weather feeds
                      |
                      v
        +----------------------------+
        |                             |
RAINFALL|       INGESTION LAYER       | SATELLITE
  ----->|                             |<----- FIRMS
        +-------------+--------------+
                        |
                        v
              NORMALISATION
                        |
                        v
                 POSTGRESQL
                   + POSTGIS
                        |
           +----------+----------+
           |                      |
           v                      v
     FEATURE ENGINE          INCIDENT NLP
           |                      |
           v                      v
     RISK MODEL              FIRE EVENTS DB
           |                      |
           +----------+----------+
                        |
                        v
                 RISK API
                        |
              +-------+-------+
              |                 |
              v                 v
          DASHBOARD          ALERTS
              |
              v
          "WHY HERE?"




7. Data Sources
Create each integration behind a provider interface so sources can be swapped
later.


                                     4
7.1 Weather
Required fields:
  • air temperature
  • daily maximum temperature
  • minimum temperature
  • relative humidity
  • dew point if available
  • wind speed
  • wind gust
  • wind direction
  • precipitation
  • forecast precipitation
Preferred source:
  • Met Oﬀice data/API where licensing and access permit
Fallback during development:
  • Other openly accessible weather observations with clear provenance
Store:
timestamp
station_id
latitude
longitude
temperature_c
relative_humidity_pct
wind_speed_mps
wind_gust_mps
wind_direction_deg
rainfall_mm
source
retrieved_at



7.2 Rainfall
Primary use:
Calculate historical dryness.
Required derived metrics:
hours_since_last_rain
days_since_last_rain
rainfall_24h
rainfall_7d


                                    5
rainfall_30d
rainfall_60d
rainfall_90d
consecutive_dry_days
rain_days_30d
rain_days_60d
Rain threshold must be configurable.
Suggested defaults:
trace_rain_threshold_mm = 0.2
meaningful_rain_threshold_mm = 1.0
Store raw rainfall observations so calculations can be reproduced.



7.3 Satellite Fire Detection
Use:
  • NASA FIRMS
  • VIIRS
  • MODIS
Capture:
detection_id
latitude
longitude
acquisition_timestamp
satellite
instrument
brightness
confidence
frp
daynight
source
Associate thermal anomalies with nearby known incidents.
Suggested matching window:
distance <= 5 km
time difference <= 12 hours
Make both configurable.




                                       6
7.4 Vegetation / Fuel
Candidate variables:
  • NDVI
  • vegetation cover
  • grassland
  • heathland
  • woodland
  • crop/stubble
  • peatland
  • land-cover class
Later features:
  • vegetation moisture proxy
  • dead fuel moisture
  • seasonal vegetation state



7.5 Soil / Ground Moisture
Candidate sources should provide:
  • soil moisture
  • drought status
  • soil moisture anomaly
Derived metrics:
soil_moisture_current
soil_moisture_percentile
soil_moisture_anomaly



7.6 Terrain
Use a UK digital elevation model.
Calculate:
elevation
slope
aspect
terrain_ruggedness
Slope is important for later fire-spread modelling.




                                       7
7.7 Human / Land-Use Context
Potential ignition-related variables:
distance_to_road
distance_to_footpath
distance_to_railway
distance_to_buildings
distance_to_car_park
population_density
urban_edge_flag
agricultural_land_flag
recreational_land_flag
These should initially be treated as experimental features.



7.8 Historical Wildfire Events
Build a canonical incident table.
Schema:
incident_id
incident_name
start_timestamp
end_timestamp
latitude
longitude
location_name
fire_service
incident_type
area_burned_ha
buildings_threatened
buildings_damaged
evacuations
injuries
suspected_cause
source_url
source_type
confidence
Every incident must have at least one source.




                                        8
8. Canonical Geography
Start with a UK-wide 1 km grid.
Each grid cell should have:
cell_id
geometry
centroid_lat
centroid_lon
admin_area
region
land_cover_class
Alternative:
Use H3 resolution suitable for roughly 0.5–1.5 km cells.
Whichever method is selected, use it consistently across:
  • model training
  • risk scoring
  • maps
  • historical analysis




9. Feature Engineering
For every cell and timestamp, calculate:

Weather
temperature_current
temperature_max_24h
temperature_max_3d
temperature_anomaly
relative_humidity
min_relative_humidity_24h
wind_speed
wind_gust
wind_direction

Rainfall
rain_24h
rain_7d
rain_30d
rain_60d


                                       9
rain_90d
days_since_rain
days_since_meaningful_rain
consecutive_dry_days

Drought
rainfall_vs_normal_30d
rainfall_vs_normal_60d
rainfall_vs_normal_90d
drought_percentile

Vegetation
ndvi
ndvi_anomaly
land_cover
vegetation_fraction

Ground
soil_moisture
soil_moisture_anomaly

Terrain
elevation
slope
aspect

Human exposure / ignition
distance_to_road
distance_to_buildings
distance_to_footpath
population_density
urban_edge_flag

Temporal
month
day_of_year
hour
weekend_flag
bank_holiday_flag




                             10
10. Target Variable
Initial supervised-learning target:
wildfire_within_cell_next_24h
Possible later targets:
wildfire_within_cell_next_6h
wildfire_within_cell_next_48h
wildfire_within_5km_next_24h
major_wildfire_next_24h
A “major wildfire” should eventually be formally defined, for example using:
   • area burned
   • number of appliances
   • duration
   • evacuations
   • structures threatened
Do not invent this threshold before inspecting historical data.




11. Negative Sampling
Wildfires are rare, so naive sampling will produce extreme class imbalance.
Create negatives that are:
   • from the same period
   • geographically comparable
   • similar land-cover types
   • similar broad weather regions
Example:
For each positive fire cell:
1 positive
10–50 matched negatives
Also maintain a truly random UK sample for calibration testing.
Avoid allowing control points to overlap a known fire perimeter or nearby active
incident.




                                       11
12. Model Strategy
Phase A — Baseline
Train:
  1. Logistic Regression
  2. Random Forest
  3. LightGBM
  4. XGBoost
Primary candidate:
LightGBM
Evaluate using:
  • ROC-AUC
  • PR-AUC
  • Recall at top X%
  • Precision at top X%
  • Brier score
  • Calibration curves
Because wildfire events are rare, prioritize:
PR-AUC and recall within the highest-risk cells
over raw accuracy.




13. Risk Score
Convert model probability to:
0–100 Wildfire Ignition Risk
Possible bands:
0–19   Low
20–39 Moderate
40–59 Elevated
60–79 High
80–89 Very High
90–100 Extreme
Do not hard-code these permanently.
Calibrate against historical outcome rates.




                                        12
14. Separate Ignition Risk from Severity
The UI must not collapse everything into one ambiguous number.
Display:
Ignition Risk: 91 / 100
Potential Severity: Very High
Satellite Fire Detection: None / Possible / Confirmed
Incident Status: None / Reported / Active / Controlled
This distinction is essential.




15. Explainability — “Why Here?”
For every score, store top contributing features.
Use SHAP or equivalent.
Example:
Wildfire Risk: 91/100

Top factors:
+ 59 days since meaningful rainfall
+ 30-day rainfall 87% below normal
+ Maximum temperature 34.2 C
+ Minimum humidity 27%
+ Wind gusts 36 km/h
+ Heathland vegetation
+ Residential edge within 200 m
Generate a short LLM explanation from these structured facts.
The LLM must never invent additional causes.




16. Incident NLP Pipeline
Create a component that ingests public incident reports.
Input examples:
   • Fire & Rescue Service reports
   • Council alerts
   • Police announcements
   • News reports
   • Oﬀicial social posts where legally/technically accessible


                                       13
Extract:
location
latitude
longitude
start_time
incident_type
area
evacuations
buildings_threatened
buildings_damaged
appliances
status
suspected_cause
source
confidence
Pipeline:
raw text
   |
   v
LLM structured extraction
   |
   v
Pydantic validation
   |
   v
geocoding
   |
   v
deduplication
   |
   v
incident database
Require source provenance for all extracted claims.




17. Fire Detection Fusion
When a satellite anomaly appears:
  1. Find nearest grid cell.
  2. Check local risk score.
  3. Search for existing incident reports.
  4. Associate if geographically and temporally plausible.


                                      14
    5. Increase detection confidence.
Example internal object:
{
    "location": "Cannock Chase",
    "risk_score": 92,
    "satellite_detected": true,
    "incident_reported": false,
    "confidence": "medium"
}
Do not call something a confirmed wildfire based solely on one thermal anomaly.




18. Dashboard
Main Map
Layers:
    • Wildfire ignition risk
    • Fire severity
    • Active incidents
    • Satellite detections
    • Rainfall deficit
    • Days since meaningful rain

Hover / Click Panel
Display:
Location
Ignition risk
Potential severity
Temperature
Humidity
Wind
Days since meaningful rain
Rainfall 7 / 30 / 60 days
Rainfall anomaly
Vegetation type
Nearest active fire
Satellite anomaly status
Top risk drivers




                                        15
19. PoC Case Study
Create:
notebooks/01_recent_fires_case_study.ipynb
For each initial wildfire:
  1. Geocode incident.
  2. Resolve ignition timestamp.
  3. Select nearest valid weather/rain stations.
  4. Pull historical observations.
  5. Calculate dry-spell metrics.
  6. Add vegetation and terrain variables.
  7. Generate matched control points.
  8. Calculate baseline risk.
  9. Rank all case-study locations.
 10. Visualise results.
Required output:
reports/recent_uk_wildfires_case_study.md
Include:
   • methodology
   • sources
   • data gaps
   • ranked fire locations
   • matched controls
   • charts
   • conclusions
   • limitations




20. Core Research Test
For every fire event, calculate:
percentile_of_risk_before_ignition
Example:
Stourbridge: 98.3 percentile
New Forest: 99.1 percentile
Pershore: 96.7 percentile
The key PoC question is:
      What proportion of real wildfire incidents occurred inside the
      model’s top 1%, 5%, and 10% highest-risk UK cells?


                                      16
Track:
recall_at_top_1_percent
recall_at_top_5_percent
recall_at_top_10_percent
This is more operationally meaningful than classification accuracy.




21. Database Tables
Suggested tables:
locations
grid_cells
weather_observations
rainfall_observations
soil_moisture
vegetation_features
terrain_features
fire_incidents
satellite_detections
model_features
risk_scores
model_versions
source_documents
Every derived record should include:
created_at
source
model_version




22. API Endpoints
Initial FastAPI endpoints:
GET /health

GET /risk
GET /risk/{cell_id}
GET /risk/nearby

GET /incidents
GET /incidents/{incident_id}



                                       17
GET /satellite-detections

GET /locations/{cell_id}/weather
GET /locations/{cell_id}/rainfall

POST /analysis/why-here
Example:
GET /risk/nearby?lat=52.45&lon=-2.15&radius_km=20




23. Repo Structure
wildfirewatch-uk/
|
|-- PLAN.md
|-- README.md
|-- pyproject.toml
|-- .env.example
|-- docker-compose.yml
|
|-- app/
|   |-- api/
|   |-- core/
|   |-- models/
|   |-- schemas/
|   |-- services/
|   |-- providers/
|   |   |-- weather/
|   |   |-- rainfall/
|   |   |-- satellite/
|   |   |-- vegetation/
|   |   |-- terrain/
|   |   `-- incidents/
|   |
|   |-- features/
|   |-- ml/
|   `-- utils/
|
|-- data/
|   |-- raw/
|   |-- interim/
|   `-- processed/



                               18
|
|-- notebooks/
|   |-- 01_recent_fires_case_study.ipynb
|   |-- 02_negative_sampling.ipynb
|   |-- 03_baseline_model.ipynb
|   `-- 04_model_explainability.ipynb
|
|-- scripts/
|   |-- ingest_weather.py
|   |-- ingest_rainfall.py
|   |-- ingest_firms.py
|   |-- ingest_incidents.py
|   |-- build_features.py
|   |-- train_model.py
|   `-- score_uk.py
|
|-- tests/
|
`-- reports/




24. Environment Variables
Create .env.example:
DATABASE_URL=
MET_OFFICE_API_KEY=
NASA_FIRMS_API_KEY=
GEOCODER_API_KEY=
LLM_API_KEY=
APP_ENV=development
LOG_LEVEL=INFO
Never commit secrets.




25. Development Phases
Phase 0 — Project Bootstrap
Tasks:
  □ Create repository structure.
  □ Create Python environment.
  □ Add formatting/linting.


                                   19
   □ Configure PostgreSQL/PostGIS.
   □ Create database migrations.
   □ Add .env.example.
   □ Add logging.
   □ Add basic FastAPI health endpoint.
Exit criteria:
docker compose up
starts the API and database successfully.



Phase 1 — Incident Dataset
Tasks:
   □ Build canonical wildfire incident schema.
   □ Add the initial August 2026 case-study fires.
   □ Record source URLs and confidence.
   □ Resolve coordinates and ignition times.
   □ Add deduplication logic.
Exit criteria:
At least 8 verified incidents are queryable from the database.



Phase 2 — Rainfall Pipeline
Tasks:
   □ Implement rainfall provider.
   □ Retrieve nearest station/gauge.
   □ Store raw observations.
   □ Calculate rainfall windows.
   □ Calculate days since rain.
   □ Calculate days since meaningful rain.
   □ Calculate consecutive dry days.
Exit criteria:
For each case-study location, produce:
rain_24h
rain_7d
rain_30d
rain_60d
days_since_rain
days_since_meaningful_rain


                                      20
with source provenance.



Phase 3 — Weather Pipeline
Tasks:
   □ Implement weather provider.
   □ Retrieve historical observations.
   □ Retrieve forecasts.
   □ Resolve station-to-grid mapping.
   □ Store temperature, humidity, and wind.
Exit criteria:
A complete weather feature row exists for every case-study incident.



Phase 4 — Geospatial Context
Tasks:
   □ Build UK grid.
   □ Add land-cover classification.
   □ Add elevation.
   □ Add slope.
   □ Add road/building proximity.
   □ Associate incidents to grid cells.
Exit criteria:
Every case-study cell has static geospatial features.



Phase 5 — Control Locations
Tasks:
   □ Generate 100+ non-fire controls.
   □ Match by season.
   □ Match by broad geography.
   □ Match by land-cover class.
   □ Prevent spatial leakage around known fires.
Exit criteria:
Training dataset has valid positive and negative examples.




                                          21
Phase 6 — Baseline Analysis
Tasks:
   □ Produce descriptive statistics.
   □ Compare fire vs control dryness.
   □ Compare fire vs control temperature.
   □ Compare humidity.
   □ Compare wind.
   □ Plot distributions.
   □ Calculate correlations.
Exit criteria:
Case-study report clearly identifies whether obvious signal exists before ML.



Phase 7 — Baseline ML
Tasks:
   □ Logistic Regression.
   □ LightGBM.
   □ XGBoost.
   □ Cross-validation.
   □ Probability calibration.
   □ Rank cells.
   □ Calculate recall@top1/5/10%.
Exit criteria:
Model is measurably better than random and produces calibrated risk scores.



Phase 8 — Explainability
Tasks:
   □ Add SHAP.
   □ Store top feature contributions.
   □ Build “Why Here?” response.
   □ Add LLM explanation from structured SHAP output.
Exit criteria:
Every model score can be explained from stored features.




                                      22
Phase 9 — Satellite Detection
Tasks:
   □ Build FIRMS ingestion.
   □ Store thermal anomalies.
   □ Match anomalies to cells.
   □ Match anomalies to incidents.
   □ Display confidence status.
Exit criteria:
Recent satellite detections appear on the map.



Phase 10 — Dashboard
Tasks:
   □ UK risk map.
   □ Fire incident markers.
   □ Satellite anomaly layer.
   □ Rainfall-deficit layer.
   □ Location detail panel.
   □ “Why Here?” explanation.
Exit criteria:
A user can visually inspect current and historical wildfire conditions.




26. Testing
Required tests:

Unit
   • rainfall aggregation
   • dry-day calculation
   • station selection
   • feature calculations
   • incident parsing
   • geospatial distance
   • risk band mapping

Integration
   • provider ingestion


                                       23
  • DB writes
  • model scoring
  • API response validation

ML
  • no future-data leakage
  • training/test separation
  • probability calibration
  • feature schema compatibility
  • model-version reproducibility




27. Data Leakage Rules
Never allow data after ignition time into pre-fire prediction features.
For an incident at:
2026-08-13 16:30
all model features must use data available at or before:
2026-08-13 16:29
Forecast features are allowed only if they were genuinely available before igni-
tion.




28. Safety / Product Guardrails
The system must clearly state:
     This is an experimental decision-support tool and is not an oﬀicial
     emergency warning service.
Never advise evacuation based solely on model output.
For active incidents, direct users to:
  • emergency services
  • local Fire & Rescue Service
  • oﬀicial government alerts
Do not describe satellite anomaly detections as confirmed wildfires without cor-
roboration.
Display timestamps and data freshness prominently.



                                         24
29. Logging and Provenance
Every external observation should track:
source_name
source_url_or_identifier
observation_timestamp
retrieved_at
raw_value
processed_value
processing_version
Every model prediction should track:
model_version
feature_version
prediction_timestamp
target_timestamp
risk_probability
risk_score
top_features




30. Agent Working Rules
Hermes should:
  1. Work phase by phase.
  2. Commit small logical changes.
  3. Do not skip tests for core feature calculations.
  4. Preserve raw source data.
  5. Never overwrite raw observations with derived data.
  6. Record assumptions in DECISIONS.md.
  7. Record unresolved issues in ISSUES.md.
  8. Update this PLAN.md checklist as tasks are completed.
  9. Prefer the simplest working implementation.
 10. Avoid premature cloud infrastructure.




31. First Execution Sprint
Hermes should begin with this exact order:

Task 1
Bootstrap repository.


                                       25
Task 2
Create incident schema and enter the initial August 2026 wildfire events.

Task 3
Implement rainfall ingestion.

Task 4
For each incident calculate:
days_since_rain
days_since_meaningful_rain
rain_7d
rain_30d
rain_60d

Task 5
Create a table:
incident
ignition_time
temperature
humidity
wind
days_since_meaningful_rain
rain_30d
rain_60d

Task 6
Select 100 matched non-fire locations.

Task 7
Run descriptive analysis.

Task 8
Train Logistic Regression baseline.

Task 9
Train LightGBM.




                                         26
Task 10
Report:
ROC-AUC
PR-AUC
Recall@Top1%
Recall@Top5%
Recall@Top10%

Task 11
Generate SHAP feature importance.

Task 12
Write:
reports/recent_uk_wildfires_case_study.md




32. Go / No-Go Decision
After the first case study, answer:

GO
Continue if:
  • wildfire locations consistently rank high before ignition;
  • useful signal exists beyond temperature alone;
  • rainfall/dryness and wind contribute meaningful predictive value;
  • the model generalises across regions;
  • data availability supports repeatable live scoring.

NO-GO / REWORK
Pause or redesign if:
  • predictions are effectively random;
  • results depend on leaked future information;
  • model works only for one fire type or region;
  • required data is too delayed for operational use;
  • model is dominated by unreliable proxy variables.




                                      27
33. Phase 2 Product Ideas
Only after the PoC succeeds:
  • Live UK wildfire-risk map
  • Hourly risk scoring
  • Local authority dashboards
  • Fire service intelligence view
  • Automated high-risk area reports
  • Satellite anomaly alerts
  • Incident NLP ingestion
  • Mobile notifications
  • Risk history charts
  • API access




34. Future Research
Later investigate:
  • Fire spread simulation
  • Cellular automata
  • Graph-based spread models
  • Physics-informed ML
  • Wind-driven propagation
  • Peat-fire persistence
  • Fuel moisture estimation
  • Satellite image segmentation
  • Camera-based smoke detection
  • Drone imagery
  • Lightning ignition
  • Human ignition likelihood
  • Climate projections
Fire-spread modelling must remain separate from ignition-risk modelling.




35. Immediate Deliverable
The immediate goal is not a full production platform.
The immediate goal is:
     Build a reproducible retrospective dataset for the August 2026 UK
     wildfires and determine whether wildfire locations could have been
     identified as unusually high-risk before ignition.


                                     28
Everything else depends on proving that signal first.




                                      29
