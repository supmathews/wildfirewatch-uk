from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.out_of_sample import evaluate_leave_one_incident_out
from wildfirewatch_uk.ml.uncertainty import BootstrapMetricInterval, bootstrap_metric_intervals
from wildfirewatch_uk.services.baseline_case_study import build_temporal_case_study_rows


def _parse_offsets(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def _metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _interval(value: BootstrapMetricInterval) -> str:
    if value.lower is None or value.upper is None:
        return "n/a"
    return f"[{value.lower:.6f}, {value.upper:.6f}]"


def write_report(
    path: Path,
    *,
    intervals: list[BootstrapMetricInterval],
    sample_count: int,
    positive_count: int,
    confidence_level: float,
) -> None:
    lines = [
        "# Temporal metric uncertainty preview",
        "",
        "This report adds deterministic bootstrap intervals around current out-of-sample",
        "temporal-control metrics. It is intended to make the tiny-sample uncertainty",
        "visible rather than hiding it behind point estimates.",
        "",
        "## Configuration",
        "",
        f"- samples: {sample_count}",
        f"- positives: {positive_count}",
        f"- confidence level: {confidence_level:.0%}",
        "",
        "## Bootstrap intervals",
        "",
        "| metric | point estimate | interval | valid resamples | skipped resamples |",
        "|---|---:|---:|---:|---:|",
    ]
    for interval in intervals:
        lines.append(
            f"| {interval.metric} | {_metric(interval.point_estimate)} | {_interval(interval)} | "
            f"{interval.valid_resamples} | {interval.skipped_resamples} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Wide intervals are expected with only four positives.",
            "- Skipped resamples occur when a bootstrap draw lacks both positive and negative",
            "  samples, making ROC-AUC or PR-AUC undefined.",
            "- These intervals are diagnostic uncertainty summaries, not formal proof of",
            "  deployment readiness.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview bootstrap metric uncertainty.")
    parser.add_argument("--day-offsets", default="30,60,90")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--confidence-level", type=float, default=0.90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="reports/temporal_metric_uncertainty_preview.md")
    args = parser.parse_args()

    rows = build_temporal_case_study_rows(
        day_offsets=_parse_offsets(args.day_offsets), lookback_days=args.lookback_days
    )
    evaluation = evaluate_leave_one_incident_out(rows)
    intervals = bootstrap_metric_intervals(
        evaluation.scored_rows,
        iterations=args.iterations,
        confidence_level=args.confidence_level,
        seed=args.seed,
    )
    output_path = Path(args.output)
    write_report(
        output_path,
        intervals=intervals,
        sample_count=evaluation.sample_count,
        positive_count=evaluation.positive_count,
        confidence_level=args.confidence_level,
    )
    print(f"wrote temporal metric uncertainty preview to {output_path}")
    for interval in intervals:
        print(
            f"{interval.metric}: point={interval.point_estimate} interval={_interval(interval)} "
            f"valid={interval.valid_resamples} skipped={interval.skipped_resamples}"
        )


if __name__ == "__main__":
    main()
