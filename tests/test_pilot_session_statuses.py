from pilot_session.schemas import ParticipantSession, SessionStatus
from pilot_session.statuses import (
    can_generate_export,
    is_invalidated,
    is_operationally_closed,
    is_research_usable,
)


def test_closed_session_is_operationally_closed():
    session = ParticipantSession(
        session_id="s1",
        participant_id="p1",
    )

    session.status = SessionStatus.CLOSED

    assert is_operationally_closed(session) is True


def test_invalidated_session_is_not_research_usable():
    session = ParticipantSession(
        session_id="s2",
        participant_id="p2",
    )

    session.status = SessionStatus.INVALIDATED

    assert is_invalidated(session) is True
    assert is_research_usable(session) is False


def test_invalidated_flag_blocks_research_usage():
    session = ParticipantSession(
        session_id="s3",
        participant_id="p3",
    )

    session.invalidated = True

    assert is_invalidated(session) is True
    assert is_research_usable(session) is False


def test_export_allowed_for_completed_valid_session():
    session = ParticipantSession(
        session_id="s4",
        participant_id="p4",
    )

    session.status = SessionStatus.RUN_COMPLETED
    
    session.public_output = {"summary_text": "ok"}

    assert can_generate_export(session) is True


def test_export_blocked_for_invalidated_session():
    session = ParticipantSession(
        session_id="s5",
        participant_id="p5",
    )

    session.status = SessionStatus.RUN_COMPLETED
    session.invalidated = True

    assert can_generate_export(session) is False


def test_export_blocked_before_run_completed():
    session = ParticipantSession(
        session_id="s6",
        participant_id="p6",
    )

    session.status = SessionStatus.ANSWERS_RECEIVED

    assert can_generate_export(session) is False
