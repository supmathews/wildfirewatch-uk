from __future__ import annotations

from datetime import datetime, timedelta

from pydantic import BaseModel

from wildfirewatch_uk.features.weather import IncidentWeatherFeatures


class TemporalControlLocation(BaseModel):
    control_id: str
    matched_incident_id: str
    target: int = 0
    target_timestamp: datetime
    latitude: float
    longitude: float
    day_offset: int
    sampling_method: str


def generate_temporal_controls(
    incidents: list[IncidentWeatherFeatures], *, day_offsets: tuple[int, ...] = (30, 60, 90)
) -> list[TemporalControlLocation]:
    """Generate same-location prior-date controls for each usable incident.

    These controls ask a different question from spatial controls: did the incident
    location look riskier near ignition than it did at earlier non-fire reference dates?
    They should be reported separately rather than mixed with spatial controls.
    """

    controls: list[TemporalControlLocation] = []
    for incident in incidents:
        for day_offset in day_offsets:
            controls.append(
                TemporalControlLocation(
                    control_id=f"control-{incident.incident_id}-temporal-{day_offset}d",
                    matched_incident_id=incident.incident_id,
                    target_timestamp=incident.target_timestamp - timedelta(days=day_offset),
                    latitude=incident.latitude,
                    longitude=incident.longitude,
                    day_offset=day_offset,
                    sampling_method="same_location_temporal_offset_v1",
                )
            )
    return controls
