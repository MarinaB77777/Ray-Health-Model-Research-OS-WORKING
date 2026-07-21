from research.consent_policy import (
    CONSENT_POLICY_VERSION,
    get_default_consent_record,
)
from pilot_session.agreement import (
    SESSION_AGREEMENT_VERSION,
    build_session_agreement_record,
)


def make_granted_pilot_participation_consent():
    record = get_default_consent_record()
    record["consent_status"] = "granted"
    record["consent_version"] = CONSENT_POLICY_VERSION
    record["consent_scope"] = ["pilot_participation"]
    record["granted_at"] = "2026-01-01T00:00:00Z"
    record["consent_basis"] = "explicit"
    return record


def test_session_agreement_accepted_when_pilot_participation_consent_granted():
    agreement = build_session_agreement_record(
        participant_id="participant-1",
        consent_record=make_granted_pilot_participation_consent(),
    )

    assert agreement["agreement_version"] == SESSION_AGREEMENT_VERSION
    assert agreement["agreement_status"] == "accepted"
    assert agreement["collection_allowed"] is True
    assert agreement["signed_at"] is not None
    assert agreement["required_scope"] == "pilot_participation"


def test_session_agreement_blocked_without_required_consent_scope():
    consent = make_granted_pilot_participation_consent()
    consent["consent_scope"] = ["research_snapshot_export"]

    agreement = build_session_agreement_record(
        participant_id="participant-1",
        consent_record=consent,
    )

    assert agreement["agreement_status"] == "blocked"
    assert agreement["collection_allowed"] is False
    assert agreement["signed_at"] is None
    assert (
        agreement["consent_evaluation"]["reason_code"]
        == "CONSENT_SCOPE_NOT_GRANTED"
    )


def test_session_agreement_declares_boundaries():
    agreement = build_session_agreement_record(
        participant_id="participant-1",
        consent_record=make_granted_pilot_participation_consent(),
    )

    assert agreement["agreement_is_session_level"] is True
    assert agreement["agreement_is_not_global_consent"] is True
    assert agreement["agreement_is_not_export_approval"] is True
    assert agreement["agreement_is_not_dataset_admission"] is True