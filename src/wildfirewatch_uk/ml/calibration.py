from __future__ import annotations


def _validate_probability(name: str, value: float, *, allow_endpoints: bool) -> None:
    valid = 0.0 <= value <= 1.0 if allow_endpoints else 0.0 < value < 1.0
    if not valid:
        interval = "[0, 1]" if allow_endpoints else "(0, 1)"
        raise ValueError(f"{name} must be in {interval}")


def correct_case_control_probability(
    *, predicted_probability: float, sample_prevalence: float, target_prevalence: float
) -> float:
    """Correct a case-control model probability to a target rare-event prevalence.

    Case/control training data often over-samples positives. The model's raw probability
    is therefore calibrated to the sample prevalence, not the real-world prevalence. This
    prior-probability correction preserves ranking while moving the probability scale
    toward an assumed target prevalence.
    """

    _validate_probability("predicted_probability", predicted_probability, allow_endpoints=True)
    _validate_probability("sample_prevalence", sample_prevalence, allow_endpoints=False)
    _validate_probability("target_prevalence", target_prevalence, allow_endpoints=False)

    if predicted_probability in {0.0, 1.0}:
        return predicted_probability

    positive_weight = target_prevalence / sample_prevalence
    negative_weight = (1.0 - target_prevalence) / (1.0 - sample_prevalence)
    numerator = predicted_probability * positive_weight
    denominator = numerator + (1.0 - predicted_probability) * negative_weight
    return round(numerator / denominator, 6)
