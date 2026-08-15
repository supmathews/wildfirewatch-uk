from wildfirewatch_uk.ml.baseline import (
    BaselineEvaluation,
    FeatureDatasetRow,
    evaluate_baseline_ranking,
    score_baseline_risk,
)


def row(target: int, rain_7d: float, rain_30d: float, days: int, temp: float, humidity: float):
    return FeatureDatasetRow(
        sample_id=f"sample-{target}-{rain_7d}-{days}",
        target=target,
        temperature_2m_c=temp,
        relative_humidity_2m_pct=humidity,
        wind_speed_10m_mps=4.0,
        wind_gust_10m_mps=8.0,
        rain_24h_mm=0.0,
        rain_7d_mm=rain_7d,
        rain_30d_mm=rain_30d,
        rain_60d_mm=40.0,
        days_since_rain=days,
        days_since_meaningful_rain=days,
    )


def test_score_baseline_risk_ranks_hot_dry_windy_low_humidity_higher():
    high = row(target=1, rain_7d=0.0, rain_30d=3.0, days=12, temp=35.0, humidity=20.0)
    low = row(target=0, rain_7d=20.0, rain_30d=70.0, days=0, temp=18.0, humidity=80.0)

    assert score_baseline_risk(high) > score_baseline_risk(low)
    assert 0 <= score_baseline_risk(low) <= 100
    assert 0 <= score_baseline_risk(high) <= 100


def test_evaluate_baseline_ranking_reports_recall_at_top_buckets():
    rows = [
        row(1, 0.0, 2.0, 15, 35.0, 20.0),
        row(1, 0.0, 5.0, 10, 32.0, 25.0),
        row(0, 20.0, 80.0, 0, 19.0, 75.0),
        row(0, 12.0, 60.0, 1, 21.0, 65.0),
        row(0, 8.0, 55.0, 2, 23.0, 60.0),
    ]

    evaluation = evaluate_baseline_ranking(rows, top_percentages=(40, 60, 100))

    assert isinstance(evaluation, BaselineEvaluation)
    assert evaluation.positive_count == 2
    assert evaluation.sample_count == 5
    assert evaluation.recall_at_top_percent[40] == 1.0
    assert evaluation.recall_at_top_percent[60] == 1.0
    assert evaluation.recall_at_top_percent[100] == 1.0
