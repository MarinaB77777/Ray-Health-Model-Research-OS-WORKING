from copy import deepcopy

from research.retention_validator import (
    RETENTION_POLICY_VERSION,
    RETENTION_VALIDATOR_VERSION,
    validate_retention_record,
)


def make_valid_active_record():
    return {
        "retention_status": "active",
        "retention_version": RETENTION_POLICY_VERSION,
        "retention_class": "bounded_research",
        "retention_basis": "pilot_research",
        "retention_reviewed_at": "2026-01-01T00:00:00Z",
        "expiration_at": None,
        "deletion_requested_at": None,
        "deleted_at": None,
        "notes": None,
    }


def test_validate_active_retention_record_is_valid():
    record = make_valid_active_record()

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert result["reason_codes"] == []
    assert (
        result["validator_version"]
        == RETENTION_VALIDATOR_VERSION
    )


def test_validate_retention_record_rejects_non_dict():
    result = validate_retention_record("not-a-record")

    assert result["valid"] is False
    assert result["reason_codes"] == ["RETENTION_RECORD_NOT_DICT"]


def test_validate_retention_record_requires_required_keys():
    record = make_valid_active_record()
    del record["retention_status"]

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "MISSING_REQUIRED_KEY:retention_status"
        in result["reason_codes"]
    )


def test_validate_retention_record_rejects_invalid_status():
    record = make_valid_active_record()
    record["retention_status"] = "secret_status"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert "INVALID_RETENTION_STATUS" in result["reason_codes"]


def test_validate_retention_record_rejects_invalid_class():
    record = make_valid_active_record()
    record["retention_class"] = "global_archive"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert "INVALID_RETENTION_CLASS" in result["reason_codes"]


def test_validate_retention_record_rejects_version_mismatch():
    record = make_valid_active_record()
    record["retention_version"] = "old-version"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert "RETENTION_VERSION_MISMATCH" in result["reason_codes"]


def test_validate_retention_record_rejects_empty_string_field():
    record = make_valid_active_record()
    record["retention_basis"] = " "

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "STRING_FIELD_INVALID:retention_basis"
        in result["reason_codes"]
    )


def test_validate_retention_record_rejects_invalid_datetime():
    record = make_valid_active_record()
    record["retention_reviewed_at"] = "not-a-date"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "DATETIME_FIELD_INVALID:retention_reviewed_at"
        in result["reason_codes"]
    )


def test_validate_expired_retention_requires_expiration_at():
    record = make_valid_active_record()
    record["retention_status"] = "expired"
    record["expiration_at"] = None

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "EXPIRED_RETENTION_MISSING_EXPIRATION_AT"
        in result["reason_codes"]
    )


def test_validate_expired_retention_with_expiration_at_is_valid():
    record = make_valid_active_record()
    record["retention_status"] = "expired"
    record["expiration_at"] = "2026-01-01T00:00:00Z"

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert result["reason_codes"] == []


def test_validate_deletion_requested_requires_deletion_requested_at():
    record = make_valid_active_record()
    record["retention_status"] = "deletion_requested"
    record["deletion_requested_at"] = None

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "DELETION_REQUESTED_MISSING_DELETION_REQUESTED_AT"
        in result["reason_codes"]
    )


def test_validate_deletion_requested_with_timestamp_is_valid():
    record = make_valid_active_record()
    record["retention_status"] = "deletion_requested"
    record["deletion_requested_at"] = "2026-01-01T00:00:00Z"

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert result["reason_codes"] == []


def test_validate_deleted_retention_requires_deleted_at():
    record = make_valid_active_record()
    record["retention_status"] = "deleted"
    record["deleted_at"] = None

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "DELETED_RETENTION_MISSING_DELETED_AT"
        in result["reason_codes"]
    )


def test_validate_deleted_retention_with_deleted_at_is_valid():
    record = make_valid_active_record()
    record["retention_status"] = "deleted"
    record["deleted_at"] = "2026-01-01T00:00:00Z"

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert result["reason_codes"] == []


def test_validate_active_retention_requires_defined_class():
    record = make_valid_active_record()
    record["retention_class"] = "not_defined"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "ACTIVE_RETENTION_REQUIRES_DEFINED_CLASS"
        in result["reason_codes"]
    )


def test_validate_active_retention_rejects_deletion_requested_at():
    record = make_valid_active_record()
    record["deletion_requested_at"] = "2026-01-01T00:00:00Z"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "ACTIVE_RETENTION_HAS_DELETION_REQUESTED_AT"
        in result["reason_codes"]
    )


def test_validate_active_retention_rejects_deleted_at():
    record = make_valid_active_record()
    record["deleted_at"] = "2026-01-01T00:00:00Z"

    result = validate_retention_record(record)

    assert result["valid"] is False
    assert (
        "ACTIVE_RETENTION_HAS_DELETED_AT"
        in result["reason_codes"]
    )


def test_validate_not_evaluated_record_is_valid_structurally():
    record = make_valid_active_record()
    record["retention_status"] = "not_evaluated"
    record["retention_class"] = "not_defined"
    record["retention_basis"] = "not_evaluated"

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert result["reason_codes"] == []


def test_validate_policy_restricted_record_is_valid_structurally():
    record = make_valid_active_record()
    record["retention_status"] = "policy_restricted"

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert result["reason_codes"] == []


def test_notes_are_ignored_and_not_leaked():
    record = make_valid_active_record()
    record["notes"] = "sensitive retention note"

    result = validate_retention_record(record)

    assert result["valid"] is True
    assert "notes" not in result
    assert "sensitive retention note" not in str(result)


def test_validator_does_not_return_authority_fields():
    result = validate_retention_record(make_valid_active_record())

    assert "retention_active" not in result
    assert "retention_eligible" not in result
    assert "export_allowed" not in result
    assert "dataset_allowed" not in result
    assert "retention_active" not in result
    assert "retention_eligible" not in result
    assert "retention_allowed" not in result
    assert "export_allowed" not in result
    assert "dataset_allowed" not in result


def test_validator_declares_non_authority_boundaries():
    result = validate_retention_record(make_valid_active_record())

    assert result["validator_is_static_structural_validator"] is True
    assert result["validator_is_not_retention_authority"] is True
    assert result["validator_does_not_repair_record"] is True
    assert result["validator_does_not_grant_retention"] is True
    assert result["validator_does_not_delete_data"] is True
    assert result["validator_does_not_authorize_export"] is True
    assert result["validator_does_not_authorize_reuse"] is True
    assert (
        result["validator_does_not_evaluate_dataset_admission"]
        is True
    )