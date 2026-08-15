from __future__ import annotations

import math
from dataclasses import dataclass

from pydantic import BaseModel

from wildfirewatch_uk.ml.baseline import FeatureDatasetRow, ScoredDatasetRow

FEATURE_NAMES = (
    "temperature_2m_c_norm",
    "low_relative_humidity_norm",
    "wind_speed_10m_mps_norm",
    "wind_gust_10m_mps_norm",
    "rain_7d_dryness_norm",
    "rain_30d_dryness_norm",
    "rain_60d_dryness_norm",
    "days_since_meaningful_rain_norm",
)


class LogisticBaselineModel(BaseModel):
    feature_names: tuple[str, ...]
    weights: list[float]
    bias: float
    epochs: int
    learning_rate: float

    def predict_proba(self, features: list[float]) -> float:
        linear = self.bias + sum(
            weight * value for weight, value in zip(self.weights, features, strict=True)
        )
        return _sigmoid(linear)


@dataclass(frozen=True)
class TrainableBaselineEvaluation:
    sample_count: int
    positive_count: int
    recall_at_top_percent: dict[int, float]
    roc_auc: float | None
    pr_auc: float | None
    model: LogisticBaselineModel
    scored_rows: list[ScoredDatasetRow]


def _bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _norm_high(value: float | int | None, *, high: float) -> float:
    if value is None:
        return 0.0
    return _bounded(float(value) / high, 0.0, 1.0)


def _norm_low(value: float | int | None, *, low: float, high: float) -> float:
    if value is None:
        return 0.0
    return 1.0 - _bounded((float(value) - low) / (high - low), 0.0, 1.0)


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def featurize_row(row: FeatureDatasetRow) -> list[float]:
    """Convert a feature row into bounded numeric features for logistic regression."""

    return [
        _norm_high(row.temperature_2m_c, high=40.0),
        _norm_low(row.relative_humidity_2m_pct, low=15.0, high=85.0),
        _norm_high(row.wind_speed_10m_mps, high=12.0),
        _norm_high(row.wind_gust_10m_mps, high=25.0),
        _norm_low(row.rain_7d_mm, low=0.0, high=40.0),
        _norm_low(row.rain_30d_mm, low=0.0, high=120.0),
        _norm_low(row.rain_60d_mm, low=0.0, high=200.0),
        _norm_high(row.days_since_meaningful_rain, high=30.0),
    ]


def train_logistic_regression(
    rows: list[FeatureDatasetRow],
    *,
    epochs: int = 1000,
    learning_rate: float = 0.4,
    l2_penalty: float = 0.01,
) -> LogisticBaselineModel:
    """Train a tiny dependency-free logistic regression baseline.

    This is intentionally lightweight and deterministic so the PoC can produce a
    trained baseline without forcing heavy ML dependencies in default CI. It is
    not a replacement for a later scikit-learn/LightGBM experiment.
    """

    if not rows:
        raise ValueError("at least one row is required")
    targets = {row.target for row in rows}
    if targets != {0, 1}:
        raise ValueError("training rows must include both positive and control samples")

    feature_matrix = [featurize_row(row) for row in rows]
    labels = [row.target for row in rows]
    weights = [0.0] * len(FEATURE_NAMES)
    bias = 0.0
    sample_count = len(rows)

    for _ in range(epochs):
        grad_weights = [0.0] * len(weights)
        grad_bias = 0.0
        for features, label in zip(feature_matrix, labels, strict=True):
            prediction = _sigmoid(
                bias + sum(w * x for w, x in zip(weights, features, strict=True))
            )
            error = prediction - label
            grad_bias += error
            for index, value in enumerate(features):
                grad_weights[index] += error * value
        bias -= learning_rate * grad_bias / sample_count
        for index, weight in enumerate(weights):
            gradient = (grad_weights[index] / sample_count) + l2_penalty * weight
            weights[index] -= learning_rate * gradient

    return LogisticBaselineModel(
        feature_names=FEATURE_NAMES,
        weights=[round(weight, 6) for weight in weights],
        bias=round(bias, 6),
        epochs=epochs,
        learning_rate=learning_rate,
    )


def _roc_auc(scored_rows: list[ScoredDatasetRow]) -> float | None:
    positives = [row.risk_score for row in scored_rows if row.target == 1]
    negatives = [row.risk_score for row in scored_rows if row.target == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    comparisons = 0
    for positive in positives:
        for negative in negatives:
            comparisons += 1
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return round(wins / comparisons, 6)


def _average_precision(scored_rows: list[ScoredDatasetRow]) -> float | None:
    ranked = sorted(scored_rows, key=lambda row: row.risk_score, reverse=True)
    positive_count = sum(row.target for row in ranked)
    if positive_count == 0:
        return None
    precision_sum = 0.0
    positives_seen = 0
    for rank, row in enumerate(ranked, start=1):
        if row.target == 1:
            positives_seen += 1
            precision_sum += positives_seen / rank
    return round(precision_sum / positive_count, 6)


def evaluate_trainable_logistic_baseline(
    rows: list[FeatureDatasetRow],
    *,
    top_percentages: tuple[int, ...] = (10, 20, 50, 100),
    epochs: int = 1200,
    learning_rate: float = 0.45,
) -> TrainableBaselineEvaluation:
    model = train_logistic_regression(rows, epochs=epochs, learning_rate=learning_rate)
    scored_rows = [
        ScoredDatasetRow(
            **row.model_dump(), risk_score=round(model.predict_proba(featurize_row(row)) * 100, 3)
        )
        for row in rows
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

    return TrainableBaselineEvaluation(
        sample_count=len(rows),
        positive_count=positive_count,
        recall_at_top_percent=recall_at_top_percent,
        roc_auc=_roc_auc(ranked),
        pr_auc=_average_precision(ranked),
        model=model,
        scored_rows=ranked,
    )
