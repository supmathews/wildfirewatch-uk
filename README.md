# WildfireWatch UK

AI-assisted wildfire risk and situational intelligence for the UK.

> **Status:** pre-alpha proof of concept. This is an experimental decision-support and research project, **not** an official emergency-warning service.

## Goal

WildfireWatch UK aims to test whether recent UK wildfire locations could have been ranked as unusually high-risk before ignition using historical weather, rainfall deficit, vegetation/fuel, terrain, and land-use context.

The first milestone is a reproducible retrospective case study, not live public alerting.

## Landscape findings and positioning

WildfireWatch UK is being developed against a landscape of wildfire occurrence,
fuel-ignitability, severity, detection, burned-area and spread-modelling systems.
The project deliberately keeps these targets separate so that a retrospective
occurrence-risk PoC is not overstated as an operational warning product.

| Finding | WildfireWatch interpretation | Citations |
|---|---|---|
| Scotland-specific ML wildfire occurrence / susceptibility work is now a close UK benchmark. | Treat Scotland as a formal geographic-transfer and calibration experiment; do not assume England/Wales weather-dryness signals transfer cleanly. | [EGU26-22119][egu-scotland]; [Scotland transfer roadmap](reports/scotland_geographic_transfer_roadmap.md) |
| FireInSite-style UK fuel ignitability / behaviour work is complementary, not the same target. | Use fuel ignitability and behaviour as inputs or benchmarks, while keeping actual event occurrence probability separate. | [Landscape differentiation report](reports/landscape_differentiation_findings.md); [Scotland transfer roadmap](reports/scotland_geographic_transfer_roadmap.md) |
| ECMWF Probability-of-Fire style work is a direct occurrence-probability benchmark. | Compare evaluation philosophy and avoid claiming probability calibration from case-control scores without prevalence correction. | [External repo lessons](reports/external_repo_lessons_not_code.md); [ECMWF Code for Earth wildfire forecasting][ecmwf-wildfire] |
| Met Office Fire Severity Index and EFFIS are important operational/fire-danger references. | Treat them as severity/danger baselines, not proof that this project predicts actual wildfire occurrence. | [Met Office Fire Severity Index][metoffice-fsi]; [EFFIS][effis] |
| Space Park Leicester / EO wildfire work is best viewed as a detection and mapping layer. | Satellite/EO detections can support confirmation and incident intelligence, but must not leak into pre-ignition features unless strictly lagged. | [Space Park Leicester][space-park]; [Landscape differentiation report](reports/landscape_differentiation_findings.md) |
| International datasets and model references raise the validation bar. | Use geographic/temporal holdouts, PR-AUC, Recall@Top-X%, calibration, uncertainty, feature ablations, and explainability before making go/no-go claims. | [CanadaFireSat][canadafiresat]; [CanadaFireSat data][canadafiresat-data]; [Mesogeos][mesogeos]; [Mesogeos code][mesogeos-code]; [ECMWF wildfire-forecasting][ecmwf-wildfire]; [Orion wildfire forecasting][orion-wildfire] |

The broader landscape watchlist also tracks WISP, mmFire / BCWildfire,
WILDFIRE-FM, TerraWise, OlmoEarth, FireCastRL and WildFireGS as future comparison
or architecture references; these are recorded in the landscape-review reports,
but direct README links should only be added once their public source URLs are
verified.

Current proof status is still deliberately modest: the project has a working
retrospective pipeline and early diagnostic signals, but only a tiny positive
dataset. Current reports track incident readiness, country/nation labels,
cluster sensitivity, temporal controls, land-cover-matched controls, calibration,
risk bands and bootstrap uncertainty under `reports/`.

## Initial PoC questions

- Were wildfire locations unusually high-risk relative to comparable UK locations before ignition?
- What proportion of real wildfire incidents occurred inside the model's top 1%, 5%, and 10% highest-risk UK cells?
- Do rainfall/dryness and wind add useful signal beyond temperature alone?

## Safety guardrails

- Do not use this project to make evacuation decisions.
- Do not treat model scores as official warnings.
- Do not describe satellite thermal anomalies as confirmed wildfires without corroboration.
- For active incidents, follow emergency services, local Fire & Rescue Service, and official government guidance.

## Quick start

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn wildfirewatch_uk.main:app --reload
```

Then open <http://127.0.0.1:8000/health>.

## Development roadmap

The canonical roadmap is in [`PLAN.md`](PLAN.md). The first execution sprint is:

1. Bootstrap repository.
2. Create incident schema and enter initial August 2026 wildfire events.
3. Implement rainfall ingestion.
4. Calculate dry-spell metrics.
5. Build a case-study table and report.

## Repository layout

```text
src/wildfirewatch_uk/       Python package
  api/                      FastAPI routers
  core/                     settings/logging
  schemas/                  Pydantic schemas
  providers/                Swappable data providers
  features/                 feature engineering
  ml/                       model training/scoring
notebooks/                  exploratory analysis
scripts/                    CLI/data jobs
data/                       local raw/interim/processed data (gitignored)
reports/                    case-study outputs
```

## Contributing

Contributions are welcome once the project is public. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md).

[canadafiresat]: https://arxiv.org/abs/2506.08690
[canadafiresat-data]: https://github.com/eceo-epfl/CanadaFireSat-Data
[ecmwf-wildfire]: https://github.com/ECMWFCode4Earth/wildfire-forecasting
[effis]: https://forest-fire.emergency.copernicus.eu/
[egu-scotland]: https://meetingorganizer.copernicus.org/EGU26/EGU26-22119.html
[mesogeos]: https://arxiv.org/abs/2306.05144
[mesogeos-code]: https://github.com/Orion-AI-Lab/mesogeos
[metoffice-fsi]: https://www.metoffice.gov.uk/services/government/environmental-hazard-resilience/fire-severity-index
[orion-wildfire]: https://github.com/Orion-AI-Lab/wildfire_forecasting
[space-park]: https://www.space-park.co.uk/
