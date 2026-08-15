from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.schemas.incident import (
    IncidentConfidence,
    IncidentRecord,
    IncidentSourceType,
)


class IncidentReadinessStatus(StrEnum):
    MODEL_READY = "model_ready"
    BLOCKED = "blocked"


class IncidentReadinessResult(BaseModel):
    incident_id: str
    location_name: str
    status: IncidentReadinessStatus
    blockers: tuple[str, ...]
    notes: str | None = None


def readiness_blockers(incident: IncidentRecord) -> tuple[str, ...]:
    blockers: list[str] = []
    if incident.confidence is IncidentConfidence.NEEDS_VERIFICATION:
        blockers.append("needs_verification")
    if incident.start_timestamp is None:
        blockers.append("missing_start_timestamp")
    if incident.latitude is None:
        blockers.append("missing_latitude")
    if incident.longitude is None:
        blockers.append("missing_longitude")
    if any(source.source_type is IncidentSourceType.PLACEHOLDER for source in incident.sources):
        blockers.append("placeholder_source")
    return tuple(blockers)


def audit_incident_readiness(
    incidents: list[IncidentRecord] | tuple[IncidentRecord, ...] | None = None,
) -> list[IncidentReadinessResult]:
    if incidents is None:
        incidents = load_seed_incidents()
    results: list[IncidentReadinessResult] = []
    for incident in incidents:
        blockers = readiness_blockers(incident)
        status = (
            IncidentReadinessStatus.MODEL_READY
            if not blockers
            else IncidentReadinessStatus.BLOCKED
        )
        results.append(
            IncidentReadinessResult(
                incident_id=incident.incident_id,
                location_name=incident.location_name,
                status=status,
                blockers=blockers,
                notes=incident.notes,
            )
        )
    return results
