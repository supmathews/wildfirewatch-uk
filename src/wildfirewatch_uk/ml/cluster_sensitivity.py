from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel

from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.ml.out_of_sample import (
    evaluate_leave_one_incident_out,
    incident_group_id,
)


class ClusterSensitivityScenario(BaseModel):
    name: str
    excluded_group_ids: list[str]
    sample_count: int
    positive_count: int
    fold_count: int
    roc_auc: float | None
    pr_auc: float | None
    recall_at_top_percent: dict[int, float]


def filter_rows_by_excluded_groups(
    rows: Iterable[FeatureDatasetRow], *, excluded_group_ids: set[str]
) -> list[FeatureDatasetRow]:
    return [row for row in rows if incident_group_id(row) not in excluded_group_ids]


def evaluate_cluster_sensitivity(
    rows: list[FeatureDatasetRow],
    *,
    exclusions: dict[str, set[str]],
    epochs: int = 1200,
    learning_rate: float = 0.45,
) -> list[ClusterSensitivityScenario]:
    scenarios: list[ClusterSensitivityScenario] = []
    for name, excluded_group_ids in exclusions.items():
        scenario_rows = filter_rows_by_excluded_groups(
            rows, excluded_group_ids=excluded_group_ids
        )
        evaluation = evaluate_leave_one_incident_out(
            scenario_rows,
            epochs=epochs,
            learning_rate=learning_rate,
        )
        scenarios.append(
            ClusterSensitivityScenario(
                name=name,
                excluded_group_ids=sorted(excluded_group_ids),
                sample_count=evaluation.sample_count,
                positive_count=evaluation.positive_count,
                fold_count=evaluation.fold_count,
                roc_auc=evaluation.roc_auc,
                pr_auc=evaluation.pr_auc,
                recall_at_top_percent=evaluation.recall_at_top_percent,
            )
        )
    return scenarios
