from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from wildfirewatch_uk.schemas.incident import (
    IncidentConfidence,
    IncidentRecord,
    IncidentSource,
    IncidentSourceType,
)


def valid_incident_payload() -> dict:
    return {
        "incident_id": "stourbridge-2026-08",
        "incident_name": "Stourbridge wildfire",
        "start_timestamp": "2026-08-13T16:30:00Z",
        "end_timestamp": None,
        "latitude": 52.4561,
        "longitude": -2.1487,
        "location_name": "Stourbridge",
        "fire_service": "Hereford & Worcester Fire and Rescue Service",
        "incident_type": "wildfire",
        "area_burned_ha": None,
        "buildings_threatened": None,
        "buildings_damaged": None,
        "evacuations": None,
        "injuries": None,
        "suspected_cause": None,
        "sources": [
            {
                "url": "https://example.test/incident-report",
                "source_type": "official_report",
                "title": "Example incident report",
            }
        ],
        "confidence": "needs_verification",
        "notes": "Seed record pending source verification.",
    }


def test_incident_record_accepts_canonical_fields():
    incident = IncidentRecord.model_validate(valid_incident_payload())

    assert incident.incident_id == "stourbridge-2026-08"
    assert incident.start_timestamp == datetime(2026, 8, 13, 16, 30, tzinfo=UTC)
    assert incident.confidence is IncidentConfidence.NEEDS_VERIFICATION
    assert incident.sources == [
        IncidentSource(
            url="https://example.test/incident-report",
            source_type=IncidentSourceType.OFFICIAL_REPORT,
            title="Example incident report",
        )
    ]


def test_incident_requires_at_least_one_source():
    payload = valid_incident_payload()
    payload["sources"] = []

    with pytest.raises(ValidationError, match="at least one source"):
        IncidentRecord.model_validate(payload)


def test_incident_rejects_end_before_start():
    payload = valid_incident_payload()
    payload["end_timestamp"] = "2026-08-13T15:00:00Z"

    with pytest.raises(ValidationError, match="end_timestamp"):
        IncidentRecord.model_validate(payload)


def test_incident_rejects_out_of_range_coordinates():
    payload = valid_incident_payload()
    payload["latitude"] = 120

    with pytest.raises(ValidationError):
        IncidentRecord.model_validate(payload)


def test_incident_rejects_negative_impact_counts():
    payload = valid_incident_payload()
    payload["injuries"] = -1

    with pytest.raises(ValidationError):
        IncidentRecord.model_validate(payload)
