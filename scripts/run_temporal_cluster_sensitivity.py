from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.cluster_sensitivity import (
    ClusterSensitivityScenario,
    evaluate_cluster_sensitivity,
)
from wildfirewatch_uk.services.baseline_case_study import build_temporal_case_study_rows

CANNOK_CLUSTER_EXCLUSIONS = {
    "all_model_ready": set(),
    "drop_cannock_chase_30_july": {"cannock-chase-2026-08"},
    "drop_cannock_chase_5_august": {"cannock-chase-sherbrook-valley-2026-08"},
}


def _parse_offsets(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def _format_recall(recall: dict[int, float]) -> str:
    return ", ".join(f"Top {key}%: {value:.3f}" for key, value in sorted(recall.items()))


def _format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def write_report(path: Path, scenarios: list[ClusterSensitivityScenario]) -> None:
    lines = [
        "# Temporal-control cluster sensitivity preview",
        "",
        "This report evaluates whether the temporal-control signal is sensitive to the",
        "two geographically and temporally close Cannock Chase positives flagged by the",
        "incident independence audit. It reruns leave-one-incident-out evaluation after",
        "dropping either member of the potential local cluster.",
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
            "If metrics collapse when one local-cluster member is removed, the current signal",
            "is likely too dependent on that cluster. If metrics remain directionally strong,",
            "that is useful evidence that the temporal weather/dryness signal is not solely",
            "carried by the paired Cannock Chase examples.",
            "",
            "This remains a tiny diagnostic test: removing one incident leaves only four",
            "positives, so the scenario metrics are intentionally treated as sensitivity",
            "checks, not stable performance estimates.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run temporal cluster-sensitivity evaluation.")
    parser.add_argument("--day-offsets", default="30,60,90")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--learning-rate", type=float, default=0.45)
    parser.add_argument(
        "--output",
        default="reports/temporal_cluster_sensitivity_preview.md",
    )
    args = parser.parse_args()
    rows = build_temporal_case_study_rows(
        day_offsets=_parse_offsets(args.day_offsets), lookback_days=args.lookback_days
    )
    scenarios = evaluate_cluster_sensitivity(
        rows,
        exclusions=CANNOK_CLUSTER_EXCLUSIONS,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    output = Path(args.output)
    write_report(output, scenarios)
    print(f"wrote temporal cluster-sensitivity report to {output}")
    for scenario in scenarios:
        print(
            f"{scenario.name}: samples={scenario.sample_count} "
            f"positives={scenario.positive_count} roc_auc={scenario.roc_auc} "
            f"pr_auc={scenario.pr_auc} recall={scenario.recall_at_top_percent}"
        )


if __name__ == "__main__":
    main()
