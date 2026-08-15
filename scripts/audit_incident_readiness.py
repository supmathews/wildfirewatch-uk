from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from wildfirewatch_uk.services.incident_readiness import (
    IncidentReadinessStatus,
    audit_incident_readiness,
)


def write_report(path: Path) -> None:
    results = audit_incident_readiness()
    status_counts = Counter(result.status for result in results)
    blocker_counts = Counter(blocker for result in results for blocker in result.blockers)
    lines = [
        "# Incident modelling-readiness audit",
        "",
        "This report lists which source-backed seed incidents are currently usable by the",
        "weather-feature/model pipeline and which are blocked. It is intentionally strict:",
        "missing timestamps or coordinates exclude incidents to preserve leakage discipline.",
        "",
        "## Summary",
        "",
        f"- total incidents: {len(results)}",
        f"- model-ready incidents: {status_counts[IncidentReadinessStatus.MODEL_READY]}",
        f"- blocked incidents: {status_counts[IncidentReadinessStatus.BLOCKED]}",
        "",
        "## Blocker counts",
        "",
    ]
    if blocker_counts:
        for blocker, count in sorted(blocker_counts.items()):
            lines.append(f"- {blocker}: {count}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Incident details",
            "",
            "| incident_id | location | status | blockers |",
            "|---|---|---|---|",
        ]
    )
    for result in results:
        blockers = ", ".join(result.blockers) if result.blockers else "none"
        lines.append(
            f"| {result.incident_id} | {result.location_name} | {result.status} | {blockers} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A blocked incident can still be source-backed and valuable, but it should not feed",
            "the weather-feature model until the blockers are resolved. The highest-value next",
            "research task is finding durable exact timestamps for source-backed incidents that",
            "already have coordinates.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit seed incident modelling readiness.")
    parser.add_argument("--output", default="reports/incident_modelling_readiness_audit.md")
    args = parser.parse_args()
    output_path = Path(args.output)
    write_report(output_path)
    print(f"wrote incident readiness audit to {output_path}")


if __name__ == "__main__":
    main()
