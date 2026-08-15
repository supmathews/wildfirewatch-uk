from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel

from wildfirewatch_uk.schemas.incident import IncidentRecord

TRACE_RAIN_THRESHOLD_MM = 0.2
MEANINGFUL_RAIN_THRESHOLD_MM = 1.0


class HourlyWeatherObservation(BaseModel):
    timestamp: datetime
    temperature_2m_c: float | None = None
    relative_humidity_2m_pct: float | None = None
    wind_speed_10m_mps: float | None = None
    wind_gust_10m_mps: float | None = None
    precipitation_mm: float | None = None


class RainfallWindows(BaseModel):
    rain_24h_mm: float
    rain_7d_mm: float
    rain_30d_mm: float
    rain_60d_mm: float


class IncidentWeatherFeatures(BaseModel):
    incident_id: str
    location_name: str
    target_timestamp: datetime
    latitude: float
    longitude: float
    temperature_2m_c: float | None
    relative_humidity_2m_pct: float | None
    wind_speed_10m_mps: float | None
    wind_gust_10m_mps: float | None
    rain_24h_mm: float
    rain_7d_mm: float
    rain_30d_mm: float
    rain_60d_mm: float
    days_since_rain: int | None
    days_since_meaningful_rain: int | None
    source: str


def _as_utc(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def _pre_target_observations(
    observations: Iterable[HourlyWeatherObservation], target_timestamp: datetime
) -> list[HourlyWeatherObservation]:
    target_utc = _as_utc(target_timestamp)
    return sorted(
        (obs for obs in observations if _as_utc(obs.timestamp) <= target_utc),
        key=lambda obs: _as_utc(obs.timestamp),
    )


def compute_rainfall_windows(
    observations: Iterable[HourlyWeatherObservation], target_timestamp: datetime
) -> RainfallWindows:
    target_utc = _as_utc(target_timestamp)
    pre_target = _pre_target_observations(observations, target_utc)

    def total_for_window(delta: timedelta) -> float:
        start = target_utc - delta
        total = sum(
            obs.precipitation_mm or 0.0
            for obs in pre_target
            if start < _as_utc(obs.timestamp) <= target_utc
        )
        return round(total, 3)

    return RainfallWindows(
        rain_24h_mm=total_for_window(timedelta(hours=24)),
        rain_7d_mm=total_for_window(timedelta(days=7)),
        rain_30d_mm=total_for_window(timedelta(days=30)),
        rain_60d_mm=total_for_window(timedelta(days=60)),
    )


def days_since_rain(
    observations: Iterable[HourlyWeatherObservation],
    target_timestamp: datetime,
    *,
    threshold_mm: float,
) -> int | None:
    target_utc = _as_utc(target_timestamp)
    rainy_observations = [
        obs
        for obs in _pre_target_observations(observations, target_utc)
        if (obs.precipitation_mm or 0.0) >= threshold_mm
    ]
    if not rainy_observations:
        return None
    latest = max(rainy_observations, key=lambda obs: _as_utc(obs.timestamp))
    return (_as_utc(target_utc).date() - _as_utc(latest.timestamp).date()).days


def latest_weather_before_target(
    observations: Iterable[HourlyWeatherObservation], target_timestamp: datetime
) -> HourlyWeatherObservation | None:
    pre_target = _pre_target_observations(observations, target_timestamp)
    if not pre_target:
        return None
    return pre_target[-1]


def build_incident_weather_features(
    incident: IncidentRecord,
    observations: Iterable[HourlyWeatherObservation],
    *,
    source: str = "open-meteo-archive",
) -> IncidentWeatherFeatures:
    if incident.start_timestamp is None:
        raise ValueError(f"incident {incident.incident_id} has no start_timestamp")
    if incident.latitude is None or incident.longitude is None:
        raise ValueError(f"incident {incident.incident_id} has no coordinates")

    target_timestamp = _as_utc(incident.start_timestamp)
    obs_list = list(observations)
    rainfall = compute_rainfall_windows(obs_list, target_timestamp)
    latest = latest_weather_before_target(obs_list, target_timestamp)

    return IncidentWeatherFeatures(
        incident_id=incident.incident_id,
        location_name=incident.location_name,
        target_timestamp=target_timestamp,
        latitude=incident.latitude,
        longitude=incident.longitude,
        temperature_2m_c=None if latest is None else latest.temperature_2m_c,
        relative_humidity_2m_pct=None if latest is None else latest.relative_humidity_2m_pct,
        wind_speed_10m_mps=None if latest is None else latest.wind_speed_10m_mps,
        wind_gust_10m_mps=None if latest is None else latest.wind_gust_10m_mps,
        rain_24h_mm=rainfall.rain_24h_mm,
        rain_7d_mm=rainfall.rain_7d_mm,
        rain_30d_mm=rainfall.rain_30d_mm,
        rain_60d_mm=rainfall.rain_60d_mm,
        days_since_rain=days_since_rain(
            obs_list, target_timestamp, threshold_mm=TRACE_RAIN_THRESHOLD_MM
        ),
        days_since_meaningful_rain=days_since_rain(
            obs_list, target_timestamp, threshold_mm=MEANINGFUL_RAIN_THRESHOLD_MM
        ),
        source=source,
    )
