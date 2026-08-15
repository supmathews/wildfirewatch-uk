from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.services.incident_readiness import (
    IncidentReadinessStatus,
    audit_incident_readiness,
)

DEFAULT_CACHE_PATH = Path("data/processed/osm_land_cover_cache.json")


class LandCoverCacheAuditRow(BaseModel):
    incident_id: str
    latitude: float
    longitude: float
    cache_key: str
    status: str
    land_cover_class: str | None


class LandCoverCacheAudit(BaseModel):
    point_count: int
    classified_count: int
    null_count: int
    missing_count: int
    coverage_ratio: float
    rows: list[LandCoverCacheAuditRow]


def _cache_key(latitude: float, longitude: float) -> str:
    return f"{latitude:.6f},{longitude:.6f}"


def _default_model_ready_points() -> list[tuple[str, float, float]]:
    readiness = {result.incident_id: result for result in audit_incident_readiness()}
    points: list[tuple[str, float, float]] = []
    for incident in load_seed_incidents():
        if readiness[incident.incident_id].status is not IncidentReadinessStatus.MODEL_READY:
            continue
        assert incident.latitude is not None
        assert incident.longitude is not None
        points.append((incident.incident_id, incident.latitude, incident.longitude))
    return points


def audit_land_cover_cache(
    *,
    cache_path: Path = DEFAULT_CACHE_PATH,
    points: list[tuple[str, float, float]] | None = None,
) -> LandCoverCacheAudit:
    if points is None:
        points = _default_model_ready_points()
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    rows: list[LandCoverCacheAuditRow] = []
    for incident_id, latitude, longitude in points:
        key = _cache_key(latitude, longitude)
        if key not in cache:
            status = "missing"
            land_cover_class = None
        elif cache[key] is None:
            status = "null"
            land_cover_class = None
        else:
            status = "classified"
            land_cover_class = cache[key]
        rows.append(
            LandCoverCacheAuditRow(
                incident_id=incident_id,
                latitude=latitude,
                longitude=longitude,
                cache_key=key,
                status=status,
                land_cover_class=land_cover_class,
            )
        )
    classified_count = sum(row.status == "classified" for row in rows)
    null_count = sum(row.status == "null" for row in rows)
    missing_count = sum(row.status == "missing" for row in rows)
    return LandCoverCacheAudit(
        point_count=len(rows),
        classified_count=classified_count,
        null_count=null_count,
        missing_count=missing_count,
        coverage_ratio=0.0 if not rows else classified_count / len(rows),
        rows=rows,
    )
