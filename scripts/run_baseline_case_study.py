from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

from wildfirewatch_uk.features.controls import ControlLocation, generate_matched_controls
from wildfirewatch_uk.features.weather import (
    IncidentWeatherFeatures,
    build_incident_weather_features,
)
from wildfirewatch_uk.ml.baseline import (
    FeatureDatasetRow,
    evaluate_baseline_ranking,
)
from wildfirewatch_uk.providers.weather.open_meteo import OpenMeteoArchiveClient
from wildfirewatch_uk.services.incident_weather_dataset import build_features_for_seed_incidents


def _dataset_row_from_features(
    features: IncidentWeatherFeatures, *, target: int
) -> FeatureDatasetRow:
    return FeatureDatasetRow(
        sample_id=features.incident_id,
        target=target,
        temperature_2m_c=features.temperature_2m_c,
        relative_humidity_2m_pct=features.relative_humidity_2m_pct,
        wind_speed_10m_mps=features.wind_speed_10m_mps,
        wind_gust_10m_mps=features.wind_gust_10m_mps,
        rain_24h_mm=features.rain_24h_mm,
        rain_7d_mm=features.rain_7d_mm,
        rain_30d_mm=features.rain_30d_mm,
        rain_60d_mm=features.rain_60d_mm,
        days_since_rain=features.days_since_rain,
        days_since_meaningful_rain=features.days_since_meaningful_rain,
    )


def _features_for_control(
    control: ControlLocation,
    *,
    client: OpenMeteoArchiveClient,
    lookback_days: int,
) -> IncidentWeatherFeatures:
    target_timestamp = control.target_timestamp
    start_date = (target_timestamp - timedelta(days=lookback_days)).date()
    observations = client.fetch_hourly_weather(
        latitude=control.latitude,
        longitude=control.longitude,
        start_date=start_date,
        end_date=target_timestamp.date(),
    )
    pseudo_incident = _pseudo_incident_from_control(control)
    return build_incident_weather_features(pseudo_incident, observations)


def _pseudo_incident_from_control(control: ControlLocation):
    from wildfirewatch_uk.schemas.incident import IncidentRecord, IncidentSource

    return IncidentRecord(
        incident_id=control.control_id,
        incident_name=control.control_id,
        start_timestamp=control.target_timestamp,
        latitude=control.latitude,
        longitude=control.longitude,
        location_name=control.control_id,
        incident_type="control",
        sources=[
            IncidentSource(
                url="https://github.com/supmathews/wildfirewatch-uk",
                source_type="placeholder",
                title="Generated non-fire control point",
            )
        ],
    )


def run_baseline_case_study(
    *, controls_per_incident: int, seed: int, lookback_days: int
):
    client = OpenMeteoArchiveClient()
    incident_features = build_features_for_seed_incidents(
        lookback_days=lookback_days, client=client
    )
    controls = generate_matched_controls(
        incident_features, controls_per_incident=controls_per_incident, seed=seed
    )
    control_features = [
        _features_for_control(control, client=client, lookback_days=lookback_days)
        for control in controls
    ]
    rows = [_dataset_row_from_features(row, target=1) for row in incident_features]
    rows.extend(_dataset_row_from_features(row, target=0) for row in control_features)
    return evaluate_baseline_ranking(rows, top_percentages=(10, 20, 50, 100))


def write_report(evaluation, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    recall_lines = "\n".join(
        f"- Recall@Top{percentage}%: {recall:.3f}"
        for percentage, recall in evaluation.recall_at_top_percent.items()
    )
    top_rows = "\n".join(
        f"| {index} | {row.sample_id} | {row.target} | {row.risk_score:.3f} |"
        for index, row in enumerate(evaluation.scored_rows[:10], start=1)
    )
    output_path.write_text(
        f"""# Baseline retrospective ranking preview

This is an early heuristic baseline using currently usable incidents and generated regional
controls. Controls use the `regional_offset_min_distance_v2` sampler, which keeps them at
least 20 km from all known incident points. It is **not** the final proof of concept: the
positive dataset is still tiny, controls are rough regional offsets, and the scoring
function is a transparent heuristic rather than a trained model.

## Dataset

- Samples: {evaluation.sample_count}
- Positive incident samples: {evaluation.positive_count}
- Control samples: {evaluation.sample_count - evaluation.positive_count}

## Ranking metrics

{recall_lines}

## Top ranked samples

| rank | sample_id | target | risk_score |
|---:|---|---:|---:|
{top_rows}

## Interpretation

This run verifies the end-to-end path: incident features, matched control generation,
control weather retrieval, combined dataset assembly, and baseline ranking. The next
iteration should increase verified positive incidents, replace rough min-distance controls
with land-cover/region-matched controls, and train Logistic Regression / LightGBM once the
dataset is large enough.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a first baseline wildfire-risk ranking.")
    parser.add_argument("--controls-per-incident", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument(
        "--output", default="reports/baseline_retrospective_ranking_preview.md"
    )
    args = parser.parse_args()

    evaluation = run_baseline_case_study(
        controls_per_incident=args.controls_per_incident,
        seed=args.seed,
        lookback_days=args.lookback_days,
    )
    write_report(evaluation, Path(args.output))
    print(f"wrote baseline report to {args.output}")
    print(f"samples={evaluation.sample_count} positives={evaluation.positive_count}")
    print(evaluation.recall_at_top_percent)


if __name__ == "__main__":
    main()
