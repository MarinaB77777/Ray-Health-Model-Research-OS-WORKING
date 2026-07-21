from pilot_session.schemas import ParticipantSession, SessionStatus


def test_participant_session_defaults_to_created():
    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
    )

    assert session.status == SessionStatus.CREATED
    assert session.answers == {}
    assert session.raw_engine_result == {}
    assert session.public_output == {}
    assert session.next_question_snapshots == []
    assert session.acquisition_request_snapshots == {}
    assert session.uncertainty_snapshot == {}
    assert session.export_generated is False
    assert session.invalidated is False


def test_session_status_values_are_explicit():
    assert SessionStatus.CREATED.value == "CREATED"
    assert SessionStatus.ANSWERS_RECEIVED.value == "ANSWERS_RECEIVED"
    assert SessionStatus.RUN_COMPLETED.value == "RUN_COMPLETED"
    assert SessionStatus.WAITING_FOR_INPUT.value == "WAITING_FOR_INPUT"
    assert SessionStatus.PARTIAL_RESULT.value == "PARTIAL_RESULT"
    assert SessionStatus.EXPORT_READY.value == "EXPORT_READY"
    assert SessionStatus.EXPORT_BLOCKED.value == "EXPORT_BLOCKED"
    assert SessionStatus.RUN_FAILED.value == "RUN_FAILED"
    assert SessionStatus.INVALIDATED.value == "INVALIDATED"
    assert SessionStatus.CLOSED.value == "CLOSED"
