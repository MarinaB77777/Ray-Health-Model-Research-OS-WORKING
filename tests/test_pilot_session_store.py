from pilot_session.schemas import ParticipantSession
from pilot_session.store import PilotSessionStore


def test_store_save_and_get_session():
    store = PilotSessionStore()

    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
    )

    store.save(session)

    loaded = store.get("session-1")

    assert loaded is not None
    assert loaded.session_id == "session-1"
    assert loaded.participant_id == "participant-1"


def test_store_exists():
    store = PilotSessionStore()

    session = ParticipantSession(
        session_id="session-2",
        participant_id="participant-2",
    )

    store.save(session)

    assert store.exists("session-2") is True
    assert store.exists("missing") is False


def test_store_list_all_sessions():
    store = PilotSessionStore()

    session_1 = ParticipantSession(
        session_id="s1",
        participant_id="p1",
    )

    session_2 = ParticipantSession(
        session_id="s2",
        participant_id="p2",
    )

    store.save(session_1)
    store.save(session_2)

    sessions = store.list_all()

    assert len(sessions) == 2

from datetime import UTC, datetime

from pilot_session.persistent_store import PilotSessionPersistentStore
from pilot_session.schemas import ParticipantSession


def test_persistent_store_preserves_agreement_fields(tmp_path):
    path = tmp_path / "pilot_sessions.json"

    store = PilotSessionPersistentStore(str(path))

    session = ParticipantSession(
        session_id="agreement-session-1",
        participant_id="participant-1",
        agreement_id="agreement-1",
        agreement_version="session-agreement-1",
        agreement_signed_at=datetime(2026, 1, 1, tzinfo=UTC),
        collection_agreement_status="accepted",
    )

    store.save(session)

    reloaded_store = PilotSessionPersistentStore(str(path))
    loaded = reloaded_store.get("agreement-session-1")

    assert loaded is not None
    assert loaded.agreement_id == "agreement-1"
    assert loaded.agreement_version == "session-agreement-1"
    assert loaded.agreement_signed_at == datetime(2026, 1, 1, tzinfo=UTC)
    assert loaded.collection_agreement_status == "accepted"