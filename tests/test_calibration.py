import pytest

from wildfirewatch_uk.ml.calibration import correct_case_control_probability


def test_correct_case_control_probability_preserves_ordering():
    corrected_low = correct_case_control_probability(
        predicted_probability=0.2,
        sample_prevalence=0.25,
        target_prevalence=0.01,
    )
    corrected_high = correct_case_control_probability(
        predicted_probability=0.8,
        sample_prevalence=0.25,
        target_prevalence=0.01,
    )

    assert corrected_low < corrected_high


def test_correct_case_control_probability_reduces_rare_event_probabilities():
    corrected = correct_case_control_probability(
        predicted_probability=0.5,
        sample_prevalence=0.25,
        target_prevalence=0.01,
    )

    assert corrected == pytest.approx(0.029412, abs=1e-6)


def test_correct_case_control_probability_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="predicted_probability"):
        correct_case_control_probability(
            predicted_probability=1.1,
            sample_prevalence=0.25,
            target_prevalence=0.01,
        )
    with pytest.raises(ValueError, match="sample_prevalence"):
        correct_case_control_probability(
            predicted_probability=0.5,
            sample_prevalence=0.0,
            target_prevalence=0.01,
        )
    with pytest.raises(ValueError, match="target_prevalence"):
        correct_case_control_probability(
            predicted_probability=0.5,
            sample_prevalence=0.25,
            target_prevalence=1.0,
        )
