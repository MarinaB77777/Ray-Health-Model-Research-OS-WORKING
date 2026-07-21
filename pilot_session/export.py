from datetime import UTC, datetime
from uuid import uuid4

from pilot_session.errors import ExportBlockedError
from pilot_session.schemas import ParticipantSession, SessionStatus
from research.snapshot_builder import build_research_snapshot


ALLOWED_PARTICIPANT_EXPORT_STATUSES = {
    SessionStatus.RUN_COMPLETED,
    SessionStatus.EXPORT_READY,
    SessionStatus.CLOSED,
}

ALLOWED_RESEARCH_EXPORT_STATUSES = {
    SessionStatus.RUN_COMPLETED,
    SessionStatus.EXPORT_READY,
    SessionStatus.CLOSED,
}


def _ensure_participant_export_allowed(
    session: ParticipantSession,
) -> None:
    if session.invalidated or session.status == SessionStatus.INVALIDATED:
        raise ExportBlockedError(
            "Participant export is blocked for invalidated session"
        )

    if session.status not in ALLOWED_PARTICIPANT_EXPORT_STATUSES:
        raise ExportBlockedError(
            "Participant export is not allowed for this session status"
        )

    if not session.public_output:
        raise ExportBlockedError(
            "Participant export is blocked because public_output is missing"
        )


def _ensure_research_export_allowed(
    session: ParticipantSession,
) -> None:
    if session.invalidated or session.status == SessionStatus.INVALIDATED:
        raise ExportBlockedError(
            "Research export is blocked for invalidated session"
        )

    if session.status not in ALLOWED_RESEARCH_EXPORT_STATUSES:
        raise ExportBlockedError(
            "Research export is not allowed for this session status"
        )

    if not session.public_output:
        raise ExportBlockedError(
            "Research export is blocked because public_output is missing"
        )


def generate_participant_export(session: ParticipantSession) -> dict:
    _ensure_participant_export_allowed(session)

    return {
        "export_id": str(uuid4()),
        "export_mode": "participant",
        "export_scope": "public_participant_safe",
        # Valid only for this generated participant export snapshot.
        "export_valid": True,
        "export_schema_version": session.export_schema_version,
        "export_policy_version": session.export_policy_version,
        "engine_version": session.engine_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "pilot_session.export",
        "purpose": "participant_view",
        "session_id": session.session_id,
        # TODO: migrate to participant_code/public pseudonymous id if needed.
        "participant_id": session.participant_id,
        "status": session.status.value,
        "participant_id": session.participant_id,
        "participant_id_boundary": (
            "mvp_pilot_reference_not_public_identity_not_longitudinal_identity"
        ),

        "status": session.status.value,

        "answer_collection": {
            "answers_count": len(session.answers),
            "answer_revision_count": session.answer_revision_count,
            "answer_merge_history": session.answer_merge_history,
            "run_count": session.run_count,
            "run_history": session.run_history,
        },

        "public_output": session.public_output,
        "uncertainty": session.uncertainty_snapshot or {},
        "next_questions": session.next_question_snapshots or [],
    }


def generate_research_export(session: ParticipantSession) -> dict:
    _ensure_research_export_allowed(session)

    return {
        "export_id": str(uuid4()),
        "export_mode": "research",
        "export_scope": "bounded_research_snapshot",
        # Valid only for this generated research export artifact.
        "export_valid": True,
        "export_schema_version": session.export_schema_version,
        "export_policy_version": session.export_policy_version,
        "engine_version": session.engine_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "pilot_session.export",
        "purpose": "research_snapshot_export",
        "session_id": session.session_id,
        "status": session.status.value,
        "research_snapshot": build_research_snapshot(session),
    }


# Temporary backward-compatible alias.
# TODO: remove after all callers use generate_participant_export explicitly.
generate_session_export = generate_participant_export
# Participant-facing export uses the pilot participant_id only as an MVP reference.
# It must not be treated as public identity or cross-session identity.