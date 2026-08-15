from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from wildfirewatch_uk.providers.land_cover.cached import CachedLandCoverClassifier
from wildfirewatch_uk.providers.land_cover.osm import OVERPASS_URL, OSMCoarseLandCoverClassifier
from wildfirewatch_uk.services.incident_weather_dataset import build_features_for_seed_incidents


@dataclass(frozen=True)
class IncidentPoint:
    incident_id: str
    latitude: float
    longitude: float


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify usable incident points with OSM land cover."
    )
    parser.add_argument("--overpass-url", default=OVERPASS_URL)
    parser.add_argument("--radius-degrees", type=float, default=0.006)
    parser.add_argument(
        "--cache-path", type=Path, default=Path("data/processed/osm_land_cover_cache.json")
    )
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--csv", type=Path, default=None)
    args = parser.parse_args()

    if args.cache_only:
        classifier = CachedLandCoverClassifier(cache_path=args.cache_path)
    else:
        classifier = OSMCoarseLandCoverClassifier(
            overpass_url=args.overpass_url,
            radius_degrees=args.radius_degrees,
            cache_path=args.cache_path,
        )
    if args.csv is not None and args.csv.exists():
        rows = list(csv.DictReader(args.csv.open()))
        incidents = [
            IncidentPoint(
                incident_id=row["incident_id"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
            )
            for row in rows
        ]
    else:
        incidents = build_features_for_seed_incidents(lookback_days=60)
    print("incident_id,latitude,longitude,osm_coarse_land_cover")
    for incident in incidents:
        try:
            land_cover = classifier.classify(
                latitude=incident.latitude, longitude=incident.longitude
            )
        except Exception as error:  # pragma: no cover - live diagnostic script
            land_cover = f"error:{type(error).__name__}"
        print(f"{incident.incident_id},{incident.latitude},{incident.longitude},{land_cover}")


if __name__ == "__main__":
    main()
