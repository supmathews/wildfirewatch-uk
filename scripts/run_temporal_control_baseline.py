from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.out_of_sample import (
    LeaveOneIncidentOutEvaluation,
    evaluate_leave_one_incident_out,
)
from wildfirewatch_uk.services.baseline_case_study import build_temporal_case_study_rows


def _parse_offsets(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def write_report(evaluation: LeaveOneIncidentOutEvaluation, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    recall_lines = "\n".join(
        f"- Recall@Top{percentage}%: {recall:.3f}"
        for percentage, recall in evaluation.recall_at_top_percent.items()
    )
    fold_lines = "\n".join(
        "| {incident_id} | {train} | {test} | {rank} | {score} | {recall20:.3f} |".format(
            incident_id=metric.held_out_incident_id,
            train=metric.train_sample_count,
            test=metric.test_sample_count,
            rank="n/a" if metric.positive_rank is None else metric.positive_rank,
            score="n/a" if metric.positive_score is None else f"{metric.positive_score:.3f}",
            recall20=metric.recall_at_top_percent.get(20, 0.0),
        )
        for metric in evaluation.fold_metrics.values()
    )
    roc_auc = "n/a" if evaluation.roc_auc is None else f"{evaluation.roc_auc:.3f}"
    pr_auc = "n/a" if evaluation.pr_auc is None else f"{evaluation.pr_auc:.3f}"
    output_path.write_text(
        f"""# Temporal-control leave-one-incident-out baseline preview

This report uses same-location temporal controls: each incident location is compared with
weather/dryness at prior non-fire reference dates. Each fold holds out one incident group
and trains on the remaining groups.

This answers a narrower question than spatial controls: did each location look more risky
near ignition than it did at earlier reference dates? It should not replace spatial matched
controls, but it is a cleaner early diagnostic of weather/dryness signal.

## Dataset

- Samples: {evaluation.sample_count}
- Positive incident samples: {evaluation.positive_count}
- Folds: {evaluation.fold_count}

## Aggregated out-of-sample metrics

- ROC-AUC: {roc_auc}
- PR-AUC / average precision: {pr_auc}
{recall_lines}

## Fold diagnostics

| held_out_incident_id | train | test | positive rank | positive score | Recall@Top20% |
|---|---:|---:|---:|---:|---:|
{fold_lines}

## Interpretation

This is still a small-sample diagnostic, but strong temporal-control performance would be
a useful sign that pre-ignition weather/dryness features are directionally meaningful. The
next proof step remains more positives and land-cover/region-matched spatial controls.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run temporal-control out-of-sample baseline.")
    parser.add_argument("--day-offsets", default="30,60,90")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--learning-rate", type=float, default=0.45)
    parser.add_argument("--output", default="reports/temporal_control_logistic_baseline_preview.md")
    args = parser.parse_args()

    rows = build_temporal_case_study_rows(
        day_offsets=_parse_offsets(args.day_offsets), lookback_days=args.lookback_days
    )
    evaluation = evaluate_leave_one_incident_out(
        rows,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    write_report(evaluation, Path(args.output))
    print(f"wrote temporal-control baseline report to {args.output}")
    print(f"samples={evaluation.sample_count} positives={evaluation.positive_count}")
    print(f"roc_auc={evaluation.roc_auc} pr_auc={evaluation.pr_auc}")
    print(evaluation.recall_at_top_percent)


if __name__ == "__main__":
    main()
