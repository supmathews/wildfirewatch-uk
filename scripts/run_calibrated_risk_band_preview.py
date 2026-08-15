from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.calibration import correct_case_control_probability
from wildfirewatch_uk.ml.out_of_sample import evaluate_leave_one_incident_out
from wildfirewatch_uk.ml.risk_bands import assign_risk_band, summarize_risk_bands
from wildfirewatch_uk.services.baseline_case_study import build_temporal_case_study_rows


def _parse_offsets(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def write_report(path: Path, *, target_prevalence: float, rows) -> None:
    evaluation = evaluate_leave_one_incident_out(rows)
    sample_prevalence = evaluation.positive_count / evaluation.sample_count
    calibrated = [
        (
            row,
            correct_case_control_probability(
                predicted_probability=row.risk_score / 100,
                sample_prevalence=sample_prevalence,
                target_prevalence=target_prevalence,
            ),
        )
        for row in evaluation.scored_rows
    ]
    summary = summarize_risk_bands(
        [(probability, row.target) for row, probability in calibrated]
    )
    lines = [
        "# Calibrated diagnostic risk-band preview",
        "",
        "This report bins calibrated case/control scores into monotonic diagnostic tiers.",
        "The bands are for retrospective evaluation only; they are not public warning",
        "levels or operational emergency guidance.",
        "",
        "## Configuration",
        "",
        f"- source samples: {evaluation.sample_count}",
        f"- positives: {evaluation.positive_count}",
        f"- sample prevalence: {sample_prevalence:.6f}",
        f"- target prevalence assumption: {target_prevalence:.6f}",
        "",
        "## Band summary",
        "",
        "| band | probability range | samples | positives | observed positive rate | description |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for band_summary in summary.values():
        band = band_summary.band
        positive_rate = band_summary.positive_rate
        positive_rate_text = "n/a" if positive_rate is None else f"{positive_rate:.3f}"
        lines.append(
            f"| {band.name} | [{band.lower_bound:.4f}, {band.upper_bound:.4f}) | "
            f"{band_summary.sample_count} | {band_summary.positive_count} | "
            f"{positive_rate_text} | {band.description} |"
        )
    lines.extend(
        [
            "",
            "## Top calibrated rows",
            "",
            "| sample_id | target | raw_score_pct | calibrated_probability | band |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row, probability in calibrated[:8]:
        lines.append(
            f"| {row.sample_id} | {row.target} | {row.risk_score:.3f} | "
            f"{probability:.6f} | {assign_risk_band(probability).name} |"
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- The target prevalence is illustrative until a proper UK cell/day denominator "
            "exists.",
            "- Bands are monotonic bins over calibrated diagnostic scores, not proof of calibrated",
            "  operational probabilities.",
            "- With only four positives, observed rates inside bands are unstable.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview calibrated diagnostic risk bands.")
    parser.add_argument("--day-offsets", default="30,60,90")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--target-prevalence", type=float, default=0.01)
    parser.add_argument("--output", default="reports/calibrated_risk_band_preview.md")
    args = parser.parse_args()

    rows = build_temporal_case_study_rows(
        day_offsets=_parse_offsets(args.day_offsets), lookback_days=args.lookback_days
    )
    output_path = Path(args.output)
    write_report(output_path, target_prevalence=args.target_prevalence, rows=rows)
    print(f"wrote calibrated risk-band preview to {output_path}")


if __name__ == "__main__":
    main()
