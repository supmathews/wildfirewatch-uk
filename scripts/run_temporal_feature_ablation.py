from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.feature_ablation import FeatureFamilyEvaluation, evaluate_feature_families
from wildfirewatch_uk.services.baseline_case_study import build_temporal_case_study_rows


def _parse_offsets(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def _metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def write_report(results: list[FeatureFamilyEvaluation], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Temporal-control feature ablation preview",
        "",
        "This report tests which feature families carry the same-location temporal-control",
        "signal. Each feature family is evaluated with leave-one-incident-out validation",
        "over the same temporal-control rows.",
        "",
        "## Results",
        "",
        "| feature_family | samples | positives | ROC-AUC | PR-AUC | "
        "Recall@Top20% | Recall@Top50% |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        recall = result.evaluation.recall_at_top_percent
        lines.append(
            f"| {result.family} | {result.sample_count} | {result.positive_count} | "
            f"{_metric(result.evaluation.roc_auc)} | {_metric(result.evaluation.pr_auc)} | "
            f"{recall.get(20, 0.0):.3f} | {recall.get(50, 0.0):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation guide",
            "",
            "- `latest_weather` tests temperature, humidity and wind near the target time.",
            "- `rainfall_windows` tests antecedent rainfall totals only.",
            "- `dry_spell_memory` tests days-since-rain style temporal memory only.",
            "- `rainfall_and_dry_spell` combines rainfall totals with dry-spell memory.",
            "- `all` uses the full current tabular weather/dryness feature set.",
            "",
            "These are tiny diagnostic ablations, not stable feature-importance claims.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run temporal-control feature ablations.")
    parser.add_argument("--day-offsets", default="30,60,90")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--learning-rate", type=float, default=0.45)
    parser.add_argument("--output", default="reports/temporal_feature_ablation_preview.md")
    args = parser.parse_args()

    rows = build_temporal_case_study_rows(
        day_offsets=_parse_offsets(args.day_offsets), lookback_days=args.lookback_days
    )
    results = evaluate_feature_families(
        rows, epochs=args.epochs, learning_rate=args.learning_rate
    )
    write_report(results, Path(args.output))
    print(f"wrote temporal feature-ablation report to {args.output}")
    for result in results:
        recall = result.evaluation.recall_at_top_percent
        print(
            f"{result.family}: samples={result.sample_count} positives={result.positive_count} "
            f"roc_auc={result.evaluation.roc_auc} pr_auc={result.evaluation.pr_auc} "
            f"recall20={recall.get(20, 0.0)} recall50={recall.get(50, 0.0)}"
        )


if __name__ == "__main__":
    main()
