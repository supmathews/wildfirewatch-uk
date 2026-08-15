from datetime import UTC, datetime

from wildfirewatch_uk.features.weather import HourlyWeatherObservation
from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.providers.weather.open_meteo import OpenMeteoArchiveClient
from wildfirewatch_uk.services.incident_weather_dataset import (
    build_features_for_seed_incidents,
    usable_incidents_for_weather,
)


class FakeOpenMeteoClient(OpenMeteoArchiveClient):
    def fetch_hourly_weather(self, **kwargs):
        return [
            HourlyWeatherObservation(
                timestamp=datetime(2026, 8, 1, 0, 0, tzinfo=UTC),
                precipitation_mm=2.0,
                temperature_2m_c=18.0,
                relative_humidity_2m_pct=55,
                wind_speed_10m_mps=2.0,
                wind_gust_10m_mps=4.0,
            ),
            HourlyWeatherObservation(
                timestamp=datetime(2026, 8, 13, 15, 0, tzinfo=UTC),
                precipitation_mm=0.0,
                temperature_2m_c=30.0,
                relative_humidity_2m_pct=25,
                wind_speed_10m_mps=3.0,
                wind_gust_10m_mps=7.0,
            ),
        ]


def test_usable_incidents_for_weather_filters_to_records_with_time_and_coordinates():
    incidents = usable_incidents_for_weather(load_seed_incidents())

    assert {incident.incident_id for incident in incidents} == {
        "cannock-chase-2026-08",
        "cannock-chase-sherbrook-valley-2026-08",
        "pershore-2026-08",
        "stoke-on-trent-2026-08",
        "rhandirmwyn-llandovery-2026-08",
    }


def test_build_features_for_seed_incidents_returns_one_row_per_usable_incident():
    rows = build_features_for_seed_incidents(client=FakeOpenMeteoClient())

    assert [row.incident_id for row in rows] == [
        "pershore-2026-08",
        "cannock-chase-2026-08",
        "cannock-chase-sherbrook-valley-2026-08",
        "stoke-on-trent-2026-08",
        "rhandirmwyn-llandovery-2026-08",
    ]
    assert all(row.source == "open-meteo-archive" for row in rows)
