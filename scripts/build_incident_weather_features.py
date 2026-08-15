from __future__ import annotations

import argparse
from pathlib import Path

from wildfirewatch_uk.services.incident_weather_dataset import (
    build_features_for_seed_incidents,
    write_features_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build retrospective Open-Meteo weather/rainfall features for seed incidents."
    )
    parser.add_argument(
        "--output",
        default="data/processed/incident_weather_features.csv",
        help="Output CSV path.",
    )
    parser.add_argument("--lookback-days", type=int, default=60)
    args = parser.parse_args()

    rows = build_features_for_seed_incidents(lookback_days=args.lookback_days)
    write_features_csv(rows, Path(args.output))
    print(f"wrote {len(rows)} feature rows to {args.output}")


if __name__ == "__main__":
    main()
