from __future__ import annotations

import random
from datetime import datetime
from math import asin, cos, radians, sin, sqrt

from pydantic import BaseModel

from wildfirewatch_uk.features.weather import IncidentWeatherFeatures

UK_LAT_MIN = 49.8
UK_LAT_MAX = 58.8
UK_LON_MIN = -8.7
UK_LON_MAX = 1.8


class ControlLocation(BaseModel):
    control_id: str
    matched_incident_id: str
    target: int = 0
    target_timestamp: datetime
    latitude: float
    longitude: float
    sampling_method: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def distance_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    """Great-circle distance between two WGS84 points."""

    radius_km = 6371.0088
    lat_a_rad = radians(lat_a)
    lat_b_rad = radians(lat_b)
    delta_lat = radians(lat_b - lat_a)
    delta_lon = radians(lon_b - lon_a)
    haversine = sin(delta_lat / 2) ** 2 + cos(lat_a_rad) * cos(lat_b_rad) * sin(
        delta_lon / 2
    ) ** 2
    return radius_km * 2 * asin(sqrt(haversine))


def _far_enough_from_incidents(
    *,
    latitude: float,
    longitude: float,
    incidents: list[IncidentWeatherFeatures],
    min_distance_km: float,
) -> bool:
    return all(
        distance_km(latitude, longitude, incident.latitude, incident.longitude) >= min_distance_km
        for incident in incidents
    )


def generate_matched_controls(
    incidents: list[IncidentWeatherFeatures],
    *,
    controls_per_incident: int,
    seed: int,
    min_offset_degrees: float = 0.15,
    max_offset_degrees: float = 0.9,
    min_distance_from_any_incident_km: float = 20.0,
) -> list[ControlLocation]:
    """Generate deterministic rough regional control points.

    This is intentionally simple for the first PoC: controls share the incident
    timestamp and are offset within the same broad region, but must stay a
    minimum distance from all known incident points so controls do not quietly
    duplicate positives. Later versions should match land cover, admin region,
    and known fire exclusion zones.
    """

    rng = random.Random(seed)
    controls: list[ControlLocation] = []
    for incident in incidents:
        for index in range(controls_per_incident):
            for _attempt in range(250):
                lat_offset = rng.uniform(min_offset_degrees, max_offset_degrees)
                lon_offset = rng.uniform(min_offset_degrees, max_offset_degrees)
                if rng.random() < 0.5:
                    lat_offset *= -1
                if rng.random() < 0.5:
                    lon_offset *= -1
                latitude = round(
                    _clamp(incident.latitude + lat_offset, UK_LAT_MIN, UK_LAT_MAX), 7
                )
                longitude = round(
                    _clamp(incident.longitude + lon_offset, UK_LON_MIN, UK_LON_MAX), 7
                )
                if _far_enough_from_incidents(
                    latitude=latitude,
                    longitude=longitude,
                    incidents=incidents,
                    min_distance_km=min_distance_from_any_incident_km,
                ):
                    break
            else:
                raise RuntimeError(
                    "Could not sample a control far enough from known incident points"
                )
            controls.append(
                ControlLocation(
                    control_id=f"control-{incident.incident_id}-{index + 1:03d}",
                    matched_incident_id=incident.incident_id,
                    target_timestamp=incident.target_timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    sampling_method="regional_offset_min_distance_v2",
                )
            )
    return controls
