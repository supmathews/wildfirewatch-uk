from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.ml.out_of_sample import (
    LeaveOneIncidentOutEvaluation,
    evaluate_leave_one_incident_out,
)
from wildfirewatch_uk.providers.land_cover.cached import CachedLandCoverClassifier
from wildfirewatch_uk.providers.land_cover.osm import OVERPASS_URL, OSMCoarseLandCoverClassifier
from wildfirewatch_uk.services.baseline_case_study import build_land_cover_case_study_rows


def format_recall(recall: dict[int, float]) -> str:
    return ", ".join(f"Top {key}%: {value:.3f}" for key, value in sorted(recall.items()))


def write_report(
    path: Path,
    evaluation: LeaveOneIncidentOutEvaluation,
    *,
    controls_per_incident: int,
    cache_only: bool,
) -> None:
    source = (
        "committed cache-only OSM coarse tag classification"
        if cache_only
        else "OSM / Overpass coarse tag classification"
    )
    lines = [
        "# Land-cover-matched spatial logistic baseline preview",
        "",
        "This diagnostic uses OSM-derived coarse land-cover classes to sample spatial controls",
        "with the same class as the matched incident point, then evaluates the trainable",
        "logistic baseline with leave-one-incident-out validation.",
        "",
        "## Configuration",
        "",
        f"- controls_per_incident: {controls_per_incident}",
        f"- land-cover source: {source}",
        "- evaluation: leave-one-incident-out",
        "",
        "## Metrics",
        "",
        f"- samples: {evaluation.sample_count}",
        f"- positives: {evaluation.positive_count}",
        f"- folds: {evaluation.fold_count}",
        f"- ROC-AUC: {evaluation.roc_auc}",
        f"- PR-AUC / average precision: {evaluation.pr_auc}",
        f"- Recall: {format_recall(evaluation.recall_at_top_percent)}",
        "",
        "## Fold diagnostics",
        "",
        "| held_out_incident_id | test_samples | positive_rank | positive_score | recall |",
        "|---|---:|---:|---:|---|",
    ]
    for fold in evaluation.fold_metrics.values():
        lines.append(
            f"| {fold.held_out_incident_id} | {fold.test_sample_count} | "
            f"{fold.positive_rank} | {fold.positive_score} | "
            f"{format_recall(fold.recall_at_top_percent)} |"
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- OSM land-cover labels are coarse and unevenly tagged.",
            f"- The sample remains tiny: {evaluation.positive_count} usable positives.",
            "- Public Overpass endpoints can rate-limit; prefer cache-only mode "
            "for deterministic reports.",
            "- This is still diagnostic evidence, not production wildfire prediction.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run land-cover-matched spatial baseline.")
    parser.add_argument("--controls-per-incident", type=int, default=1)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--max-attempts-per-control", type=int, default=80)
    parser.add_argument("--overpass-url", default=OVERPASS_URL)
    parser.add_argument("--radius-degrees", type=float, default=0.02)
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument(
        "--cache-path", type=Path, default=Path("data/processed/osm_land_cover_cache.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("reports/land_cover_matched_baseline_preview.md")
    )
    args = parser.parse_args()

    if args.cache_only:
        classifier = CachedLandCoverClassifier(cache_path=args.cache_path, missing_ok=True)
    else:
        classifier = OSMCoarseLandCoverClassifier(
            overpass_url=args.overpass_url,
            radius_degrees=args.radius_degrees,
            cache_path=args.cache_path,
            suppress_fetch_errors=True,
        )
    rows = build_land_cover_case_study_rows(
        controls_per_incident=args.controls_per_incident,
        seed=args.seed,
        lookback_days=args.lookback_days,
        land_cover_classifier=classifier,
        max_attempts_per_control=args.max_attempts_per_control,
    )
    evaluation = evaluate_leave_one_incident_out(rows)
    write_report(
        args.output,
        evaluation,
        controls_per_incident=args.controls_per_incident,
        cache_only=args.cache_only,
    )
    print(
        f"samples={evaluation.sample_count} positives={evaluation.positive_count} "
        f"roc_auc={evaluation.roc_auc} pr_auc={evaluation.pr_auc} "
        f"{evaluation.recall_at_top_percent}"
    )
    print(f"wrote report to {args.output}")


if __name__ == "__main__":
    main()
