from research.consent_policy import (
    CONSENT_POLICY_VERSION,
    get_default_consent_record,
)
from research.consent_validator import (
    CONSENT_VALIDATOR_VERSION,
    validate_consent_record,
)


def make_valid_granted_record():
    record = get_default_consent_record()
    record["consent_status"] = "granted"
    record["consent_version"] = CONSENT_POLICY_VERSION
    record["consent_scope"] = ["research_snapshot_export"]
    record["granted_at"] = "2026-01-01T00:00:00Z"
    record["revoked_at"] = None
    record["expiration_at"] = None
    record["consent_basis"] = "explicit"
    record["notes"] = None
    return record


def test_valid_granted_record_passes():
    result = validate_consent_record(
        make_valid_granted_record()
    )

    assert result["valid"] is True
    assert result["reason_codes"] == []
    assert (
        result["validator_version"]
        == CONSENT_VALIDATOR_VERSION
    )


def test_non_dict_record_is_invalid():
    result = validate_consent_record("not-a-record")

    assert result["valid"] is False
    assert result["reason_codes"] == [
        "CONSENT_RECORD_NOT_DICT"
    ]


def test_missing_required_key_is_invalid():
    record = make_valid_granted_record()
    del record["consent_status"]

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "CONSENT_RECORD_MISSING_KEY:consent_status"
        in result["reason_codes"]
    )
    assert "CONSENT_STATUS_MISSING" in result["reason_codes"]


def test_invalid_status_is_invalid():
    record = make_valid_granted_record()
    record["consent_status"] = "secret_status"

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_STATUS_INVALID" in result["reason_codes"]


def test_wrong_consent_version_is_invalid():
    record = make_valid_granted_record()
    record["consent_version"] = "old-version"

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_VERSION_MISMATCH" in result["reason_codes"]


def test_invalid_scope_type_is_invalid():
    record = make_valid_granted_record()
    record["consent_scope"] = {
        "scope": "research_snapshot_export"
    }

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_SCOPE_INVALID_TYPE" in result["reason_codes"]


def test_invalid_scope_item_is_invalid():
    record = make_valid_granted_record()
    record["consent_scope"] = [
        "research_snapshot_export",
        123,
    ]

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_SCOPE_ITEM_INVALID" in result["reason_codes"]


def test_not_allowed_scope_item_is_invalid():
    record = make_valid_granted_record()
    record["consent_scope"] = [
        "global_permission",
    ]

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_SCOPE_NOT_ALLOWED" in result["reason_codes"]


def test_duplicate_scope_item_is_invalid():
    record = make_valid_granted_record()
    record["consent_scope"] = [
        "research_snapshot_export",
        "research_snapshot_export",
    ]

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_SCOPE_DUPLICATE" in result["reason_codes"]


def test_granted_without_granted_at_is_invalid():
    record = make_valid_granted_record()
    record["granted_at"] = None

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "GRANTED_CONSENT_MISSING_GRANTED_AT"
        in result["reason_codes"]
    )


def test_granted_with_revoked_at_is_invalid():
    record = make_valid_granted_record()
    record["revoked_at"] = "2026-01-02T00:00:00Z"

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "GRANTED_CONSENT_HAS_REVOKED_AT"
        in result["reason_codes"]
    )


def test_granted_with_past_expiration_is_invalid():
    record = make_valid_granted_record()
    record["expiration_at"] = "2000-01-01T00:00:00Z"

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "GRANTED_CONSENT_EXPIRED_BY_DATE"
        in result["reason_codes"]
    )


def test_revoked_without_revoked_at_is_invalid():
    record = make_valid_granted_record()
    record["consent_status"] = "revoked"
    record["revoked_at"] = None

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "REVOKED_CONSENT_MISSING_REVOKED_AT"
        in result["reason_codes"]
    )


def test_expired_without_expiration_at_is_invalid():
    record = make_valid_granted_record()
    record["consent_status"] = "expired"
    record["expiration_at"] = None

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "EXPIRED_CONSENT_MISSING_EXPIRATION_AT"
        in result["reason_codes"]
    )


def test_bad_datetime_string_is_invalid():
    record = make_valid_granted_record()
    record["granted_at"] = "not-a-date"

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "CONSENT_DATETIME_FIELD_INVALID:granted_at"
        in result["reason_codes"]
    )


def test_granted_with_not_evaluated_basis_is_invalid():
    record = make_valid_granted_record()
    record["consent_basis"] = "not_evaluated"

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "GRANTED_CONSENT_BASIS_NOT_EVALUATED"
        in result["reason_codes"]
    )


def test_notes_are_ignored_and_not_leaked():
    record = make_valid_granted_record()
    record["notes"] = "sensitive note"

    result = validate_consent_record(record)

    assert result["valid"] is True
    assert "notes" not in result
    assert "sensitive note" not in str(result)


def test_validator_does_not_return_consent_eligible():
    result = validate_consent_record(
        make_valid_granted_record()
    )

    assert "consent_eligible" not in result


def test_validator_boundary_flags_are_present():
    result = validate_consent_record(
        make_valid_granted_record()
    )

    assert result["validator_is_not_consent_authority"] is True
    assert result["validator_does_not_grant_consent"] is True
    assert result["validator_does_not_authorize_export"] is True
    assert (
        result["validator_does_not_evaluate_scope_eligibility"]
        is True
    )

def test_granted_without_scope_is_invalid():
    record = make_valid_granted_record()
    record["consent_scope"] = []

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "GRANTED_CONSENT_MISSING_SCOPE"
        in result["reason_codes"]
    )


def test_granted_with_none_scope_is_invalid():
    record = make_valid_granted_record()
    record["consent_scope"] = None

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert (
        "GRANTED_CONSENT_MISSING_SCOPE"
        in result["reason_codes"]
    )


def test_consent_basis_none_is_invalid():
    record = make_valid_granted_record()
    record["consent_basis"] = None

    result = validate_consent_record(record)

    assert result["valid"] is False
    assert "CONSENT_BASIS_INVALID" in result["reason_codes"]


def test_validator_declares_static_and_non_storage_boundaries():
    result = validate_consent_record(
        make_valid_granted_record()
    )

    assert result["validator_is_static_structural_validator"] is True
    assert result["validator_does_not_store_consent"] is True
    assert result["validator_does_not_modify_record"] is True


def test_consent_validator_declares_session_collection_boundaries():
    result = validate_consent_record(make_valid_granted_record())

    assert result["valid"] is True
    assert result["validator_does_not_authorize_session_creation"] is True
    assert result["validator_does_not_authorize_collection"] is True
    assert result["session_collection_requires_session_level_agreement"] is True
    assert (
        result["declined_session_agreement_blocks_new_collection"]
        is True
    )
