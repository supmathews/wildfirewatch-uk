from __future__ import annotations

import csv
from datetime import timedelta
from pathlib import Path

from wildfirewatch_uk.features.weather import (
    IncidentWeatherFeatures,
    build_incident_weather_features,
)
from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.providers.weather.open_meteo import OpenMeteoArchiveClient
from wildfirewatch_uk.schemas.incident import IncidentConfidence, IncidentRecord


def usable_incidents_for_weather(
    incidents: tuple[IncidentRecord, ...] | list[IncidentRecord] | None = None,
) -> list[IncidentRecord]:
    incidents = incidents if incidents is not None else load_seed_incidents()
    return [
        incident
        for incident in incidents
        if incident.confidence is not IncidentConfidence.NEEDS_VERIFICATION
        and incident.start_timestamp is not None
        and incident.latitude is not None
        and incident.longitude is not None
    ]


def build_features_for_seed_incidents(
    *, lookback_days: int = 60, client: OpenMeteoArchiveClient | None = None
) -> list[IncidentWeatherFeatures]:
    client = client or OpenMeteoArchiveClient()
    rows = []
    for incident in usable_incidents_for_weather():
        assert incident.start_timestamp is not None
        assert incident.latitude is not None
        assert incident.longitude is not None
        start_date = (incident.start_timestamp - timedelta(days=lookback_days)).date()
        end_date = incident.start_timestamp.date()
        observations = client.fetch_hourly_weather(
            latitude=incident.latitude,
            longitude=incident.longitude,
            start_date=start_date,
            end_date=end_date,
        )
        rows.append(build_incident_weather_features(incident, observations))
    return rows


def write_features_csv(rows: list[IncidentWeatherFeatures], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(IncidentWeatherFeatures.model_fields)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.model_dump(mode="json"))
