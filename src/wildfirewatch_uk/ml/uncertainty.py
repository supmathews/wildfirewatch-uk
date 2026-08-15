from __future__ import annotations

import random
from dataclasses import dataclass

from wildfirewatch_uk.ml.baseline import ScoredDatasetRow
from wildfirewatch_uk.ml.out_of_sample import _average_precision, _roc_auc

SUPPORTED_BOOTSTRAP_METRICS = ("roc_auc", "pr_auc")


@dataclass(frozen=True)
class BootstrapMetricInterval:
    metric: str
    point_estimate: float | None
    lower: float | None
    upper: float | None
    confidence_level: float
    sample_count: int
    iterations: int
    valid_resamples: int
    skipped_resamples: int


def _metric_value(rows: list[ScoredDatasetRow], metric: str) -> float | None:
    if metric == "roc_auc":
        return _roc_auc(rows)
    if metric == "pr_auc":
        return _average_precision(rows)
    raise ValueError(f"unsupported bootstrap metric: {metric}")


def _percentile(sorted_values: list[float], percentile: float) -> float:
    if not sorted_values:
        raise ValueError("at least one value is required")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * percentile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = position - lower_index
    lower = sorted_values[lower_index]
    upper = sorted_values[upper_index]
    return lower + (upper - lower) * fraction


def bootstrap_metric_interval(
    rows: list[ScoredDatasetRow],
    *,
    metric: str,
    iterations: int = 500,
    confidence_level: float = 0.90,
    seed: int = 42,
) -> BootstrapMetricInterval:
    if metric not in SUPPORTED_BOOTSTRAP_METRICS:
        raise ValueError(f"metric must be one of {SUPPORTED_BOOTSTRAP_METRICS}")
    if not rows:
        raise ValueError("at least one scored row is required")
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be in (0, 1)")

    point_estimate = _metric_value(rows, metric)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(iterations):
        sample = [rows[rng.randrange(len(rows))] for _ in rows]
        value = _metric_value(sample, metric)
        if value is not None:
            values.append(value)

    if values:
        values.sort()
        alpha = (1.0 - confidence_level) / 2.0
        lower = round(_percentile(values, alpha), 6)
        upper = round(_percentile(values, 1.0 - alpha), 6)
    else:
        lower = None
        upper = None

    return BootstrapMetricInterval(
        metric=metric,
        point_estimate=point_estimate,
        lower=lower,
        upper=upper,
        confidence_level=confidence_level,
        sample_count=len(rows),
        iterations=iterations,
        valid_resamples=len(values),
        skipped_resamples=iterations - len(values),
    )


def bootstrap_metric_intervals(
    rows: list[ScoredDatasetRow],
    *,
    metrics: tuple[str, ...] = SUPPORTED_BOOTSTRAP_METRICS,
    iterations: int = 500,
    confidence_level: float = 0.90,
    seed: int = 42,
) -> list[BootstrapMetricInterval]:
    return [
        bootstrap_metric_interval(
            rows,
            metric=metric,
            iterations=iterations,
            confidence_level=confidence_level,
            seed=seed,
        )
        for metric in metrics
    ]
