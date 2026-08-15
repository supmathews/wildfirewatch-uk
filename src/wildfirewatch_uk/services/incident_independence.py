from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations

from pydantic import BaseModel

from wildfirewatch_uk.features.controls import distance_km
from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.schemas.incident import IncidentConfidence, IncidentRecord


class IncidentClusterPair(BaseModel):
    incident_id_a: str
    incident_id_b: str
    distance_km: float
    days_apart: int
    reason: str


class IncidentIndependenceAudit(BaseModel):
    model_ready_incident_count: int
    cluster_pair_count: int
    cluster_pairs: list[IncidentClusterPair]


def _is_model_ready(incident: IncidentRecord) -> bool:
    return (
        incident.start_timestamp is not None
        and incident.latitude is not None
        and incident.longitude is not None
        and incident.confidence is not IncidentConfidence.NEEDS_VERIFICATION
    )


def audit_incident_independence(
    incidents: Sequence[IncidentRecord] | None = None,
    *,
    distance_threshold_km: float = 10.0,
    day_threshold: int = 14,
) -> IncidentIndependenceAudit:
    """Flag model-ready incidents that may not be independent examples.

    A pair is flagged when both incidents are model-ready, geographically close,
    and temporally close. This does not merge or delete incidents; it documents
    a small-sample evaluation caveat so metrics are not over-interpreted.
    """

    if incidents is None:
        incidents = load_seed_incidents()
    ready = [incident for incident in incidents if _is_model_ready(incident)]
    cluster_pairs: list[IncidentClusterPair] = []
    for first, second in combinations(ready, 2):
        assert first.latitude is not None
        assert first.longitude is not None
        assert second.latitude is not None
        assert second.longitude is not None
        assert first.start_timestamp is not None
        assert second.start_timestamp is not None
        separation_km = distance_km(
            first.latitude, first.longitude, second.latitude, second.longitude
        )
        days_apart = abs((first.start_timestamp.date() - second.start_timestamp.date()).days)
        if separation_km <= distance_threshold_km and days_apart <= day_threshold:
            cluster_pairs.append(
                IncidentClusterPair(
                    incident_id_a=first.incident_id,
                    incident_id_b=second.incident_id,
                    distance_km=round(separation_km, 2),
                    days_apart=days_apart,
                    reason=f"within_{distance_threshold_km:.1f}km_and_{day_threshold}d",
                )
            )
    return IncidentIndependenceAudit(
        model_ready_incident_count=len(ready),
        cluster_pair_count=len(cluster_pairs),
        cluster_pairs=cluster_pairs,
    )
