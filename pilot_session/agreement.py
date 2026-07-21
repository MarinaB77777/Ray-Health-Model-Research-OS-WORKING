from datetime import UTC, datetime
from uuid import uuid4

from research.consent_policy import evaluate_consent_for_scope


SESSION_AGREEMENT_VERSION = "session-agreement-1"
SESSION_AGREEMENT_REQUIRED_SCOPE = "pilot_participation"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_session_agreement_record(
    participant_id: str,
    consent_record: dict,
    agreement_text_version: str = SESSION_AGREEMENT_VERSION,
) -> dict:
    consent_result = evaluate_consent_for_scope(
        consent_record=consent_record,
        required_scope=SESSION_AGREEMENT_REQUIRED_SCOPE,
    )

    agreement_accepted = (
        consent_result.get("consent_eligible") is True
    )

    return {
        "agreement_id": str(uuid4()),
        "agreement_version": SESSION_AGREEMENT_VERSION,
        "agreement_text_version": agreement_text_version,
        "agreement_status": (
            "accepted" if agreement_accepted else "blocked"
        ),
        "participant_id": participant_id,
        "required_scope": SESSION_AGREEMENT_REQUIRED_SCOPE,
        "signed_at": utc_now_iso() if agreement_accepted else None,
        "consent_evaluation": consent_result,
        "collection_allowed": agreement_accepted,
        "agreement_is_session_level": True,
        "agreement_is_not_global_consent": True,
        "agreement_is_not_export_approval": True,
        "agreement_is_not_dataset_admission": True,
    }