from wildfirewatch_uk.providers.incidents.seed_loader import load_seed_incidents
from wildfirewatch_uk.schemas.incident import IncidentConfidence


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


def test_initial_seed_dataset_is_explicitly_unverified_until_sources_are_added():
    incidents = load_seed_incidents()

    assert all(
        incident.confidence is IncidentConfidence.NEEDS_VERIFICATION for incident in incidents
    )
    assert all(incident.sources for incident in incidents)
    assert all("placeholder" in str(incident.sources[0].url) for incident in incidents)
