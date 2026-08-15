from datetime import UTC, datetime

import pytest

from wildfirewatch_uk.features.land_cover_controls import (
    StaticLandCoverClassifier,
    generate_land_cover_matched_controls,
)
from wildfirewatch_uk.features.weather import IncidentWeatherFeatures


def feature_row(incident_id: str, lat: float, lon: float) -> IncidentWeatherFeatures:
    return IncidentWeatherFeatures(
        incident_id=incident_id,
        location_name=incident_id,
        target_timestamp=datetime(2026, 8, 13, 15, 0, tzinfo=UTC),
        latitude=lat,
        longitude=lon,
        temperature_2m_c=30.0,
        relative_humidity_2m_pct=25.0,
        wind_speed_10m_mps=4.0,
        wind_gust_10m_mps=8.0,
        rain_24h_mm=0.0,
        rain_7d_mm=1.0,
        rain_30d_mm=10.0,
        rain_60d_mm=30.0,
        days_since_rain=4,
        days_since_meaningful_rain=8,
        source="test",
    )


def test_land_cover_matched_controls_keep_same_classifier_class():
    incident = feature_row("heath-fire", 52.0, -2.0)
    classifier = StaticLandCoverClassifier(default_class="heath_or_grass")

    controls = generate_land_cover_matched_controls(
        [incident],
        controls_per_incident=4,
        seed=3,
        land_cover_classifier=classifier,
        min_distance_from_any_incident_km=20,
    )

    assert len(controls) == 4
    assert all(control.land_cover_class == "heath_or_grass" for control in controls)
    assert all(control.sampling_method == "regional_land_cover_matched_v1" for control in controls)
    assert all(control.matched_incident_id == incident.incident_id for control in controls)


def test_land_cover_matched_controls_reject_non_matching_candidates():
    incident = feature_row("heath-fire", 52.0, -2.0)
    classifier = StaticLandCoverClassifier(
        default_class="urban",
        point_classes={(52.0, -2.0): "heath_or_grass"},
    )

    with pytest.raises(RuntimeError, match="land-cover matched control"):
        generate_land_cover_matched_controls(
            [incident],
            controls_per_incident=1,
            seed=3,
            land_cover_classifier=classifier,
            max_attempts_per_control=5,
        )
