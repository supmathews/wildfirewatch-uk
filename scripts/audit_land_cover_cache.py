from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.services.land_cover_cache_audit import (
    DEFAULT_CACHE_PATH,
    LandCoverCacheAudit,
    audit_land_cover_cache,
)


def write_report(path: Path, audit: LandCoverCacheAudit, *, cache_path: Path) -> None:
    lines = [
        "# OSM land-cover cache coverage audit",
        "",
        "This report checks whether current model-ready incident points have deterministic",
        "coarse land-cover labels in the committed OSM cache. It does not call Overpass.",
        "",
        "## Configuration",
        "",
        f"- cache_path: `{cache_path}`",
        "- point set: current model-ready seed incidents",
        "",
        "## Summary",
        "",
        f"- model-ready points: {audit.point_count}",
        f"- classified points: {audit.classified_count}",
        f"- cached null points: {audit.null_count}",
        f"- missing cache entries: {audit.missing_count}",
        f"- classified coverage: {audit.coverage_ratio:.3f}",
        "",
        "## Details",
        "",
        "| incident_id | cache_key | status | land_cover_class |",
        "|---|---|---|---|",
    ]
    for row in audit.rows:
        land_cover_class = row.land_cover_class or ""
        lines.append(
            f"| {row.incident_id} | {row.cache_key} | {row.status} | {land_cover_class} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Full cache coverage means routine land-cover diagnostics for current model-ready",
            "incidents can run without live Overpass calls. This does not make OSM-derived",
            "classes authoritative, and it does not solve land-cover coverage for future",
            "new incidents or generated controls.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit OSM land-cover cache coverage.")
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/osm_land_cover_cache_coverage.md"),
    )
    args = parser.parse_args()
    audit = audit_land_cover_cache(cache_path=args.cache_path)
    write_report(args.output, audit, cache_path=args.cache_path)
    print(f"wrote OSM land-cover cache coverage report to {args.output}")
    print(
        f"points={audit.point_count} classified={audit.classified_count} "
        f"null={audit.null_count} missing={audit.missing_count} "
        f"coverage={audit.coverage_ratio:.3f}"
    )


if __name__ == "__main__":
    main()
