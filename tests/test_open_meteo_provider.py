from datetime import date

from wildfirewatch_uk.providers.weather.open_meteo import (
    OpenMeteoArchiveClient,
    parse_open_meteo_hourly_response,
)


def test_parse_open_meteo_hourly_response_maps_units_and_timestamps():
    payload = {
        "latitude": 52.0,
        "longitude": -2.0,
        "hourly": {
            "time": ["2026-08-13T14:00", "2026-08-13T15:00"],
            "temperature_2m": [29.5, 31.2],
            "relative_humidity_2m": [28, 25],
            "wind_speed_10m": [14.4, 18.0],
            "wind_gusts_10m": [28.8, 36.0],
            "precipitation": [0.0, 0.2],
        },
    }

    observations = parse_open_meteo_hourly_response(payload)

    assert len(observations) == 2
    assert observations[0].timestamp.isoformat() == "2026-08-13T14:00:00+00:00"
    assert observations[0].temperature_2m_c == 29.5
    assert observations[0].relative_humidity_2m_pct == 28
    assert observations[0].wind_speed_10m_mps == 4.0
    assert observations[0].wind_gust_10m_mps == 8.0
    assert observations[1].precipitation_mm == 0.2


def test_open_meteo_client_builds_archive_url_with_required_variables():
    client = OpenMeteoArchiveClient()

    url = client.build_url(
        latitude=52.113,
        longitude=-2.084,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 8, 13),
    )

    assert url.startswith("https://archive-api.open-meteo.com/v1/archive?")
    assert "latitude=52.113" in url
    assert "longitude=-2.084" in url
    assert "start_date=2026-07-01" in url
    assert "end_date=2026-08-13" in url
    assert "temperature_2m" in url
    assert "relative_humidity_2m" in url
    assert "precipitation" in url
    assert "wind_speed_10m" in url
    assert "wind_gusts_10m" in url
    assert "timezone=UTC" in url
