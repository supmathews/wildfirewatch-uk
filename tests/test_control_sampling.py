from datetime import UTC, datetime

from wildfirewatch_uk.features.controls import ControlLocation, generate_matched_controls
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


def test_generate_matched_controls_is_deterministic_and_labeled():
    incidents = [feature_row("a", 52.0, -2.0), feature_row("b", 53.0, -3.0)]

    controls = generate_matched_controls(incidents, controls_per_incident=3, seed=42)

    assert len(controls) == 6
    assert controls == generate_matched_controls(incidents, controls_per_incident=3, seed=42)
    assert all(isinstance(control, ControlLocation) for control in controls)
    assert all(control.target == 0 for control in controls)
    assert {control.matched_incident_id for control in controls} == {"a", "b"}


def test_generate_matched_controls_keep_same_target_time_but_offset_location():
    incident = feature_row("pershore-2026-08", 52.113, -2.084)

    controls = generate_matched_controls([incident], controls_per_incident=5, seed=1)

    assert all(control.target_timestamp == incident.target_timestamp for control in controls)
    assert all(control.latitude != incident.latitude for control in controls)
    assert all(control.longitude != incident.longitude for control in controls)
    assert all(49.8 <= control.latitude <= 58.8 for control in controls)
    assert all(-8.7 <= control.longitude <= 1.8 for control in controls)
