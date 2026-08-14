from datetime import datetime, timedelta, timezone

from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.schemas.incident import IncidentConfidence, IncidentSourceType

BST = timezone(timedelta(hours=1))


def incident_by_id():
    return {incident.incident_id: incident for incident in load_seed_incidents()}


def test_initial_seed_dataset_contains_plan_case_study_locations():
    incidents = load_seed_incidents()

    assert len(incidents) == 8
    assert {incident.location_name for incident in incidents} == {
        "Stourbridge",
        "Pershore",
        "New Forest",
        "Cannock Chase",
        "Tamworth",
        "Stoke-on-Trent",
        "Rhandirmwyn / Llandovery",
        "Porth",
    }


def test_seed_dataset_replaces_placeholder_sources_where_research_found_sources():
    incidents = load_seed_incidents()

    placeholder_records = [
        incident
        for incident in incidents
        if any(source.source_type is IncidentSourceType.PLACEHOLDER for source in incident.sources)
    ]

    assert {incident.location_name for incident in placeholder_records} == {"Tamworth"}
    verified_incidents = [
        incident for incident in incidents if incident.location_name != "Tamworth"
    ]
    assert all(
        incident.confidence is not IncidentConfidence.NEEDS_VERIFICATION
        for incident in verified_incidents
    )


def test_seed_dataset_keeps_exact_times_only_when_source_supported():
    incidents = incident_by_id()

    assert incidents["pershore-2026-08"].start_timestamp == datetime(
        2026, 8, 13, 16, 17, tzinfo=BST
    )
    assert incidents["cannock-chase-2026-08"].start_timestamp == datetime(
        2026, 7, 30, 18, 0, tzinfo=BST
    )
    assert incidents["stoke-on-trent-2026-08"].start_timestamp == datetime(
        2026, 8, 9, 16, 30, tzinfo=BST
    )
    assert incidents["rhandirmwyn-llandovery-2026-08"].start_timestamp == datetime(
        2026, 8, 12, 12, 45, tzinfo=BST
    )

    assert incidents["stourbridge-2026-08"].start_timestamp is None
    assert incidents["new-forest-2026-08"].start_timestamp is None
    assert incidents["porth-2026-08"].start_timestamp is None


def test_seed_dataset_includes_researched_coordinates_when_source_location_is_specific():
    incidents = incident_by_id()

    assert incidents["pershore-2026-08"].latitude == 52.1130376
    assert incidents["pershore-2026-08"].longitude == -2.0843023
    assert incidents["stoke-on-trent-2026-08"].latitude == 53.00131
    assert incidents["stoke-on-trent-2026-08"].longitude == -2.1069951
    assert incidents["rhandirmwyn-llandovery-2026-08"].latitude == 52.0776364
    assert incidents["rhandirmwyn-llandovery-2026-08"].longitude == -3.7751552
    assert incidents["porth-2026-08"].latitude == 51.6191027
    assert incidents["porth-2026-08"].longitude == -3.4149125
