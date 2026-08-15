from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.cluster_sensitivity import (
    CANNOCK_CLUSTER_EXCLUSIONS,
    ClusterSensitivityScenario,
    evaluate_cluster_sensitivity,
)
from wildfirewatch_uk.services.baseline_case_study import build_case_study_rows


def _format_recall(recall: dict[int, float]) -> str:
    return ", ".join(f"Top {key}%: {value:.3f}" for key, value in sorted(recall.items()))


def _format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def write_report(path: Path, scenarios: list[ClusterSensitivityScenario]) -> None:
    lines = [
        "# Rough spatial-control cluster sensitivity preview",
        "",
        "This report evaluates whether rough spatial-control performance is sensitive to",
        "the two geographically and temporally close Cannock Chase positives flagged by",
        "the incident independence audit. It reruns leave-one-incident-out evaluation",
        "after dropping either member of the potential local cluster.",
        "",
        "## Results",
        "",
        "| scenario | excluded_group_ids | samples | positives | folds | "
        "ROC-AUC | PR-AUC | Recall |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for scenario in scenarios:
        excluded = ", ".join(scenario.excluded_group_ids) or "none"
        lines.append(
            f"| {scenario.name} | {excluded} | {scenario.sample_count} | "
            f"{scenario.positive_count} | {scenario.fold_count} | "
            f"{_format_metric(scenario.roc_auc)} | {_format_metric(scenario.pr_auc)} | "
            f"{_format_recall(scenario.recall_at_top_percent)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This sensitivity check applies to the rough regional-offset spatial controls.",
            "It is intentionally separate from the temporal-control sensitivity report",
            "because spatial controls answer a harder generalisation question.",
            "",
            "If spatial metrics collapse when one local-cluster member is removed, the",
            "current spatial signal should be treated as especially fragile. If metrics",
            "remain similar, the rough spatial diagnostic is less dependent on the cluster,",
            "but still weak because the controls are coarse and the positive count is tiny.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run rough spatial cluster-sensitivity evaluation."
    )
    parser.add_argument("--controls-per-incident", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--learning-rate", type=float, default=0.45)
    parser.add_argument(
        "--output",
        default="reports/spatial_cluster_sensitivity_preview.md",
    )
    args = parser.parse_args()
    rows = build_case_study_rows(
        controls_per_incident=args.controls_per_incident,
        seed=args.seed,
        lookback_days=args.lookback_days,
    )
    scenarios = evaluate_cluster_sensitivity(
        rows,
        exclusions=CANNOCK_CLUSTER_EXCLUSIONS,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    output = Path(args.output)
    write_report(output, scenarios)
    print(f"wrote rough spatial cluster-sensitivity report to {output}")
    for scenario in scenarios:
        print(
            f"{scenario.name}: samples={scenario.sample_count} "
            f"positives={scenario.positive_count} roc_auc={scenario.roc_auc} "
            f"pr_auc={scenario.pr_auc} recall={scenario.recall_at_top_percent}"
        )


if __name__ == "__main__":
    main()
