from __future__ import annotations

import math
from dataclasses import dataclass

from pydantic import BaseModel

from wildfirewatch_uk.ml.baseline import FeatureDatasetRow, ScoredDatasetRow
from wildfirewatch_uk.ml.trainable_baseline import featurize_row, train_logistic_regression


class FoldMetric(BaseModel):
    held_out_incident_id: str
    train_sample_count: int
    test_sample_count: int
    positive_rank: int | None
    positive_score: float | None
    recall_at_top_percent: dict[int, float]


@dataclass(frozen=True)
class LeaveOneIncidentOutEvaluation:
    sample_count: int
    positive_count: int
    fold_count: int
    recall_at_top_percent: dict[int, float]
    roc_auc: float | None
    pr_auc: float | None
    fold_metrics: dict[str, FoldMetric]
    scored_rows: list[ScoredDatasetRow]


def incident_group_id(row: FeatureDatasetRow) -> str:
    """Return the positive incident group a row belongs to."""

    if row.sample_id.startswith("control-"):
        return row.sample_id.removeprefix("control-").rsplit("-", 1)[0]
    return row.sample_id


def _positive_group_ids(rows: list[FeatureDatasetRow]) -> list[str]:
    return sorted(incident_group_id(row) for row in rows if row.target == 1)


def _recall_at_top(
    ranked: list[ScoredDatasetRow], top_percentages: tuple[int, ...]
) -> dict[int, float]:
    positive_count = sum(row.target for row in ranked)
    recall: dict[int, float] = {}
    for percentage in top_percentages:
        cutoff = max(1, math.ceil(len(ranked) * percentage / 100))
        positives_in_bucket = sum(row.target for row in ranked[:cutoff])
        recall[percentage] = (
            0.0 if positive_count == 0 else round(positives_in_bucket / positive_count, 6)
        )
    return recall


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


def _score_rows(
    model_rows: list[FeatureDatasetRow],
    test_rows: list[FeatureDatasetRow],
    *,
    epochs: int,
    learning_rate: float,
) -> list[ScoredDatasetRow]:
    model = train_logistic_regression(model_rows, epochs=epochs, learning_rate=learning_rate)
    return [
        ScoredDatasetRow(
            **row.model_dump(), risk_score=round(model.predict_proba(featurize_row(row)) * 100, 3)
        )
        for row in test_rows
    ]


def evaluate_leave_one_incident_out(
    rows: list[FeatureDatasetRow],
    *,
    top_percentages: tuple[int, ...] = (10, 20, 50, 100),
    epochs: int = 1200,
    learning_rate: float = 0.45,
) -> LeaveOneIncidentOutEvaluation:
    """Evaluate a logistic baseline by holding out one incident group at a time.

    Each fold holds out one positive incident plus its generated controls. The model
    trains on all remaining incident/control groups, then scores only the held-out group.
    Aggregated metrics are calculated over out-of-sample predictions from all folds.
    """

    group_ids = _positive_group_ids(rows)
    if len(group_ids) < 3:
        raise ValueError("leave-one-incident-out evaluation needs at least 3 positive groups")

    all_scored_rows: list[ScoredDatasetRow] = []
    fold_metrics: dict[str, FoldMetric] = {}
    for held_out_group_id in group_ids:
        train_rows = [row for row in rows if incident_group_id(row) != held_out_group_id]
        test_rows = [row for row in rows if incident_group_id(row) == held_out_group_id]
        scored_test_rows = sorted(
            _score_rows(train_rows, test_rows, epochs=epochs, learning_rate=learning_rate),
            key=lambda row: row.risk_score,
            reverse=True,
        )
        all_scored_rows.extend(scored_test_rows)
        positive_rank = next(
            (index for index, row in enumerate(scored_test_rows, start=1) if row.target == 1), None
        )
        positive_score = next((row.risk_score for row in scored_test_rows if row.target == 1), None)
        fold_metrics[held_out_group_id] = FoldMetric(
            held_out_incident_id=held_out_group_id,
            train_sample_count=len(train_rows),
            test_sample_count=len(test_rows),
            positive_rank=positive_rank,
            positive_score=positive_score,
            recall_at_top_percent=_recall_at_top(scored_test_rows, top_percentages),
        )

    ranked_all = sorted(all_scored_rows, key=lambda row: row.risk_score, reverse=True)
    return LeaveOneIncidentOutEvaluation(
        sample_count=len(rows),
        positive_count=sum(row.target for row in rows),
        fold_count=len(fold_metrics),
        recall_at_top_percent=_recall_at_top(ranked_all, top_percentages),
        roc_auc=_roc_auc(ranked_all),
        pr_auc=_average_precision(ranked_all),
        fold_metrics=fold_metrics,
        scored_rows=ranked_all,
    )
