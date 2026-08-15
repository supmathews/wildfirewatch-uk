from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.services.incident_independence import audit_incident_independence


def write_report(path: Path, *, distance_threshold_km: float, day_threshold: int) -> None:
    audit = audit_incident_independence(
        distance_threshold_km=distance_threshold_km,
        day_threshold=day_threshold,
    )
    lines = [
        "# Incident independence / cluster audit",
        "",
        "This report flags model-ready positive incidents that are geographically and",
        "temporally close enough to be treated as a potential local cluster rather than",
        "fully independent evidence. It does not merge or remove records; it documents",
        "an evaluation caveat for tiny-sample metrics.",
        "",
        "## Configuration",
        "",
        f"- distance threshold: {distance_threshold_km:.1f} km",
        f"- day threshold: {day_threshold} days",
        "",
        "## Summary",
        "",
        f"- model-ready incidents: {audit.model_ready_incident_count}",
        f"- potential cluster pairs: {audit.cluster_pair_count}",
        "",
        "## Potential cluster pairs",
        "",
        "| incident_id_a | incident_id_b | distance_km | days_apart | reason |",
        "|---|---|---:|---:|---|",
    ]
    if audit.cluster_pairs:
        for pair in audit.cluster_pairs:
            lines.append(
                f"| {pair.incident_id_a} | {pair.incident_id_b} | "
                f"{pair.distance_km:.2f} | {pair.days_apart} | {pair.reason} |"
            )
    else:
        lines.append("| none | none |  |  |  |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Potential cluster pairs should be treated cautiously in model interpretation:",
            "they may represent distinct incidents, but they are not as independent as",
            "events separated across wider geography and time. With only five usable",
            "positives, even one local cluster can make point estimates look more stable",
            "than they really are.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit incident independence.")
    parser.add_argument("--distance-threshold-km", type=float, default=10.0)
    parser.add_argument("--day-threshold", type=int, default=14)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/incident_independence_cluster_audit.md"),
    )
    args = parser.parse_args()
    write_report(
        args.output,
        distance_threshold_km=args.distance_threshold_km,
        day_threshold=args.day_threshold,
    )
    print(f"wrote incident independence audit to {args.output}")


if __name__ == "__main__":
    main()
