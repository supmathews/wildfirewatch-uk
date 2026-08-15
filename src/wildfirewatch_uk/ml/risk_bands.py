from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskBand:
    name: str
    lower_bound: float
    upper_bound: float
    description: str


@dataclass(frozen=True)
class RiskBandSummary:
    band: RiskBand
    sample_count: int
    positive_count: int

    @property
    def positive_rate(self) -> float | None:
        if self.sample_count == 0:
            return None
        return round(self.positive_count / self.sample_count, 6)


CALIBRATED_RISK_BANDS = (
    RiskBand(
        name="very_low",
        lower_bound=0.0,
        upper_bound=0.001,
        description="Lowest calibrated diagnostic tier; not zero risk.",
    ),
    RiskBand(
        name="low",
        lower_bound=0.001,
        upper_bound=0.01,
        description="Low calibrated diagnostic tier.",
    ),
    RiskBand(
        name="elevated",
        lower_bound=0.01,
        upper_bound=0.05,
        description="Elevated diagnostic tier for retrospective ranking review.",
    ),
    RiskBand(
        name="high",
        lower_bound=0.05,
        upper_bound=1.000001,
        description="Highest diagnostic tier; not an operational warning label.",
    ),
)


def _validate_probability(probability: float) -> None:
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")


def assign_risk_band(probability: float) -> RiskBand:
    _validate_probability(probability)
    for band in CALIBRATED_RISK_BANDS:
        if band.lower_bound <= probability < band.upper_bound:
            return band
    return CALIBRATED_RISK_BANDS[-1]


def summarize_risk_bands(samples: list[tuple[float, int]]) -> dict[str, RiskBandSummary]:
    counts = {
        band.name: {"band": band, "sample_count": 0, "positive_count": 0}
        for band in CALIBRATED_RISK_BANDS
    }
    for probability, target in samples:
        band = assign_risk_band(probability)
        counts[band.name]["sample_count"] += 1
        counts[band.name]["positive_count"] += target
    return {
        name: RiskBandSummary(
            band=values["band"],
            sample_count=values["sample_count"],
            positive_count=values["positive_count"],
        )
        for name, values in counts.items()
    }
