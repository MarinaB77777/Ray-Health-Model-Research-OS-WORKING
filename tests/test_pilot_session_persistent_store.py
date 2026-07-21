from pilot_session.persistent_store import PilotSessionPersistentStore
from pilot_session.schemas import ParticipantSession, SessionStatus


def test_persistent_store_saves_and_loads_session(tmp_path):
    storage_path = tmp_path / "sessions.json"

    store = PilotSessionPersistentStore(str(storage_path))

    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
    )
    session.answers = {"k23": 0, "k24": 0}
    session.status = SessionStatus.ANSWERS_RECEIVED

    store.save(session)

    reloaded_store = PilotSessionPersistentStore(str(storage_path))
    loaded = reloaded_store.get("session-1")

    assert loaded is not None
    assert loaded.session_id == "session-1"
    assert loaded.participant_id == "participant-1"
    assert loaded.status == SessionStatus.ANSWERS_RECEIVED
    assert loaded.answers == {"k23": 0, "k24": 0}


def test_persistent_store_preserves_engine_snapshots(tmp_path):
    storage_path = tmp_path / "sessions.json"

    store = PilotSessionPersistentStore(str(storage_path))

    session = ParticipantSession(
        session_id="session-2",
        participant_id="participant-2",
    )
    session.status = SessionStatus.RUN_COMPLETED
    session.raw_engine_result = {"state": "SAFE_DATA_REQUEST"}
    session.public_output = {"summary_text": "Need more data"}
    session.uncertainty_snapshot = {"uncertainty_level": "high"}
    session.next_question_snapshots = [{"variable_code": "d0"}]
    session.acquisition_request_snapshots = {
        "requests": [{"variable_code": "d0"}]
    }

    store.save(session)

    reloaded_store = PilotSessionPersistentStore(str(storage_path))
    loaded = reloaded_store.get("session-2")

    assert loaded is not None
    assert loaded.status == SessionStatus.RUN_COMPLETED
    assert loaded.raw_engine_result == {"state": "SAFE_DATA_REQUEST"}
    assert loaded.public_output == {"summary_text": "Need more data"}
    assert loaded.uncertainty_snapshot == {"uncertainty_level": "high"}
    assert loaded.next_question_snapshots == [{"variable_code": "d0"}]
    assert loaded.acquisition_request_snapshots == {
        "requests": [{"variable_code": "d0"}]
    }


def test_persistent_store_preserves_version_fields(tmp_path):
    storage_path = tmp_path / "sessions.json"

    store = PilotSessionPersistentStore(str(storage_path))

    session = ParticipantSession(
        session_id="session-3",
        participant_id="participant-3",
    )
    session.engine_version = "engine-test"
    session.engine_snapshot_schema_version = "snapshot-test"
    session.public_output_schema_version = "public-test"
    session.export_schema_version = "export-test"
    session.export_policy_version = "policy-test"

    store.save(session)

    reloaded_store = PilotSessionPersistentStore(str(storage_path))
    loaded = reloaded_store.get("session-3")

    assert loaded is not None
    assert loaded.engine_version == "engine-test"
    assert loaded.engine_snapshot_schema_version == "snapshot-test"
    assert loaded.public_output_schema_version == "public-test"
    assert loaded.export_schema_version == "export-test"
    assert loaded.export_policy_version == "policy-test"
