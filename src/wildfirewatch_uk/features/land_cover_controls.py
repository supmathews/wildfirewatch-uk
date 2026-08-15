from __future__ import annotations

import random
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from wildfirewatch_uk.features.controls import (
    UK_LAT_MAX,
    UK_LAT_MIN,
    UK_LON_MAX,
    UK_LON_MIN,
    _clamp,
    _far_enough_from_incidents,
)
from wildfirewatch_uk.features.weather import IncidentWeatherFeatures


class LandCoverClassifier(Protocol):
    def classify(self, *, latitude: float, longitude: float) -> str | None: ...


class StaticLandCoverClassifier(BaseModel):
    """Deterministic test/development classifier for land-cover matching.

    Real land-cover providers can implement the same `classify()` interface using
    OSM, UKCEH, or another authoritative dataset. This class exists so the
    sampler can be tested without network calls.
    """

    default_class: str | None = None
    point_classes: dict[tuple[float, float], str] = {}

    def classify(self, *, latitude: float, longitude: float) -> str | None:
        return self.point_classes.get((round(latitude, 7), round(longitude, 7)), self.default_class)


class LandCoverMatchedControlLocation(BaseModel):
    control_id: str
    matched_incident_id: str
    target: int = 0
    target_timestamp: datetime
    latitude: float
    longitude: float
    land_cover_class: str
    sampling_method: str


def generate_land_cover_matched_controls(
    incidents: list[IncidentWeatherFeatures],
    *,
    controls_per_incident: int,
    seed: int,
    land_cover_classifier: LandCoverClassifier,
    min_offset_degrees: float = 0.15,
    max_offset_degrees: float = 0.9,
    min_distance_from_any_incident_km: float = 20.0,
    max_attempts_per_control: int = 250,
) -> list[LandCoverMatchedControlLocation]:
    """Generate controls that match each incident's coarse land-cover class.

    This is provider-agnostic scaffolding: the caller supplies the land-cover
    classifier, and the sampler only accepts candidate control points with the
    same non-null class as the matched incident.
    """

    rng = random.Random(seed)
    controls: list[LandCoverMatchedControlLocation] = []
    for incident in incidents:
        incident_class = land_cover_classifier.classify(
            latitude=incident.latitude, longitude=incident.longitude
        )
        if incident_class is None:
            raise RuntimeError(f"No land-cover class for incident {incident.incident_id}")
        for index in range(controls_per_incident):
            for _attempt in range(max_attempts_per_control):
                lat_offset = rng.uniform(min_offset_degrees, max_offset_degrees)
                lon_offset = rng.uniform(min_offset_degrees, max_offset_degrees)
                if rng.random() < 0.5:
                    lat_offset *= -1
                if rng.random() < 0.5:
                    lon_offset *= -1
                latitude = round(_clamp(incident.latitude + lat_offset, UK_LAT_MIN, UK_LAT_MAX), 7)
                longitude = round(
                    _clamp(incident.longitude + lon_offset, UK_LON_MIN, UK_LON_MAX), 7
                )
                candidate_class = land_cover_classifier.classify(
                    latitude=latitude, longitude=longitude
                )
                if candidate_class != incident_class:
                    continue
                if not _far_enough_from_incidents(
                    latitude=latitude,
                    longitude=longitude,
                    incidents=incidents,
                    min_distance_km=min_distance_from_any_incident_km,
                ):
                    continue
                break
            else:
                raise RuntimeError(
                    f"Could not sample a land-cover matched control for {incident.incident_id}"
                )
            controls.append(
                LandCoverMatchedControlLocation(
                    control_id=f"control-{incident.incident_id}-landcover-{index + 1:03d}",
                    matched_incident_id=incident.incident_id,
                    target_timestamp=incident.target_timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    land_cover_class=incident_class,
                    sampling_method="regional_land_cover_matched_v1",
                )
            )
    return controls
