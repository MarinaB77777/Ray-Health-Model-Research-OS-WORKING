import pytest

from pilot_session.errors import ExportBlockedError
from pilot_session.export import (
    generate_participant_export,
    generate_research_export,
    generate_session_export,
)
from pilot_session.schemas import (
    ParticipantSession,
    SessionStatus,
)

from research.aggregation_governance import (
    evaluate_snapshot_dataset_admission,
)


def test_generate_participant_export_uses_public_snapshot_only():
    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.raw_engine_result = {
        "internal": "do-not-export"
    }

    session.public_output = {
        "summary_text": "Public summary"
    }

    session.uncertainty_snapshot = {
        "level": "low"
    }

    session.next_question_snapshots = [
        {"code": "q1"}
    ]

    export = generate_participant_export(session)

    assert export["export_mode"] == "participant"
    assert (
        export["export_scope"]
        == "public_participant_safe"
    )

    assert export["export_valid"] is True

    assert (
        export["purpose"]
        == "participant_view"
    )

    assert (
        export["generated_by"]
        == "pilot_session.export"
    )

    assert export["engine_version"] == "mvp-1"

    assert export["session_id"] == "session-1"

    assert (
        export["participant_id"]
        == "participant-1"
    )

    assert export["public_output"] == {
        "summary_text": "Public summary"
    }

    assert export["uncertainty"] == {
        "level": "low"
    }

    assert export["next_questions"] == [
        {"code": "q1"}
    ]

    assert "raw_engine_result" not in export
    assert "internal" not in export


def test_participant_export_requires_allowed_status():
    session = ParticipantSession(
        session_id="session-2",
        participant_id="participant-2",
        status=SessionStatus.CREATED,
    )

    session.public_output = {
        "summary_text": "Not ready"
    }

    with pytest.raises(ExportBlockedError):
        generate_participant_export(session)


def test_participant_export_blocks_invalidated_session():
    session = ParticipantSession(
        session_id="session-3",
        participant_id="participant-3",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.invalidated = True

    session.public_output = {
        "summary_text": "Invalidated"
    }

    with pytest.raises(ExportBlockedError):
        generate_participant_export(session)


def test_participant_export_requires_public_output():
    session = ParticipantSession(
        session_id="session-4",
        participant_id="participant-4",
        status=SessionStatus.RUN_COMPLETED,
    )

    with pytest.raises(ExportBlockedError):
        generate_participant_export(session)


def test_generate_session_export_aliases_participant_export():
    session = ParticipantSession(
        session_id="session-5",
        participant_id="participant-5",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.public_output = {
        "summary_text": "Alias export"
    }

    export = generate_session_export(session)

    assert export["export_mode"] == "participant"


def test_generate_research_export_returns_bounded_snapshot():
    session = ParticipantSession(
        session_id="session-6",
        participant_id="participant-6",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.public_output = {
        "summary_text": "Research export",
        "result_level": "low",
    }

    export = generate_research_export(session)

    assert export["export_mode"] == "research"
    assert export["export_scope"] == "bounded_research_snapshot"
    assert export["purpose"] == "research_snapshot_export"
    assert "research_snapshot" in export
    assert "raw_engine_result" not in export


def test_research_export_generation_is_not_dataset_admission():
    session = ParticipantSession(
        session_id="session-7",
        participant_id="participant-7",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.public_output = {
        "summary_text": "Research export",
        "result_level": "low",
    }

    export = generate_research_export(session)
    snapshot = export["research_snapshot"]
    policy = snapshot["snapshot_policy_status"]

    assert export["export_valid"] is True
    assert policy["consent_status"] == "not_evaluated"
    assert policy["retention_status"] == "not_evaluated"
    assert policy["policy_restricted"] == "not_evaluated"
    assert policy["usable_for_research_preliminary"] is True

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "CONSENT_NOT_GRANTED" in verdict["blockers"]
    assert "RETENTION_NOT_EVALUATED" in verdict["blockers"]
    assert (
        "POLICY_RESTRICTED_OR_NOT_EVALUATED"
        in verdict["blockers"]
    )