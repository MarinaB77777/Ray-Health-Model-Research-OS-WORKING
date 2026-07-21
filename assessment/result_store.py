from datetime import datetime, timezone


RESULTS = {}


def save_result(account_id: str | None, session_id: str, study_id: str, result: dict) -> dict:
    record = {
        "account_id": account_id,
        "session_id": session_id,
        "study_id": study_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": result.get("summary", {}),
        "status": "completed",
    }

    RESULTS.setdefault(account_id or "anonymous", []).append(record)
    return record


def list_results(account_id: str) -> list[dict]:
    return RESULTS.get(account_id, [])