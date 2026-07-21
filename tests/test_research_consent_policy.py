import pytest

from research.consent_policy import (
    ALLOWED_CONSENT_SCOPES,
    ALLOWED_CONSENT_STATUSES,
    CONSENT_POLICY_VERSION,
    evaluate_consent_for_scope,
    get_default_consent_record,
)


def make_granted_record(scope="research_snapshot_export"):
    record = get_default_consent_record()
    record["consent_status"] = "granted"
    record["consent_scope"] = [scope]
    record["granted_at"] = "2026-01-01T00:00:00Z"
    record["consent_basis"] = "explicit"
    return record


def test_allowed_consent_statuses_are_explicit():
    assert ALLOWED_CONSENT_STATUSES == {
        "not_evaluated",
        "pending",
        "granted",
        "denied",
        "revoked",
        "expired",
    }


def test_allowed_consent_scopes_are_explicit():
    assert ALLOWED_CONSENT_SCOPES == {
        "pilot_participation",
        "research_snapshot_export",
        "dataset_inclusion",
        "future_contact",
        "future_studies",
    }


def test_default_consent_record_is_not_evaluated():
    record = get_default_consent_record()

    assert record["consent_status"] == "not_evaluated"
    assert record["consent_version"] == CONSENT_POLICY_VERSION
    assert record["consent_scope"] == []
    assert record["consent_basis"] == "not_evaluated"


def test_default_consent_record_is_deepcopy_safe():
    record = get_default_consent_record()
    record["consent_scope"].append("bad_scope")

    fresh_record = get_default_consent_record()

    assert fresh_record["consent_scope"] == []


