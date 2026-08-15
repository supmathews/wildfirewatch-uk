from datetime import UTC, datetime

from wildfirewatch_uk.schemas.incident import (
    IncidentConfidence,
    IncidentRecord,
    IncidentSource,
    IncidentSourceType,
)
from wildfirewatch_uk.services.incident_independence import (
    IncidentClusterPair,
    audit_incident_independence,
)


def _incident(
    incident_id: str,
    *,
    latitude: float,
    longitude: float,
    day: int,
) -> IncidentRecord:
    return IncidentRecord(
        incident_id=incident_id,
        incident_name=incident_id,
        start_timestamp=datetime(2026, 8, day, 12, 0, tzinfo=UTC),
        latitude=latitude,
        longitude=longitude,
        location_name=incident_id,
        incident_type="wildfire",
        confidence=IncidentConfidence.HIGH,
        sources=[
            IncidentSource(
                url=f"https://example.com/{incident_id}",
                source_type=IncidentSourceType.NEWS_REPORT,
                title=incident_id,
            )
        ],
    )


def test_audit_flags_close_incidents_within_time_window():
    first = _incident("first", latitude=52.75, longitude=-2.00, day=1)
    second = _incident("second", latitude=52.77, longitude=-2.04, day=7)
    distant = _incident("distant", latitude=53.50, longitude=-1.00, day=8)

    audit = audit_incident_independence(
        [first, second, distant], distance_threshold_km=10.0, day_threshold=14
    )

    assert audit.model_ready_incident_count == 3
    assert audit.cluster_pair_count == 1
    assert audit.cluster_pairs == [
        IncidentClusterPair(
            incident_id_a="first",
            incident_id_b="second",
            distance_km=3.49,
            days_apart=6,
            reason="within_10.0km_and_14d",
        )
    ]


def test_audit_ignores_blocked_incidents():
    ready = _incident("ready", latitude=52.75, longitude=-2.00, day=1)
    blocked = _incident("blocked", latitude=52.77, longitude=-2.04, day=7)
    blocked.start_timestamp = None

    audit = audit_incident_independence([ready, blocked])

    assert audit.model_ready_incident_count == 1
    assert audit.cluster_pair_count == 0


def test_current_seed_audit_flags_cannock_chase_cluster():
    audit = audit_incident_independence()

    assert audit.model_ready_incident_count == 5
    pair_ids = {frozenset((pair.incident_id_a, pair.incident_id_b)) for pair in audit.cluster_pairs}
    assert frozenset(
        (
            "cannock-chase-2026-08",
            "cannock-chase-sherbrook-valley-2026-08",
        )
    ) in pair_ids
