from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.ml.out_of_sample import (
    LeaveOneIncidentOutEvaluation,
    evaluate_leave_one_incident_out,
    incident_group_id,
)


def row(sample_id: str, target: int, temp: float, rain_7d: float) -> FeatureDatasetRow:
    return FeatureDatasetRow(
        sample_id=sample_id,
        target=target,
        temperature_2m_c=temp,
        relative_humidity_2m_pct=30.0 if target else 70.0,
        wind_speed_10m_mps=4.0,
        wind_gust_10m_mps=10.0,
        rain_24h_mm=0.0,
        rain_7d_mm=rain_7d,
        rain_30d_mm=rain_7d + 10.0,
        rain_60d_mm=rain_7d + 30.0,
        days_since_rain=10 if target else 1,
        days_since_meaningful_rain=10 if target else 1,
    )


def test_incident_group_id_maps_controls_to_matched_positive():
    assert incident_group_id(row("pershore-2026-08", 1, 33.0, 0.0)) == "pershore-2026-08"
    assert (
        incident_group_id(row("control-pershore-2026-08-005", 0, 21.0, 12.0))
        == "pershore-2026-08"
    )


def test_leave_one_incident_out_holds_out_positive_and_its_controls():
    rows = [
        row("fire-a", 1, 34.0, 0.0),
        row("control-fire-a-001", 0, 18.0, 25.0),
        row("control-fire-a-002", 0, 19.0, 22.0),
        row("fire-b", 1, 33.0, 1.0),
        row("control-fire-b-001", 0, 17.0, 30.0),
        row("control-fire-b-002", 0, 18.0, 28.0),
        row("fire-c", 1, 31.0, 2.0),
        row("control-fire-c-001", 0, 20.0, 18.0),
        row("control-fire-c-002", 0, 19.0, 21.0),
    ]

    evaluation = evaluate_leave_one_incident_out(
        rows,
        top_percentages=(50, 100),
        epochs=700,
        learning_rate=0.7,
    )

    assert isinstance(evaluation, LeaveOneIncidentOutEvaluation)
    assert evaluation.fold_count == 3
    assert evaluation.sample_count == 9
    assert evaluation.positive_count == 3
    assert set(evaluation.fold_metrics) == {"fire-a", "fire-b", "fire-c"}
    assert evaluation.recall_at_top_percent[100] == 1.0
    assert evaluation.roc_auc is not None
    assert evaluation.pr_auc is not None
    assert all(fold.test_sample_count == 3 for fold in evaluation.fold_metrics.values())
