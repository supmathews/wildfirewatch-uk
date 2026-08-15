from __future__ import annotations

from dataclasses import dataclass

from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.ml.out_of_sample import (
    LeaveOneIncidentOutEvaluation,
    evaluate_leave_one_incident_out,
)

FEATURE_FAMILIES = (
    "all",
    "latest_weather",
    "rainfall_windows",
    "dry_spell_memory",
    "rainfall_and_dry_spell",
)


@dataclass(frozen=True)
class FeatureFamilyEvaluation:
    family: str
    sample_count: int
    positive_count: int
    evaluation: LeaveOneIncidentOutEvaluation


def ablate_row(row: FeatureDatasetRow, family: str) -> FeatureDatasetRow:
    if family not in FEATURE_FAMILIES:
        raise ValueError(f"unknown feature family: {family}")
    if family == "all":
        return row

    keep_latest_weather = family == "latest_weather"
    keep_rainfall = family in {"rainfall_windows", "rainfall_and_dry_spell"}
    keep_dry_spell = family in {"dry_spell_memory", "rainfall_and_dry_spell"}

    return FeatureDatasetRow(
        sample_id=row.sample_id,
        target=row.target,
        temperature_2m_c=row.temperature_2m_c if keep_latest_weather else None,
        relative_humidity_2m_pct=row.relative_humidity_2m_pct if keep_latest_weather else None,
        wind_speed_10m_mps=row.wind_speed_10m_mps if keep_latest_weather else None,
        wind_gust_10m_mps=row.wind_gust_10m_mps if keep_latest_weather else None,
        rain_24h_mm=row.rain_24h_mm if keep_rainfall else 0.0,
        rain_7d_mm=row.rain_7d_mm if keep_rainfall else 0.0,
        rain_30d_mm=row.rain_30d_mm if keep_rainfall else 0.0,
        rain_60d_mm=row.rain_60d_mm if keep_rainfall else 0.0,
        days_since_rain=row.days_since_rain if keep_dry_spell else None,
        days_since_meaningful_rain=row.days_since_meaningful_rain if keep_dry_spell else None,
    )


def evaluate_feature_families(
    rows: list[FeatureDatasetRow],
    *,
    families: tuple[str, ...] = FEATURE_FAMILIES,
    epochs: int = 1200,
    learning_rate: float = 0.45,
) -> list[FeatureFamilyEvaluation]:
    results: list[FeatureFamilyEvaluation] = []
    for family in families:
        ablated_rows = [ablate_row(row, family) for row in rows]
        evaluation = evaluate_leave_one_incident_out(
            ablated_rows, epochs=epochs, learning_rate=learning_rate
        )
        results.append(
            FeatureFamilyEvaluation(
                family=family,
                sample_count=len(ablated_rows),
                positive_count=sum(row.target for row in ablated_rows),
                evaluation=evaluation,
            )
        )
    return results
