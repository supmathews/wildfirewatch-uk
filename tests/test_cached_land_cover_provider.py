from pathlib import Path

import pytest

from wildfirewatch_uk.providers.land_cover.cached import CachedLandCoverClassifier


def test_cached_land_cover_classifier_returns_cached_value(tmp_path: Path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text('{"52.100000,-2.100000": "heath_or_grass"}\n')

    classifier = CachedLandCoverClassifier(cache_path=cache_path)

    assert classifier.classify(latitude=52.1, longitude=-2.1) == "heath_or_grass"


def test_cached_land_cover_classifier_returns_none_for_cached_null(tmp_path: Path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text('{"52.100000,-2.100000": null}\n')

    classifier = CachedLandCoverClassifier(cache_path=cache_path)

    assert classifier.classify(latitude=52.1, longitude=-2.1) is None


def test_cached_land_cover_classifier_raises_for_missing_key_by_default(tmp_path: Path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text("{}\n")
    classifier = CachedLandCoverClassifier(cache_path=cache_path)

    with pytest.raises(KeyError, match="No cached land-cover class"):
        classifier.classify(latitude=52.1, longitude=-2.1)


def test_cached_land_cover_classifier_can_tolerate_missing_key(tmp_path: Path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text("{}\n")
    classifier = CachedLandCoverClassifier(cache_path=cache_path, missing_ok=True)

    assert classifier.classify(latitude=52.1, longitude=-2.1) is None