def test_missing_consent_record_blocks_scope():
    result = evaluate_consent_for_scope(
        None,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_status"] is None
    assert result["consent_evaluation_status"] == "missing_record"
    assert result["reason_code"] == "CONSENT_RECORD_MISSING"


def test_not_evaluated_consent_blocks_scope():
    result = evaluate_consent_for_scope(
        get_default_consent_record(),
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "blocked"
    assert result["reason_code"] == "CONSENT_NOT_EVALUATED"


@pytest.mark.parametrize(
    ("status", "reason_code"),
    [
        ("pending", "CONSENT_PENDING"),
        ("denied", "CONSENT_DENIED"),
        ("revoked", "CONSENT_REVOKED"),
        ("expired", "CONSENT_EXPIRED"),
    ],
)
def test_non_granted_consent_statuses_block_scope(
    status,
    reason_code,
):
    record = get_default_consent_record()
    record["consent_status"] = status

    if status == "revoked":
        record["revoked_at"] = "2026-01-01T00:00:00Z"

    if status == "expired":
        record["expiration_at"] = "2026-01-01T00:00:00Z"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["reason_code"] == reason_code


def test_granted_consent_with_required_scope_is_eligible():
    record = make_granted_record()

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is True
    assert result["reason_code"] == "CONSENT_GRANTED_FOR_SCOPE"
    assert result["granted_scopes"] == ["research_snapshot_export"]


def test_granted_consent_without_required_scope_blocks():
    record = make_granted_record("pilot_participation")

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["reason_code"] == "CONSENT_SCOPE_NOT_GRANTED"
    assert result["granted_scopes"] == ["pilot_participation"]


def test_string_scope_is_supported_for_mvp():
    record = make_granted_record()
    record["consent_scope"] = "research_snapshot_export"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is True
    assert result["reason_code"] == "CONSENT_GRANTED_FOR_SCOPE"


def test_missing_consent_status_is_invalid_record():
    record = get_default_consent_record()
    del record["consent_status"]

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert result["reason_code"] == "CONSENT_RECORD_INVALID"
    assert "CONSENT_STATUS_MISSING" in result["reason_codes"]


def test_invalid_consent_status_is_invalid_record():
    record = get_default_consent_record()
    record["consent_status"] = "secret_status"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert "CONSENT_STATUS_INVALID" in result["reason_codes"]


def test_wrong_consent_version_is_invalid_record():
    record = make_granted_record()
    record["consent_version"] = "old-version"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert "CONSENT_VERSION_MISMATCH" in result["reason_codes"]


def test_granted_consent_requires_granted_at():
    record = make_granted_record()
    record["granted_at"] = None

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "GRANTED_CONSENT_MISSING_GRANTED_AT" in result["reason_codes"]


def test_granted_consent_with_revoked_at_is_invalid():
    record = make_granted_record()
    record["revoked_at"] = "2026-01-02T00:00:00Z"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "GRANTED_CONSENT_HAS_REVOKED_AT" in result["reason_codes"]


def test_revoked_consent_requires_revoked_at():
    record = get_default_consent_record()
    record["consent_status"] = "revoked"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "REVOKED_CONSENT_MISSING_REVOKED_AT" in result["reason_codes"]


def test_invalid_scope_type_is_invalid_record():
    record = make_granted_record()
    record["consent_scope"] = {"scope": "research_snapshot_export"}

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "CONSENT_SCOPE_INVALID_TYPE" in result["reason_codes"]


def test_invalid_scope_item_is_invalid_record():
    record = make_granted_record()
    record["consent_scope"] = ["research_snapshot_export", 123]

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "CONSENT_SCOPE_ITEM_INVALID" in result["reason_codes"]


def test_not_allowed_scope_item_is_invalid_record():
    record = make_granted_record()
    record["consent_scope"] = [
        "research_snapshot_export",
        "global_permission",
    ]

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "CONSENT_SCOPE_NOT_ALLOWED" in result["reason_codes"]


def test_duplicate_scope_item_is_invalid_record():
    record = make_granted_record()
    record["consent_scope"] = [
        "research_snapshot_export",
        "research_snapshot_export",
    ]

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "CONSENT_SCOPE_DUPLICATE" in result["reason_codes"]


def test_invalid_consent_basis_is_invalid_record():
    record = make_granted_record()
    record["consent_basis"] = ""

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert "CONSENT_BASIS_INVALID" in result["reason_codes"]


def test_invalid_required_scope_raises():
    with pytest.raises(ValueError):
        evaluate_consent_for_scope(
            get_default_consent_record(),
            "global_permission",
        )


def test_empty_required_scope_raises():
    with pytest.raises(ValueError):
        evaluate_consent_for_scope(
            get_default_consent_record(),
            " ",
        )


def test_non_string_required_scope_raises():
    with pytest.raises(ValueError):
        evaluate_consent_for_scope(
            get_default_consent_record(),
            None,
        )


def test_non_dict_consent_record_raises():
    with pytest.raises(ValueError):
        evaluate_consent_for_scope(
            "not-a-record",
            "research_snapshot_export",
        )


def test_consent_policy_declares_non_authority_boundaries():
    result = evaluate_consent_for_scope(
        make_granted_record(),
        "research_snapshot_export",
    )

    assert result["consent_policy_version"] == CONSENT_POLICY_VERSION
    assert (
        result["consent_evaluation_method"]
        == "static_consent_policy"
    )
    assert (
        result["consent_decision_is_not_governance_verdict"]
        is True
    )
    assert (
        result["consent_status_is_not_runtime_permission"]
        is True
    )
    assert (
        result["consent_granted_is_not_export_approval"]
        is True
    )
    assert (
        result["consent_evaluation_is_not_research_approval"]
        is True
    )
    assert (
        result["consent_evaluation_is_not_dataset_admission"]
        is True
    )
    assert (
        result["consent_evaluation_is_not_retention_approval"]
        is True
    )
    assert result["silence_is_not_consent"] is True
    assert result["consent_scope_is_not_global_permission"] is True


def test_granted_consent_with_past_expiration_is_invalid():
    record = make_granted_record()
    record["expiration_at"] = "2000-01-01T00:00:00Z"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert (
        "GRANTED_CONSENT_EXPIRED_BY_DATE"
        in result["reason_codes"]
    )


def test_granted_consent_with_not_evaluated_basis_is_invalid():
    record = make_granted_record()
    record["consent_basis"] = "not_evaluated"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert (
        "GRANTED_CONSENT_BASIS_NOT_EVALUATED"
        in result["reason_codes"]
    )


def test_expired_consent_requires_expiration_at():
    record = get_default_consent_record()
    record["consent_status"] = "expired"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert (
        "EXPIRED_CONSENT_MISSING_EXPIRATION_AT"
        in result["reason_codes"]
    )


def test_bad_datetime_string_is_invalid_record():
    record = make_granted_record()
    record["expiration_at"] = "not-a-date"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert result["consent_eligible"] is False
    assert result["consent_evaluation_status"] == "invalid_record"
    assert (
        "CONSENT_DATETIME_FIELD_INVALID:expiration_at"
        in result["reason_codes"]
    )


def test_notes_are_not_exported_in_consent_evaluation_result():
    record = make_granted_record()
    record["notes"] = "sensitive internal note"

    result = evaluate_consent_for_scope(
        record,
        "research_snapshot_export",
    )

    assert "notes" not in result
    assert "sensitive internal note" not in str(result)


def test_consent_policy_declares_record_and_scope_boundaries():
    result = evaluate_consent_for_scope(
        make_granted_record(),
        "research_snapshot_export",
    )

    assert result["consent_record_is_not_identity"] is True
    assert result["consent_version_checked"] is True
    assert result["consent_scope_checked"] is True


def test_consent_policy_declares_session_collection_boundary():
    result = evaluate_consent_for_scope(
        get_default_consent_record(),
        "pilot_participation",
    )

    assert (
        result[
            "consent_evaluation_is_not_session_collection_permission"
        ]
        is True
    )
    assert (
        result[
            "session_collection_requires_session_level_agreement"
        ]
        is True
    )
    assert (
        result[
            "declined_session_agreement_blocks_new_collection"
        ]
        is True
    )
