from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.baseline import (
    evaluate_baseline_ranking,
)
from wildfirewatch_uk.ml.trainable_baseline import evaluate_trainable_logistic_baseline
from wildfirewatch_uk.services.baseline_case_study import build_case_study_rows


def run_baseline_case_study(
    *,
    controls_per_incident: int,
    seed: int,
    lookback_days: int,
    model: str = "heuristic",
    epochs: int = 1200,
    learning_rate: float = 0.45,
):
    rows = build_case_study_rows(
        controls_per_incident=controls_per_incident, seed=seed, lookback_days=lookback_days
    )
    if model == "logistic":
        return evaluate_trainable_logistic_baseline(
            rows,
            top_percentages=(10, 20, 50, 100),
            epochs=epochs,
            learning_rate=learning_rate,
        )
    if model != "heuristic":
        raise ValueError(f"Unsupported baseline model: {model}")
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
