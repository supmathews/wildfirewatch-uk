from __future__ import annotations

import json
from pathlib import Path


class CachedLandCoverClassifier:
    """Cache-only coarse land-cover classifier.

    This provider never calls external services. It is useful for deterministic
    tests/reports where missing cache entries should be explicit instead of
    quietly falling back to live Overpass.
    """

    def __init__(self, *, cache_path: Path, missing_ok: bool = False) -> None:
        self.cache_path = cache_path
        self.missing_ok = missing_ok
        self._cache = self._load_cache()

    def _load_cache(self) -> dict[tuple[float, float], str | None]:
        payload = json.loads(self.cache_path.read_text()) if self.cache_path.exists() else {}
        cache: dict[tuple[float, float], str | None] = {}
        for key, value in payload.items():
            latitude_text, longitude_text = key.split(",", maxsplit=1)
            cache[(float(latitude_text), float(longitude_text))] = value
        return cache

    def classify(self, *, latitude: float, longitude: float) -> str | None:
        cache_key = (round(latitude, 6), round(longitude, 6))
        if cache_key in self._cache:
            return self._cache[cache_key]
        if self.missing_ok:
            return None
        raise KeyError(
            "No cached land-cover class for "
            f"{cache_key[0]:.6f},{cache_key[1]:.6f} in {self.cache_path}"
        )
