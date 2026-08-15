from __future__ import annotations

import math
from dataclasses import dataclass

from pydantic import BaseModel


class FeatureDatasetRow(BaseModel):
    sample_id: str
    target: int
    temperature_2m_c: float | None
    relative_humidity_2m_pct: float | None
    wind_speed_10m_mps: float | None
    wind_gust_10m_mps: float | None
    rain_24h_mm: float
    rain_7d_mm: float
    rain_30d_mm: float
    rain_60d_mm: float
    days_since_rain: int | None
    days_since_meaningful_rain: int | None


class ScoredDatasetRow(FeatureDatasetRow):
    risk_score: float


@dataclass(frozen=True)
class BaselineEvaluation:
    sample_count: int
    positive_count: int
    recall_at_top_percent: dict[int, float]
    scored_rows: list[ScoredDatasetRow]


def _bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _norm_high(value: float | None, *, high: float) -> float:
    if value is None:
        return 0.0
    return _bounded(value / high, 0.0, 1.0)


def _norm_low(value: float | None, *, low: float, high: float) -> float:
    if value is None:
        return 0.0
    return 1.0 - _bounded((value - low) / (high - low), 0.0, 1.0)


def score_baseline_risk(row: FeatureDatasetRow) -> float:
    """Transparent heuristic baseline before learned ML models.

    Scores higher for hot, dry, low-humidity, windy conditions. This gives us a
    deterministic ranking baseline while the positive dataset is still tiny.
    """

    components = [
        0.25 * _norm_high(row.temperature_2m_c, high=40.0),
        0.20 * _norm_low(row.relative_humidity_2m_pct, low=15.0, high=85.0),
        0.15 * _norm_high(row.wind_gust_10m_mps, high=20.0),
        0.15 * _norm_low(row.rain_7d_mm, low=0.0, high=25.0),
        0.15 * _norm_low(row.rain_30d_mm, low=0.0, high=80.0),
        0.10 * _norm_high(row.days_since_meaningful_rain, high=21.0),
    ]
    return round(_bounded(sum(components) * 100, 0.0, 100.0), 3)


def evaluate_baseline_ranking(
    rows: list[FeatureDatasetRow], *, top_percentages: tuple[int, ...] = (1, 5, 10)
) -> BaselineEvaluation:
    scored_rows = [
        ScoredDatasetRow(**row.model_dump(), risk_score=score_baseline_risk(row)) for row in rows
    ]
    ranked = sorted(scored_rows, key=lambda row: row.risk_score, reverse=True)
    positive_count = sum(row.target for row in ranked)
    recall_at_top_percent: dict[int, float] = {}
    for percentage in top_percentages:
        cutoff = max(1, math.ceil(len(ranked) * percentage / 100))
        positives_in_bucket = sum(row.target for row in ranked[:cutoff])
        recall_at_top_percent[percentage] = (
            0.0 if positive_count == 0 else round(positives_in_bucket / positive_count, 6)
        )
    return BaselineEvaluation(
        sample_count=len(rows),
        positive_count=positive_count,
        recall_at_top_percent=recall_at_top_percent,
        scored_rows=ranked,
    )
