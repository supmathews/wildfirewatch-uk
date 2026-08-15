from __future__ import annotations

from datetime import timedelta

from wildfirewatch_uk.features.controls import ControlLocation, generate_matched_controls
from wildfirewatch_uk.features.weather import (
    IncidentWeatherFeatures,
    build_incident_weather_features,
)
from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.providers.weather.open_meteo import OpenMeteoArchiveClient
from wildfirewatch_uk.schemas.incident import IncidentRecord, IncidentSource, IncidentSourceType
from wildfirewatch_uk.services.incident_weather_dataset import build_features_for_seed_incidents


def dataset_row_from_features(
    features: IncidentWeatherFeatures, *, target: int
) -> FeatureDatasetRow:
    return FeatureDatasetRow(
        sample_id=features.incident_id,
        target=target,
        temperature_2m_c=features.temperature_2m_c,
        relative_humidity_2m_pct=features.relative_humidity_2m_pct,
        wind_speed_10m_mps=features.wind_speed_10m_mps,
        wind_gust_10m_mps=features.wind_gust_10m_mps,
        rain_24h_mm=features.rain_24h_mm,
        rain_7d_mm=features.rain_7d_mm,
        rain_30d_mm=features.rain_30d_mm,
        rain_60d_mm=features.rain_60d_mm,
        days_since_rain=features.days_since_rain,
        days_since_meaningful_rain=features.days_since_meaningful_rain,
    )


def pseudo_incident_from_control(control: ControlLocation) -> IncidentRecord:
    return IncidentRecord(
        incident_id=control.control_id,
        incident_name=control.control_id,
        start_timestamp=control.target_timestamp,
        latitude=control.latitude,
        longitude=control.longitude,
        location_name=control.control_id,
        incident_type="control",
        sources=[
            IncidentSource(
                url="https://github.com/supmathews/wildfirewatch-uk",
                source_type=IncidentSourceType.PLACEHOLDER,
                title="Generated non-fire control point",
            )
        ],
    )


def features_for_control(
    control: ControlLocation,
    *,
    client: OpenMeteoArchiveClient,
    lookback_days: int,
) -> IncidentWeatherFeatures:
    target_timestamp = control.target_timestamp
    start_date = (target_timestamp - timedelta(days=lookback_days)).date()
    observations = client.fetch_hourly_weather(
        latitude=control.latitude,
        longitude=control.longitude,
        start_date=start_date,
        end_date=target_timestamp.date(),
    )
    pseudo_incident = pseudo_incident_from_control(control)
    return build_incident_weather_features(pseudo_incident, observations)


def build_case_study_rows(
    *, controls_per_incident: int, seed: int, lookback_days: int
) -> list[FeatureDatasetRow]:
    client = OpenMeteoArchiveClient()
    incident_features = build_features_for_seed_incidents(
        lookback_days=lookback_days, client=client
    )
    controls = generate_matched_controls(
        incident_features, controls_per_incident=controls_per_incident, seed=seed
    )
    control_features = [
        features_for_control(control, client=client, lookback_days=lookback_days)
        for control in controls
    ]
    rows = [dataset_row_from_features(row, target=1) for row in incident_features]
    rows.extend(dataset_row_from_features(row, target=0) for row in control_features)
    return rows
