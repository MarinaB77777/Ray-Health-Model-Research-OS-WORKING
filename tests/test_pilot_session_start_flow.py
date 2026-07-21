from pilot_account.service import PilotAccountService
from pilot_account.session_start_flow import PilotSessionStartFlow
from pilot_account.store import PilotAccountStore

from pilot_session.service import PilotSessionService
from pilot_session.store import PilotSessionStore

from research.consent_policy import (
    CONSENT_POLICY_VERSION,
    get_default_consent_record,
)


def make_granted_pilot_consent():
    record = get_default_consent_record()
    record["consent_status"] = "granted"
    record["consent_version"] = CONSENT_POLICY_VERSION
    record["consent_scope"] = ["pilot_participation"]
    record["granted_at"] = "2026-01-01T00:00:00Z"
    record["consent_basis"] = "explicit"
    return record


def test_start_session_after_agreement_creates_linked_session():
    account_service = PilotAccountService(PilotAccountStore())
    session_service = PilotSessionService(PilotSessionStore())

    account = account_service.create_account(
        preferred_language="ru"
    )

    flow = PilotSessionStartFlow(
        account_service=account_service,
        session_service=session_service,
    )

    result = flow.start_session_after_agreement(
        account_id=account.account_id,
        consent_record=make_granted_pilot_consent(),
        study_id="pilot-study-1",
    )

    assert result is not None
    assert result["agreement"]["collection_allowed"] is True

    session = result["session"]

    assert session.participant_id == account.participant_id
    assert session.subject_link_id == account.subject_link_id
    assert session.study_id == "pilot-study-1"
    assert session.participant_role == "participant"
    assert session.agreement_id == result["agreement"]["agreement_id"]
    assert session.collection_agreement_status == "accepted"


def test_start_session_missing_account_returns_none():
    account_service = PilotAccountService(PilotAccountStore())
    session_service = PilotSessionService(PilotSessionStore())

    flow = PilotSessionStartFlow(
        account_service=account_service,
        session_service=session_service,
    )

    result = flow.start_session_after_agreement(
        account_id="missing-account",
        consent_record=make_granted_pilot_consent(),
    )

    assert result is None