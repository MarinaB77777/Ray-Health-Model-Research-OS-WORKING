from datetime import datetime, timezone


class ResultService:

    def __init__(self):
        self._storage = {}

    def save(
        self,
        account_id: str | None,
        session_id: str,
        study_id: str,
        result: dict,
    ) -> dict:

        record = {
            "account_id": account_id,
            "session_id": session_id,
            "study_id": study_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "summary": result.get("summary", {}),
            "status": "completed",
        }

        self._storage.setdefault(account_id or "anonymous", []).append(record)

        return record

    def list(self, account_id: str):
        return self._storage.get(account_id, [])