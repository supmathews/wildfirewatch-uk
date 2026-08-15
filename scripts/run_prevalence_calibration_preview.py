from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.calibration import correct_case_control_probability
from wildfirewatch_uk.ml.out_of_sample import evaluate_leave_one_incident_out
from wildfirewatch_uk.services.baseline_case_study import build_temporal_case_study_rows


def _parse_offsets(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def _parse_prevalences(value: str) -> tuple[float, ...]:
    return tuple(float(part.strip()) for part in value.split(",") if part.strip())


def write_report(path: Path, *, prevalences: tuple[float, ...], rows) -> None:
    evaluation = evaluate_leave_one_incident_out(rows)
    sample_prevalence = evaluation.positive_count / evaluation.sample_count
    lines = [
        "# Prevalence-corrected probability preview",
        "",
        "This report demonstrates why case/control model scores should not be presented as",
        "real-world wildfire probabilities. The ranking is unchanged, but probabilities are",
        "corrected from the sampled positive prevalence to assumed rare-event prevalences.",
        "",
        "## Source evaluation",
        "",
        f"- samples: {evaluation.sample_count}",
        f"- positives: {evaluation.positive_count}",
        f"- sample prevalence: {sample_prevalence:.6f}",
        f"- ROC-AUC: {evaluation.roc_auc}",
        f"- PR-AUC: {evaluation.pr_auc}",
        "",
        "## Top out-of-sample rows with corrected probabilities",
        "",
    ]
    header = ["sample_id", "target", "raw_score_pct"] + [
        f"p@{prevalence:.4%}" for prevalence in prevalences
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for row in evaluation.scored_rows[:8]:
        raw_probability = row.risk_score / 100
        corrected = [
            correct_case_control_probability(
                predicted_probability=raw_probability,
                sample_prevalence=sample_prevalence,
                target_prevalence=prevalence,
            )
            for prevalence in prevalences
        ]
        values = [row.sample_id, str(row.target), f"{row.risk_score:.3f}"] + [
            f"{probability:.6f}" for probability in corrected
        ]
        lines.append("| " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The correction preserves rank order, so ROC-AUC/PR-AUC are unchanged.",
            "- It prevents oversampled case/control outputs from being mistaken for real-world",
            "  wildfire probabilities.",
            "- The target prevalences here are illustrative until a proper cell/day sampling",
            "  denominator exists.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview case-control prevalence correction.")
    parser.add_argument("--day-offsets", default="30,60,90")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--target-prevalences", default="0.01,0.001")
    parser.add_argument("--output", default="reports/prevalence_calibration_preview.md")
    args = parser.parse_args()

    rows = build_temporal_case_study_rows(
        day_offsets=_parse_offsets(args.day_offsets), lookback_days=args.lookback_days
    )
    output_path = Path(args.output)
    write_report(output_path, prevalences=_parse_prevalences(args.target_prevalences), rows=rows)
    print(f"wrote prevalence calibration preview to {output_path}")


if __name__ == "__main__":
    main()
