# WildfireWatch UK

AI-assisted wildfire risk and situational intelligence for the UK.

> **Status:** pre-alpha proof of concept. This is an experimental decision-support and research project, **not** an official emergency-warning service.

## Goal

WildfireWatch UK aims to test whether recent UK wildfire locations could have been ranked as unusually high-risk before ignition using historical weather, rainfall deficit, vegetation/fuel, terrain, and land-use context.

The first milestone is a reproducible retrospective case study, not live public alerting.

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
