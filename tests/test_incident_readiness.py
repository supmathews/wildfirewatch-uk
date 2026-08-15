from datetime import UTC, datetime

from wildfirewatch_uk.schemas.incident import (
    IncidentConfidence,
    IncidentRecord,
    IncidentSource,
    IncidentSourceType,
)
from wildfirewatch_uk.services.incident_readiness import (
    IncidentReadinessStatus,
    audit_incident_readiness,
)


def incident(**overrides) -> IncidentRecord:
    payload = {
        "incident_id": "example-2026-08",
        "incident_name": "Example wildfire",
        "start_timestamp": datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
        "latitude": 52.0,
        "longitude": -2.0,
        "location_name": "Example",
        "incident_type": "wildfire",
        "sources": [
            IncidentSource(
                url="https://example.com/source",
                source_type=IncidentSourceType.NEWS_REPORT,
                title="Example source",
            )
        ],
        "confidence": IncidentConfidence.MEDIUM,
    }
    payload.update(overrides)
    return IncidentRecord.model_validate(payload)


def test_audit_marks_complete_incident_as_model_ready():
    [result] = audit_incident_readiness([incident()])

    assert result.status is IncidentReadinessStatus.MODEL_READY
    assert result.blockers == ()


def test_audit_blocks_missing_timestamp_and_coordinates():
    [result] = audit_incident_readiness(
        [incident(start_timestamp=None, latitude=None, longitude=None)]
    )

    assert result.status is IncidentReadinessStatus.BLOCKED
    assert result.blockers == (
        "missing_start_timestamp",
        "missing_latitude",
        "missing_longitude",
    )


def test_audit_blocks_needs_verification_and_placeholder_sources():
    [result] = audit_incident_readiness(
        [
            incident(
                confidence=IncidentConfidence.NEEDS_VERIFICATION,
                sources=[
                    IncidentSource(
                        url="https://placeholder.local/example",
                        source_type=IncidentSourceType.PLACEHOLDER,
                        title="Placeholder",
                    )
                ],
            )
        ]
    )

    assert result.status is IncidentReadinessStatus.BLOCKED
    assert "needs_verification" in result.blockers
    assert "placeholder_source" in result.blockers


def test_audit_seed_incidents_counts_current_model_ready_records():
    results = audit_incident_readiness()

    ready = [result for result in results if result.status is IncidentReadinessStatus.MODEL_READY]
    blocked = [result for result in results if result.status is IncidentReadinessStatus.BLOCKED]

    assert len(results) == 10
    assert len(ready) == 4
    assert len(blocked) == 6
    assert {result.incident_id for result in ready} == {
        "pershore-2026-08",
        "cannock-chase-sherbrook-valley-2026-08",
        "stoke-on-trent-2026-08",
        "rhandirmwyn-llandovery-2026-08",
    }
