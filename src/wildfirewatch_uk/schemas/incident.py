from datetime import datetime
from enum import StrEnum

from pydantic import AnyUrl, BaseModel, Field, field_validator, model_validator


class IncidentConfidence(StrEnum):
    """Confidence level for canonical incident facts."""

    NEEDS_VERIFICATION = "needs_verification"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IncidentSourceType(StrEnum):
    """Supported provenance categories for incident records."""

    OFFICIAL_REPORT = "official_report"
    FIRE_SERVICE = "fire_service"
    COUNCIL_ALERT = "council_alert"
    POLICE_STATEMENT = "police_statement"
    NEWS_REPORT = "news_report"
    SOCIAL_POST = "social_post"
    GEOCODER = "geocoder"
    PLACEHOLDER = "placeholder"


class IncidentSource(BaseModel):
    """A source supporting one or more incident claims."""

    url: AnyUrl
    source_type: IncidentSourceType
    title: str | None = None


class IncidentRecord(BaseModel):
    """Canonical wildfire incident record used by the retrospective PoC."""

    incident_id: str = Field(min_length=3, pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
    incident_name: str = Field(min_length=3)
    start_timestamp: datetime | None = None
    end_timestamp: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    location_name: str = Field(min_length=2)
    fire_service: str | None = None
    incident_type: str = Field(default="wildfire", min_length=2)
    area_burned_ha: float | None = Field(default=None, ge=0)
    buildings_threatened: int | None = Field(default=None, ge=0)
    buildings_damaged: int | None = Field(default=None, ge=0)
    evacuations: int | None = Field(default=None, ge=0)
    injuries: int | None = Field(default=None, ge=0)
    suspected_cause: str | None = None
    sources: list[IncidentSource]
    confidence: IncidentConfidence = IncidentConfidence.NEEDS_VERIFICATION
    notes: str | None = None

    @field_validator("sources")
    @classmethod
    def require_source_provenance(cls, sources: list[IncidentSource]) -> list[IncidentSource]:
        if not sources:
            raise ValueError("incident records must include at least one source")
        return sources

    @model_validator(mode="after")
    def validate_time_window(self) -> "IncidentRecord":
        has_invalid_window = (
            self.start_timestamp
            and self.end_timestamp
            and self.end_timestamp < self.start_timestamp
        )
        if has_invalid_window:
            raise ValueError("end_timestamp must be greater than or equal to start_timestamp")
        return self
