from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime
from typing import Any

from wildfirewatch_uk.features.weather import HourlyWeatherObservation

KMH_TO_MPS = 1000 / 3600


class OpenMeteoArchiveClient:
    """Minimal Open-Meteo historical weather client.

    This is a development fallback provider with explicit provenance. It should
    be swappable once authoritative UK rainfall/weather sources are selected.
    """

    base_url = "https://archive-api.open-meteo.com/v1/archive"
    hourly_variables = (
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "wind_gusts_10m",
    )

    def build_url(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> str:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(self.hourly_variables),
            "timezone": "UTC",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
        }
        return self.base_url + "?" + urllib.parse.urlencode(params)

    def fetch_hourly_weather(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> list[HourlyWeatherObservation]:
        url = self.build_url(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
        )
        request = urllib.request.Request(url, headers={"User-Agent": "WildfireWatchUK/0.1"})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return parse_open_meteo_hourly_response(payload)


def _value(values: list[Any], index: int) -> Any:
    try:
        return values[index]
    except IndexError:
        return None


def _kmh_to_mps(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value * KMH_TO_MPS, 3)


def parse_open_meteo_hourly_response(payload: dict[str, Any]) -> list[HourlyWeatherObservation]:
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    wind_speeds = hourly.get("wind_speed_10m", [])
    wind_gusts = hourly.get("wind_gusts_10m", [])
    precipitation = hourly.get("precipitation", [])

    observations = []
    for index, timestamp_text in enumerate(times):
        observations.append(
            HourlyWeatherObservation(
                timestamp=datetime.fromisoformat(timestamp_text).replace(tzinfo=UTC),
                temperature_2m_c=_value(temperatures, index),
                relative_humidity_2m_pct=_value(humidities, index),
                wind_speed_10m_mps=_kmh_to_mps(_value(wind_speeds, index)),
                wind_gust_10m_mps=_kmh_to_mps(_value(wind_gusts, index)),
                precipitation_mm=_value(precipitation, index),
            )
        )
    return observations
