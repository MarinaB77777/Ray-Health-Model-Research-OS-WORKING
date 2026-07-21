from measurement_graph.time_contract import (
    normalize_measurement_time_reference,
    validate_measurement_time_reference,
)


def test_measurement_is_bound_to_registered_global_datetime_scale():
    normalized = normalize_measurement_time_reference({
        "observation_time": "2026-07-15T12:00:00-06:00",
        "clock_source": "application_server_timestamp",
        "synchronization_reference": "system_clock",
    })
    assert normalized["observation_time"] == "2026-07-15T18:00:00+00:00"
    assert normalized["global_time_reference"] == "UTC"
    assert normalized["global_time_scale"]["scale_type"] == "datetime"
    assert normalized["global_time_scale"]["scale_reference"]["scale_code"] == "datetime"
    assert normalized["time_scale"]["binding_status"] == "unbound"
    assert validate_measurement_time_reference(normalized)["valid"] is True


def test_naive_or_missing_time_is_not_silently_assumed():
    normalized = normalize_measurement_time_reference({
        "observation_time": "2026-07-15T12:00:00",
    })
    validation = validate_measurement_time_reference(normalized)
    assert validation["valid"] is False
    assert any(
        item["code"] == "OBSERVATION_TIME_REQUIRED"
        for item in validation["errors"]
    )


def test_finished_at_fallback_is_recorded_explicitly():
    normalized = normalize_measurement_time_reference({
        "finished_at": "2026-07-15T18:00:00Z",
    })
    assert normalized["observation_time_source"] == "finished_at_fallback"
    assert validate_measurement_time_reference(normalized)["valid"] is True


def test_legacy_session_timestamp_is_preserved_as_global_time_anchor():
    normalized = normalize_measurement_time_reference({
        "finished_at": "2026-07-15T18:00:00Z",
        "global_time_reference": "2026-07-15T17:55:00Z",
    })
    assert normalized["global_time_reference"] == "UTC"
    assert normalized["global_time_anchor"] == "2026-07-15T17:55:00+00:00"
    assert normalized["global_time_reference_source"] == (
        "legacy_timestamp_migrated_to_global_time_anchor"
    )
    assert validate_measurement_time_reference(normalized)["valid"] is True


def test_unrecognized_global_time_reference_is_not_hidden():
    normalized = normalize_measurement_time_reference({
        "finished_at": "2026-07-15T18:00:00Z",
        "global_time_reference": "unknown-clock-domain",
    })
    validation = validate_measurement_time_reference(normalized)
    assert validation["valid"] is False
    assert any(
        item["code"] == "GLOBAL_TIME_REFERENCE_UNRECOGNIZED"
        for item in validation["errors"]
    )
