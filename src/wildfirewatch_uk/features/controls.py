from __future__ import annotations

import random
from datetime import datetime

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


def generate_matched_controls(
    incidents: list[IncidentWeatherFeatures],
    *,
    controls_per_incident: int,
    seed: int,
    min_offset_degrees: float = 0.15,
    max_offset_degrees: float = 0.9,
) -> list[ControlLocation]:
    """Generate deterministic rough regional control points.

    This is intentionally simple for the first PoC: controls share the incident
    timestamp and are offset within the same broad region. Later versions should
    match land cover, admin region, and known fire exclusion zones.
    """

    rng = random.Random(seed)
    controls: list[ControlLocation] = []
    for incident in incidents:
        for index in range(controls_per_incident):
            lat_offset = rng.uniform(min_offset_degrees, max_offset_degrees)
            lon_offset = rng.uniform(min_offset_degrees, max_offset_degrees)
            if rng.random() < 0.5:
                lat_offset *= -1
            if rng.random() < 0.5:
                lon_offset *= -1
            controls.append(
                ControlLocation(
                    control_id=f"control-{incident.incident_id}-{index + 1:03d}",
                    matched_incident_id=incident.incident_id,
                    target_timestamp=incident.target_timestamp,
                    latitude=round(
                        _clamp(incident.latitude + lat_offset, UK_LAT_MIN, UK_LAT_MAX), 7
                    ),
                    longitude=round(
                        _clamp(incident.longitude + lon_offset, UK_LON_MIN, UK_LON_MAX), 7
                    ),
                    sampling_method="regional_random_offset_v1",
                )
            )
    return controls
