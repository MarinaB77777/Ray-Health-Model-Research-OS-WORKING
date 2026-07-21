from pilot_session.schemas import ParticipantSession


class PilotSessionStore:
    def __init__(self):
        self._sessions = {}

    def save(self, session: ParticipantSession):
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> ParticipantSession | None:
        return self._sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def list_all(self) -> list[ParticipantSession]:
        return list(self._sessions.values())
