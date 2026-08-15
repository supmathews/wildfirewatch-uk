from datetime import UTC, datetime, timedelta

from wildfirewatch_uk.features.weather import (
    HourlyWeatherObservation,
    build_incident_weather_features,
    compute_rainfall_windows,
    days_since_rain,
)
from wildfirewatch_uk.schemas.incident import IncidentRecord, IncidentSource


def hourly(ts: datetime, rain: float, temp: float = 20, humidity: float = 50):
    return HourlyWeatherObservation(
        timestamp=ts,
        temperature_2m_c=temp,
        relative_humidity_2m_pct=humidity,
        wind_speed_10m_mps=3.0,
        wind_gust_10m_mps=5.0,
        precipitation_mm=rain,
    )


def test_compute_rainfall_windows_uses_only_data_before_target():
    target = datetime(2026, 8, 13, 15, 0, tzinfo=UTC)
    observations = [
        hourly(target - timedelta(hours=2), 1.5),
        hourly(target - timedelta(days=3), 2.0),
        hourly(target - timedelta(days=20), 3.0),
        hourly(target + timedelta(hours=1), 99.0),
    ]

    windows = compute_rainfall_windows(observations, target)

    assert windows.rain_24h_mm == 1.5
    assert windows.rain_7d_mm == 3.5
    assert windows.rain_30d_mm == 6.5
    assert windows.rain_60d_mm == 6.5


def test_days_since_rain_respects_thresholds_and_target_time():
    target = datetime(2026, 8, 13, 15, 0, tzinfo=UTC)
    observations = [
        hourly(target - timedelta(hours=10), 0.3),
        hourly(target - timedelta(days=5), 2.0),
        hourly(target + timedelta(hours=1), 5.0),
    ]

    assert days_since_rain(observations, target, threshold_mm=0.2) == 0
    assert days_since_rain(observations, target, threshold_mm=1.0) == 5


def test_build_incident_weather_features_requires_timestamp_and_coordinates():
    incident = IncidentRecord(
        incident_id="example-2026-08",
        incident_name="Example wildfire",
        start_timestamp=datetime(2026, 8, 13, 16, 0, tzinfo=UTC),
        latitude=52.0,
        longitude=-2.0,
        location_name="Example",
        sources=[
            IncidentSource(
                url="https://example.test/source",
                source_type="news_report",
                title="Example source",
            )
        ],
    )
    observations = [
        hourly(datetime(2026, 8, 13, 15, 0, tzinfo=UTC), 0.0, temp=30, humidity=25),
        hourly(datetime(2026, 8, 1, 15, 0, tzinfo=UTC), 2.0, temp=20, humidity=50),
    ]

    features = build_incident_weather_features(incident, observations)

    assert features.incident_id == "example-2026-08"
    assert features.target_timestamp == datetime(2026, 8, 13, 16, 0, tzinfo=UTC)
    assert features.rain_30d_mm == 2.0
    assert features.days_since_meaningful_rain == 12
    assert features.temperature_2m_c == 30
    assert features.relative_humidity_2m_pct == 25
