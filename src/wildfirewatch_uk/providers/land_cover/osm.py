from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

LAND_COVER_PRIORITY = {
    "heath_or_grass": 50,
    "woodland": 40,
    "scrub": 35,
    "farmland": 25,
    "built_up": 10,
    "water": 5,
}


def coarse_land_cover_from_tags(tags: dict[str, str]) -> str | None:
    natural = tags.get("natural")
    landuse = tags.get("landuse")
    leisure = tags.get("leisure")

    if natural in {"heath", "grassland", "fell", "moor"}:
        return "heath_or_grass"
    if landuse in {"grass", "meadow", "recreation_ground"} or leisure in {"park", "common"}:
        return "heath_or_grass"
    if natural in {"wood", "tree_row"} or landuse in {"forest", "wood"}:
        return "woodland"
    if natural in {"scrub", "shrubbery"}:
        return "scrub"
    if landuse in {"farmland", "farmyard", "orchard", "vineyard"}:
        return "farmland"
    if landuse in {"residential", "industrial", "commercial", "retail"}:
        return "built_up"
    if natural in {"water", "wetland", "bay"} or landuse in {"reservoir", "basin"}:
        return "water"
    return None


def build_overpass_point_query(
    *, latitude: float, longitude: float, radius_degrees: float = 0.003
) -> str:
    south = latitude - radius_degrees
    north = latitude + radius_degrees
    west = longitude - radius_degrees
    east = longitude + radius_degrees
    bbox = f"{south:.6f},{west:.6f},{north:.6f},{east:.6f}"
    return f"""
[out:json][timeout:25];
(
  way["natural"]({bbox});
  relation["natural"]({bbox});
  way["landuse"]({bbox});
  relation["landuse"]({bbox});
  way["leisure"]({bbox});
  relation["leisure"]({bbox});
);
out tags center 20;
""".strip()


def fetch_overpass_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "WildfireWatchUK/0.1"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:  # pragma: no cover - live network fallback
            last_error = error
            if attempt < 2:
                time.sleep(2**attempt)
    assert last_error is not None
    raise last_error


class OSMCoarseLandCoverClassifier:
    """Coarse OSM/Overpass land-cover classifier for prototype controls.

    This is suitable for an open-data prototype but not authoritative. OSM tagging
    coverage varies, and the result should be labelled as OSM-derived coarse class.
    """

    def __init__(
        self,
        *,
        overpass_url: str = OVERPASS_URL,
        radius_degrees: float = 0.003,
        fetcher: Callable[[str], dict[str, Any]] = fetch_overpass_json,
    ) -> None:
        self.overpass_url = overpass_url
        self.radius_degrees = radius_degrees
        self.fetcher = fetcher
        self._cache: dict[tuple[float, float], str | None] = {}

    def classify(self, *, latitude: float, longitude: float) -> str | None:
        cache_key = (round(latitude, 6), round(longitude, 6))
        if cache_key in self._cache:
            return self._cache[cache_key]
        query = build_overpass_point_query(
            latitude=latitude, longitude=longitude, radius_degrees=self.radius_degrees
        )
        url = self.overpass_url + "?" + urllib.parse.urlencode({"data": query})
        payload = self.fetcher(url)
        classes = [
            coarse_land_cover_from_tags(element.get("tags", {}))
            for element in payload.get("elements", [])
        ]
        result = max(
            (land_cover_class for land_cover_class in classes if land_cover_class is not None),
            key=lambda land_cover_class: LAND_COVER_PRIORITY[land_cover_class],
            default=None,
        )
        self._cache[cache_key] = result
        return result
