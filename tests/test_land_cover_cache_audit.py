from pathlib import Path

from wildfirewatch_uk.services.land_cover_cache_audit import audit_land_cover_cache


def test_audit_land_cover_cache_counts_cached_and_missing_points(tmp_path: Path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text(
        '{"52.100000,-2.100000": "heath_or_grass", "52.200000,-2.200000": null}\n'
    )

    audit = audit_land_cover_cache(
        cache_path=cache_path,
        points=[
            ("ready", 52.1, -2.1),
            ("unknown", 52.2, -2.2),
            ("missing", 52.3, -2.3),
        ],
    )

    assert audit.point_count == 3
    assert audit.classified_count == 1
    assert audit.null_count == 1
    assert audit.missing_count == 1
    assert audit.coverage_ratio == 1 / 3
    assert [row.status for row in audit.rows] == ["classified", "null", "missing"]


def test_current_model_ready_incidents_have_cached_land_cover():
    audit = audit_land_cover_cache()

    assert audit.point_count == 5
    assert audit.classified_count == 5
    assert audit.null_count == 0
    assert audit.missing_count == 0
    assert audit.coverage_ratio == 1.0
    assert {row.land_cover_class for row in audit.rows} == {"heath_or_grass", "woodland"}
