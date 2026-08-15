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
