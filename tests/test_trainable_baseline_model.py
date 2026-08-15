from wildfirewatch_uk.ml.baseline import FeatureDatasetRow
from wildfirewatch_uk.ml.trainable_baseline import (
    TrainableBaselineEvaluation,
    evaluate_trainable_logistic_baseline,
    featurize_row,
    train_logistic_regression,
)


def row(
    sample_id: str,
    target: int,
    *,
    temp: float,
    humidity: float,
    rain_7d: float,
    rain_30d: float,
    dry_days: int,
) -> FeatureDatasetRow:
    return FeatureDatasetRow(
        sample_id=sample_id,
        target=target,
        temperature_2m_c=temp,
        relative_humidity_2m_pct=humidity,
        wind_speed_10m_mps=3.0,
        wind_gust_10m_mps=9.0,
        rain_24h_mm=0.0,
        rain_7d_mm=rain_7d,
        rain_30d_mm=rain_30d,
        rain_60d_mm=rain_30d + 20.0,
        days_since_rain=dry_days,
        days_since_meaningful_rain=dry_days,
    )


def test_featurize_row_uses_normalized_weather_and_dryness_features():
    features = featurize_row(
        row("hot-dry", 1, temp=32.0, humidity=25.0, rain_7d=0.0, rain_30d=5.0, dry_days=14)
    )

    assert len(features) == 8
    assert all(0.0 <= value <= 1.0 for value in features)
    assert features[0] > 0.7  # temperature
    assert features[1] > 0.7  # low humidity transformed into risk-positive dryness
    assert features[4] == 1.0  # no 7d rain is maximally dry for this feature


def test_train_logistic_regression_learns_hot_dry_rows_score_higher():
    rows = [
        row("fire-1", 1, temp=34.0, humidity=20.0, rain_7d=0.0, rain_30d=4.0, dry_days=18),
        row("fire-2", 1, temp=32.0, humidity=24.0, rain_7d=1.0, rain_30d=6.0, dry_days=16),
        row("fire-3", 1, temp=30.0, humidity=30.0, rain_7d=2.0, rain_30d=10.0, dry_days=10),
        row("control-1", 0, temp=17.0, humidity=80.0, rain_7d=25.0, rain_30d=70.0, dry_days=0),
        row("control-2", 0, temp=18.0, humidity=75.0, rain_7d=30.0, rain_30d=90.0, dry_days=1),
        row("control-3", 0, temp=20.0, humidity=68.0, rain_7d=18.0, rain_30d=60.0, dry_days=2),
    ]

    model = train_logistic_regression(rows, epochs=900, learning_rate=0.8)

    hot_dry_score = model.predict_proba(featurize_row(rows[0]))
    cool_wet_score = model.predict_proba(featurize_row(rows[-1]))
    assert hot_dry_score > cool_wet_score


def test_evaluate_trainable_logistic_baseline_returns_ranking_metrics():
    rows = [
        row("fire-1", 1, temp=34.0, humidity=20.0, rain_7d=0.0, rain_30d=4.0, dry_days=18),
        row("fire-2", 1, temp=32.0, humidity=24.0, rain_7d=1.0, rain_30d=6.0, dry_days=16),
        row("control-1", 0, temp=17.0, humidity=80.0, rain_7d=25.0, rain_30d=70.0, dry_days=0),
        row("control-2", 0, temp=18.0, humidity=75.0, rain_7d=30.0, rain_30d=90.0, dry_days=1),
    ]

    evaluation = evaluate_trainable_logistic_baseline(
        rows,
        top_percentages=(50, 100),
        epochs=600,
        learning_rate=0.7,
    )

    assert isinstance(evaluation, TrainableBaselineEvaluation)
    assert evaluation.sample_count == 4
    assert evaluation.positive_count == 2
    assert evaluation.recall_at_top_percent[50] >= 0.5
    assert evaluation.roc_auc is not None
    assert evaluation.pr_auc is not None
    assert evaluation.scored_rows[0].risk_score >= evaluation.scored_rows[-1].risk_score
