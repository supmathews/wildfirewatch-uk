from wildfirewatch_uk.ml.baseline import ScoredDatasetRow
from wildfirewatch_uk.ml.uncertainty import bootstrap_metric_interval, bootstrap_metric_intervals


def scored(sample_id: str, target: int, risk_score: float) -> ScoredDatasetRow:
    return ScoredDatasetRow(
        sample_id=sample_id,
        target=target,
        temperature_2m_c=None,
        relative_humidity_2m_pct=None,
        wind_speed_10m_mps=None,
        wind_gust_10m_mps=None,
        rain_24h_mm=0.0,
        rain_7d_mm=0.0,
        rain_30d_mm=0.0,
        rain_60d_mm=0.0,
        days_since_rain=None,
        days_since_meaningful_rain=None,
        risk_score=risk_score,
    )


def test_bootstrap_metric_interval_is_deterministic():
    rows = [
        scored("a", 1, 0.9),
        scored("b", 1, 0.8),
        scored("c", 0, 0.2),
        scored("d", 0, 0.1),
    ]

    first = bootstrap_metric_interval(rows, metric="roc_auc", iterations=50, seed=7)
    second = bootstrap_metric_interval(rows, metric="roc_auc", iterations=50, seed=7)

    assert first == second
    assert first.metric == "roc_auc"
    assert first.point_estimate == 1.0
    assert first.valid_resamples <= 50
    assert first.lower <= first.point_estimate <= first.upper


def test_bootstrap_metric_interval_tracks_skipped_resamples():
    rows = [
        scored("a", 1, 0.9),
        scored("b", 0, 0.2),
    ]

    interval = bootstrap_metric_interval(rows, metric="pr_auc", iterations=30, seed=3)

    assert interval.valid_resamples < 30
    assert interval.skipped_resamples > 0


def test_bootstrap_metric_intervals_returns_requested_metrics():
    rows = [
        scored("a", 1, 0.9),
        scored("b", 1, 0.8),
        scored("c", 0, 0.2),
        scored("d", 0, 0.1),
    ]

    intervals = bootstrap_metric_intervals(rows, metrics=("roc_auc", "pr_auc"), iterations=25)

    assert tuple(interval.metric for interval in intervals) == ("roc_auc", "pr_auc")
    assert all(interval.sample_count == 4 for interval in intervals)
