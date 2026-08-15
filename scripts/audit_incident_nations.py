from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.services.incident_readiness import (
    IncidentReadinessStatus,
    audit_incident_readiness,
)


def write_report(path: Path) -> None:
    incidents = load_seed_incidents()
    readiness = {result.incident_id: result for result in audit_incident_readiness()}
    all_counts = Counter(
        incident.uk_nation.value if incident.uk_nation else "unknown" for incident in incidents
    )
    ready_counts = Counter(
        incident.uk_nation.value if incident.uk_nation else "unknown"
        for incident in incidents
        if readiness[incident.incident_id].status is IncidentReadinessStatus.MODEL_READY
    )

    lines = [
        "# Incident UK-nation data contract preview",
        "",
        "This report summarizes the first geographic-transfer data-contract field:",
        "`uk_nation`. It supports future England/Wales/Scotland transfer and",
        "calibration experiments without implying those experiments are ready yet.",
        "",
        "## Counts by UK nation",
        "",
        "| uk_nation | seed_incidents | model_ready_incidents |",
        "|---|---:|---:|",
    ]
    for nation in sorted(all_counts):
        lines.append(f"| {nation} | {all_counts[nation]} | {ready_counts[nation]} |")
    lines.extend(
        [
            "",
            "## Incident details",
            "",
            "| incident_id | location | uk_nation | modelling_status |",
            "|---|---|---|---|",
        ]
    )
    for incident in incidents:
        nation = incident.uk_nation.value if incident.uk_nation else "unknown"
        status = readiness[incident.incident_id].status.value
        lines.append(f"| {incident.incident_id} | {incident.location_name} | {nation} | {status} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Current source-backed/model-ready positives cover England and Wales only.",
            "Scotland transfer testing remains blocked until Scotland-specific source-backed",
            "positive incidents are collected with the same strict timestamp/coordinate",
            "readiness rules.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize incident UK-nation labels.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/incident_uk_nation_contract_preview.md"),
    )
    args = parser.parse_args()
    write_report(args.output)
    print(f"wrote incident UK-nation contract preview to {args.output}")


if __name__ == "__main__":
    main()
