from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.ml.feature_ablation import (
    FEATURE_FAMILIES,
    ablate_row,
    evaluate_feature_families,
)


def row(sample_id: str, target: int) -> FeatureDatasetRow:
    return FeatureDatasetRow(
        sample_id=sample_id,
        target=target,
        temperature_2m_c=30.0,
        relative_humidity_2m_pct=25.0,
        wind_speed_10m_mps=4.0,
        wind_gust_10m_mps=9.0,
        rain_24h_mm=0.5,
        rain_7d_mm=4.0,
        rain_30d_mm=20.0,
        rain_60d_mm=60.0,
        days_since_rain=3,
        days_since_meaningful_rain=10,
    )


def test_ablate_row_keeps_only_latest_weather_family():
    ablated = ablate_row(row("sample", 1), "latest_weather")

    assert ablated.temperature_2m_c == 30.0
    assert ablated.relative_humidity_2m_pct == 25.0
    assert ablated.wind_speed_10m_mps == 4.0
    assert ablated.wind_gust_10m_mps == 9.0
    assert ablated.rain_24h_mm == 0.0
    assert ablated.rain_7d_mm == 0.0
    assert ablated.rain_30d_mm == 0.0
    assert ablated.rain_60d_mm == 0.0
    assert ablated.days_since_rain is None
    assert ablated.days_since_meaningful_rain is None


def test_ablate_row_keeps_only_rainfall_windows_family():
    ablated = ablate_row(row("sample", 1), "rainfall_windows")

    assert ablated.temperature_2m_c is None
    assert ablated.relative_humidity_2m_pct is None
    assert ablated.wind_speed_10m_mps is None
    assert ablated.wind_gust_10m_mps is None
    assert ablated.rain_24h_mm == 0.5
    assert ablated.rain_7d_mm == 4.0
    assert ablated.rain_30d_mm == 20.0
    assert ablated.rain_60d_mm == 60.0
    assert ablated.days_since_rain is None
    assert ablated.days_since_meaningful_rain is None


def test_evaluate_feature_families_returns_all_requested_families():
    rows = [
        row("fire-a", 1),
        row("control-fire-a-temporal-30d", 0),
        row("fire-b", 1),
        row("control-fire-b-temporal-30d", 0),
        row("fire-c", 1),
        row("control-fire-c-temporal-30d", 0),
    ]

    results = evaluate_feature_families(rows, families=("all", "latest_weather"))

    assert tuple(result.family for result in results) == ("all", "latest_weather")
    assert all(result.sample_count == len(rows) for result in results)
    assert all(result.positive_count == 3 for result in results)


def test_feature_families_include_landscape_recommended_stages():
    assert FEATURE_FAMILIES == (
        "all",
        "latest_weather",
        "rainfall_windows",
        "dry_spell_memory",
        "rainfall_and_dry_spell",
    )
