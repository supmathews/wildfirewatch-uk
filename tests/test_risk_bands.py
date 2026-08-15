from wildfirewatch_uk.ml.risk_bands import (
    CALIBRATED_RISK_BANDS,
    assign_risk_band,
    summarize_risk_bands,
)


def test_assign_risk_band_uses_ordered_calibrated_thresholds():
    assert assign_risk_band(0.0001).name == "very_low"
    assert assign_risk_band(0.003).name == "low"
    assert assign_risk_band(0.02).name == "elevated"
    assert assign_risk_band(0.08).name == "high"


def test_assign_risk_band_rejects_invalid_probability():
    for probability in (-0.1, 1.1):
        try:
            assign_risk_band(probability)
        except ValueError as error:
            assert "probability" in str(error)
        else:
            raise AssertionError("expected invalid probability to fail")


def test_risk_band_thresholds_are_monotonic():
    previous = -1.0
    for band in CALIBRATED_RISK_BANDS:
        assert band.lower_bound >= previous
        assert band.upper_bound > band.lower_bound
        previous = band.upper_bound


def test_summarize_risk_bands_counts_samples_and_positives():
    summary = summarize_risk_bands(
        [
            (0.0001, 0),
            (0.0002, 1),
            (0.0030, 0),
            (0.0200, 1),
        ]
    )

    assert summary["very_low"].sample_count == 2
    assert summary["very_low"].positive_count == 1
    assert summary["low"].sample_count == 1
    assert summary["elevated"].sample_count == 1
    assert summary["elevated"].positive_rate == 1.0
