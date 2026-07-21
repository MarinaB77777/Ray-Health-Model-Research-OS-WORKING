import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from pilot_session.schemas import ParticipantSession, SessionStatus


class PilotSessionPersistentStore:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, ParticipantSession] = {}
        self._load()

    def save(self, session: ParticipantSession):
        self._sessions[session.session_id] = session
        self._persist()

    def get(self, session_id: str) -> Optional[ParticipantSession]:
        return self._sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def list_all(self) -> list[ParticipantSession]:
        return list(self._sessions.values())

    def delete(self, session_id: str) -> Optional[ParticipantSession]:
        """Remove one session and persist immediately; eligibility is checked by policy layer."""
        removed = self._sessions.pop(session_id, None)
        if removed is not None:
            self._persist()
        return removed

    def _persist(self):
        data = [
            self._serialize_session(session)
            for session in self._sessions.values()
        ]

        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load(self):
        if not self.storage_path.exists():
            return

        raw = self.storage_path.read_text(encoding="utf-8").strip()

        if not raw:
            return

        data = json.loads(raw)

        for item in data:
            session = self._deserialize_session(item)
            self._sessions[session.session_id] = session

    def _serialize_session(self, session: ParticipantSession) -> dict:
        data = asdict(session)

        data["status"] = session.status.value
        data["created_at"] = session.created_at.isoformat()
        data["updated_at"] = session.updated_at.isoformat()
        data["closed_at"] = (
            session.closed_at.isoformat()
            if session.closed_at is not None
            else None
        )
        data["agreement_signed_at"] = (
            session.agreement_signed_at.isoformat()
            if session.agreement_signed_at is not None
            else None
        )
        return data

    def _deserialize_session(self, data: dict) -> ParticipantSession:
        return ParticipantSession(
            session_id=data["session_id"],
            participant_id=data["participant_id"],
            subject_link_id=data.get("subject_link_id"),
            study_id=data.get("study_id"),
            participant_role=data.get("participant_role"),
            synchronization_reference=data.get("synchronization_reference"),
            agreement_id=data.get("agreement_id"),
            agreement_version=data.get("agreement_version"),
            agreement_signed_at=(
                datetime.fromisoformat(data["agreement_signed_at"])
                if data.get("agreement_signed_at") is not None
                else None
            ),
            collection_agreement_status=data.get("collection_agreement_status"),
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            closed_at=(
                datetime.fromisoformat(data["closed_at"])
                if data.get("closed_at") is not None
                else None
            ),
            answers=data.get("answers", {}),
            domain_data_identity=data.get("domain_data_identity", {}),
            answer_revision_count=data.get("answer_revision_count", 0),
            answer_merge_history=data.get("answer_merge_history", []),
            questionnaire_submissions=data.get(
                "questionnaire_submissions",
                [],
            ),
            research_answer_records=data.get(
                "research_answer_records",
                [],
            ),
            run_count=data.get("run_count", 0),
            run_history=data.get("run_history", []),
            engine_version=data.get("engine_version", "mvp-1"),
            engine_snapshot_schema_version=data.get(
                "engine_snapshot_schema_version",
                "mvp-1",
            ),
            public_output_schema_version=data.get(
                "public_output_schema_version",
                "mvp-1",
            ),
            export_schema_version=data.get("export_schema_version", "mvp-1"),
            raw_engine_result=data.get("raw_engine_result", {}),
            public_output=data.get("public_output", {}),
            next_question_snapshots=data.get("next_question_snapshots", []),
            acquisition_request_snapshots=data.get(
                "acquisition_request_snapshots",
                {},
            ),
            uncertainty_snapshot=data.get("uncertainty_snapshot", {}),
            export_generated=data.get("export_generated", False),
            export_policy_version=data.get("export_policy_version", "mvp-1"),
            invalidated=data.get("invalidated", False),
            invalidation_reason=data.get("invalidation_reason"),
        )
