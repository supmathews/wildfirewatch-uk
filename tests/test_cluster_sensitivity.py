from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.ml.cluster_sensitivity import (
    ClusterSensitivityScenario,
    evaluate_cluster_sensitivity,
    filter_rows_by_excluded_groups,
)


def _row(sample_id: str, *, target: int, rain_7d_mm: float = 0.0) -> FeatureDatasetRow:
    return FeatureDatasetRow(
        sample_id=sample_id,
        target=target,
        temperature_2m_c=30.0,
        relative_humidity_2m_pct=30.0,
        wind_speed_10m_mps=2.0,
        wind_gust_10m_mps=4.0,
        rain_24h_mm=0.0,
        rain_7d_mm=rain_7d_mm,
        rain_30d_mm=rain_7d_mm,
        rain_60d_mm=rain_7d_mm,
        days_since_rain=5,
        days_since_meaningful_rain=10,
    )


def test_filter_rows_by_excluded_groups_removes_positive_and_controls():
    rows = [
        _row("first", target=1),
        _row("control-first-temporal-30d", target=0),
        _row("second", target=1),
        _row("control-second-temporal-30d", target=0),
    ]

    filtered = filter_rows_by_excluded_groups(rows, excluded_group_ids={"first"})

    assert [row.sample_id for row in filtered] == [
        "second",
        "control-second-temporal-30d",
    ]


def test_evaluate_cluster_sensitivity_runs_all_scenarios():
    rows: list[FeatureDatasetRow] = []
    for index, incident_id in enumerate(("a", "b", "c", "d"), start=1):
        rows.append(_row(incident_id, target=1, rain_7d_mm=float(index)))
        rows.append(_row(f"control-{incident_id}-temporal-30d", target=0, rain_7d_mm=10.0 + index))
        rows.append(_row(f"control-{incident_id}-temporal-60d", target=0, rain_7d_mm=20.0 + index))

    scenarios = evaluate_cluster_sensitivity(
        rows,
        exclusions={
            "all_model_ready": set(),
            "drop_a": {"a"},
        },
    )

    assert [scenario.name for scenario in scenarios] == ["all_model_ready", "drop_a"]
    assert scenarios[0].sample_count == 12
    assert scenarios[0].positive_count == 4
    assert scenarios[1].sample_count == 9
    assert scenarios[1].positive_count == 3
    assert isinstance(scenarios[0], ClusterSensitivityScenario)
