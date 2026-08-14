import json
from functools import lru_cache
from importlib import resources

from wildfirewatch_uk.schemas.incident import IncidentRecord


@lru_cache
def load_seed_incidents() -> tuple[IncidentRecord, ...]:
    """Load the initial PLAN.md case-study incidents.

    These seed records intentionally use placeholder provenance until each
    incident's source URL, ignition time, and coordinates are verified.
    """

    seed_path = resources.files(__package__).joinpath("initial_incidents.json")
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    return tuple(IncidentRecord.model_validate(record) for record in payload)
