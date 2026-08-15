from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.out_of_sample import (
    LeaveOneIncidentOutEvaluation,
    evaluate_leave_one_incident_out,
)
from wildfirewatch_uk.services.baseline_case_study import build_case_study_rows


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
    top_rows = "\n".join(
        f"| {index} | {row.sample_id} | {row.target} | {row.risk_score:.3f} |"
        for index, row in enumerate(evaluation.scored_rows[:12], start=1)
    )
    roc_auc = "n/a" if evaluation.roc_auc is None else f"{evaluation.roc_auc:.3f}"
    pr_auc = "n/a" if evaluation.pr_auc is None else f"{evaluation.pr_auc:.3f}"
    output_path.write_text(
        f"""# Leave-one-incident-out logistic baseline preview

This report is the first out-of-sample check for the retrospective wildfire-risk PoC.
Each fold holds out one positive incident and its generated controls, trains on the
remaining incident/control groups, and scores only the held-out group.

This is still **not** proof of concept: there are only {evaluation.positive_count} positive
incidents and controls are rough min-distance regional offsets. It is, however, a stricter
diagnostic than the earlier in-sample trainable baseline.

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

## Top out-of-sample scored rows

| rank | sample_id | target | held_out_risk_score |
|---:|---|---:|---:|
{top_rows}

## Interpretation

These metrics should be treated as a smoke test for model generalisation plumbing, not as
evidence of a deployable signal. The next meaningful data-science step is still to improve
control quality with land-cover/region matching and add more source-backed positive
incidents before making any go/no-go call.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run leave-one-incident-out baseline preview.")
    parser.add_argument("--controls-per-incident", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--learning-rate", type=float, default=0.45)
    parser.add_argument("--output", default="reports/out_of_sample_logistic_baseline_preview.md")
    args = parser.parse_args()

    rows = build_case_study_rows(
        controls_per_incident=args.controls_per_incident,
        seed=args.seed,
        lookback_days=args.lookback_days,
    )
    evaluation = evaluate_leave_one_incident_out(
        rows,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    write_report(evaluation, Path(args.output))
    print(f"wrote out-of-sample baseline report to {args.output}")
    print(f"samples={evaluation.sample_count} positives={evaluation.positive_count}")
    print(f"roc_auc={evaluation.roc_auc} pr_auc={evaluation.pr_auc}")
    print(evaluation.recall_at_top_percent)


if __name__ == "__main__":
    main()
