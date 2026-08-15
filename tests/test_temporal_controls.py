from datetime import UTC, datetime

from wildfirewatch_uk.features.temporal_controls import (
    TemporalControlLocation,
    generate_temporal_controls,
)
from wildfirewatch_uk.features.weather import IncidentWeatherFeatures


def feature_row(incident_id: str) -> IncidentWeatherFeatures:
    return IncidentWeatherFeatures(
        incident_id=incident_id,
        location_name=incident_id,
        target_timestamp=datetime(2026, 8, 13, 15, 0, tzinfo=UTC),
        latitude=52.113,
        longitude=-2.084,
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


def test_generate_temporal_controls_use_same_location_and_prior_dates():
    incident = feature_row("pershore-2026-08")

    controls = generate_temporal_controls([incident], day_offsets=(30, 60, 90))

    assert len(controls) == 3
    assert all(isinstance(control, TemporalControlLocation) for control in controls)
    assert all(control.latitude == incident.latitude for control in controls)
    assert all(control.longitude == incident.longitude for control in controls)
    assert {control.day_offset for control in controls} == {30, 60, 90}
    assert [control.target_timestamp.day for control in controls] == [14, 14, 15]
    assert all(control.target == 0 for control in controls)
    assert all(control.matched_incident_id == "pershore-2026-08" for control in controls)
    assert all(
        control.sampling_method == "same_location_temporal_offset_v1" for control in controls
    )


def test_generate_temporal_controls_are_deterministic_and_labeled():
    incidents = [feature_row("a"), feature_row("b")]

    controls = generate_temporal_controls(incidents, day_offsets=(14, 28))

    assert [control.control_id for control in controls] == [
        "control-a-temporal-14d",
        "control-a-temporal-28d",
        "control-b-temporal-14d",
        "control-b-temporal-28d",
    ]
