import json

from wildfirewatch_uk.providers.land_cover.osm import (
    OSMCoarseLandCoverClassifier,
    build_overpass_point_query,
    coarse_land_cover_from_tags,
)


def test_coarse_land_cover_from_osm_tags_prioritizes_wildfire_relevant_classes():
    assert coarse_land_cover_from_tags({"natural": "heath"}) == "heath_or_grass"
    assert coarse_land_cover_from_tags({"natural": "grassland"}) == "heath_or_grass"
    assert coarse_land_cover_from_tags({"landuse": "forest"}) == "woodland"
    assert coarse_land_cover_from_tags({"natural": "wood"}) == "woodland"
    assert coarse_land_cover_from_tags({"landuse": "residential"}) == "built_up"
    assert coarse_land_cover_from_tags({"natural": "water"}) == "water"
    assert coarse_land_cover_from_tags({"amenity": "parking"}) is None


def test_build_overpass_point_query_contains_bbox_and_relevant_keys():
    query = build_overpass_point_query(latitude=52.1, longitude=-2.2, radius_degrees=0.005)

    assert "52.095" in query
    assert "52.105" in query
    assert "-2.205" in query
    assert "-2.195" in query
    assert "natural" in query
    assert "landuse" in query


def test_osm_classifier_parses_fetcher_payload_and_caches_by_rounded_point():
    calls = []

    def fetcher(url: str) -> dict:
        calls.append(url)
        return {
            "elements": [
                {"tags": {"landuse": "residential"}},
                {"tags": {"natural": "heath"}},
            ]
        }

    classifier = OSMCoarseLandCoverClassifier(fetcher=fetcher)

    assert classifier.classify(latitude=52.12345671, longitude=-2.76543219) == "heath_or_grass"
    assert classifier.classify(latitude=52.12345674, longitude=-2.76543216) == "heath_or_grass"
    assert len(calls) == 1


def test_osm_classifier_returns_none_when_payload_has_no_relevant_tags():
    classifier = OSMCoarseLandCoverClassifier(fetcher=lambda _url: {"elements": []})

    assert classifier.classify(latitude=52.0, longitude=-2.0) is None


def test_osm_classifier_can_treat_fetch_errors_as_unknown():
    def fetcher(_url: str) -> dict:
        raise TimeoutError("overpass unavailable")

    classifier = OSMCoarseLandCoverClassifier(fetcher=fetcher, suppress_fetch_errors=True)

    assert classifier.classify(latitude=52.0, longitude=-2.0) is None


def test_osm_classifier_persists_cache_between_instances(tmp_path):
    cache_path = tmp_path / "osm_land_cover_cache.json"
    calls = []

    def fetcher(url: str) -> dict:
        calls.append(url)
        return {"elements": [{"tags": {"natural": "wood"}}]}

    first = OSMCoarseLandCoverClassifier(fetcher=fetcher, cache_path=cache_path)
    assert first.classify(latitude=52.123456, longitude=-2.654321) == "woodland"
    assert json.loads(cache_path.read_text()) == {"52.123456,-2.654321": "woodland"}

    second = OSMCoarseLandCoverClassifier(
        fetcher=lambda _url: (_ for _ in ()).throw(AssertionError("should use cache")),
        cache_path=cache_path,
    )
    assert second.classify(latitude=52.123456, longitude=-2.654321) == "woodland"
    assert len(calls) == 1
