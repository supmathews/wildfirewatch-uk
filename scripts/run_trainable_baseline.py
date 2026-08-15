from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.trainable_baseline import (
    TrainableBaselineEvaluation,
    evaluate_trainable_logistic_baseline,
)
from wildfirewatch_uk.services.baseline_case_study import build_case_study_rows


def write_report(evaluation: TrainableBaselineEvaluation, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    recall_lines = "\n".join(
        f"- Recall@Top{percentage}%: {recall:.3f}"
        for percentage, recall in evaluation.recall_at_top_percent.items()
    )
    coefficient_lines = "\n".join(
        f"| {name} | {weight:.6f} |"
        for name, weight in zip(
            evaluation.model.feature_names, evaluation.model.weights, strict=True
        )
    )
    top_rows = "\n".join(
        f"| {index} | {row.sample_id} | {row.target} | {row.risk_score:.3f} |"
        for index, row in enumerate(evaluation.scored_rows[:12], start=1)
    )
    roc_auc = "n/a" if evaluation.roc_auc is None else f"{evaluation.roc_auc:.3f}"
    pr_auc = "n/a" if evaluation.pr_auc is None else f"{evaluation.pr_auc:.3f}"
    output_path.write_text(
        f"""# Trainable logistic baseline preview

This is the first trainable baseline for the retrospective wildfire-risk PoC. It uses the
same currently usable incident/control rows as the heuristic baseline, but fits a small,
dependency-free logistic regression model over normalized weather and dry-spell features.

This is **not** proof of signal yet: there are only {evaluation.positive_count} positive
incident samples, controls are still rough min-distance regional offsets, and this report
uses in-sample ranking only. It is a wiring milestone before a larger Logistic Regression /
LightGBM evaluation with proper train/test splits.

## Dataset

- Samples: {evaluation.sample_count}
- Positive incident samples: {evaluation.positive_count}
- Control samples: {evaluation.sample_count - evaluation.positive_count}

## Metrics

- ROC-AUC: {roc_auc}
- PR-AUC / average precision: {pr_auc}
{recall_lines}

## Learned coefficients

| feature | coefficient |
|---|---:|
{coefficient_lines}

Model bias: `{evaluation.model.bias:.6f}`

## Top ranked samples

| rank | sample_id | target | trained_risk_score |
|---:|---|---:|---:|
{top_rows}

## Interpretation

This proves the repository can now train and score a logistic baseline from the generated
retrospective feature table. Treat the numbers as diagnostic only until the positive dataset
is much larger and controls are land-cover/region matched.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run trained logistic baseline preview.")
    parser.add_argument("--controls-per-incident", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--learning-rate", type=float, default=0.45)
    parser.add_argument("--output", default="reports/trainable_logistic_baseline_preview.md")
    args = parser.parse_args()

    rows = build_case_study_rows(
        controls_per_incident=args.controls_per_incident,
        seed=args.seed,
        lookback_days=args.lookback_days,
    )
    evaluation = evaluate_trainable_logistic_baseline(
        rows,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    write_report(evaluation, Path(args.output))
    print(f"wrote trainable baseline report to {args.output}")
    print(f"samples={evaluation.sample_count} positives={evaluation.positive_count}")
    print(f"roc_auc={evaluation.roc_auc} pr_auc={evaluation.pr_auc}")
    print(evaluation.recall_at_top_percent)


if __name__ == "__main__":
    main()
