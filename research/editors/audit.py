from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4


AUDIT_SCHEMA_VERSION = "research-editor-audit-1"
DEFAULT_AUDIT_PATH = Path("data/research_editor_audit.jsonl")
_LOCK = RLock()


def append_audit_event(
    *,
    action: str,
    actor_id: str,
    object_type: str,
    object_id: str,
    reason: str,
    details: dict | None = None,
    path: Path = DEFAULT_AUDIT_PATH,
) -> dict:
    if not str(actor_id or "").strip():
        raise ValueError("actor_id is required")
    if not str(reason or "").strip():
        raise ValueError("reason is required")
    event = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "event_id": str(uuid4()),
        "occurred_at": datetime.now(UTC).isoformat(),
        "action": action,
        "actor_id": str(actor_id).strip(),
        "object_type": object_type,
        "object_id": object_id,
        "reason": str(reason).strip(),
        "details": details or {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def list_audit_events(
    *,
    object_type: str | None = None,
    object_id: str | None = None,
    limit: int = 200,
    path: Path = DEFAULT_AUDIT_PATH,
) -> list[dict]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if object_type and event.get("object_type") != object_type:
            continue
        if object_id and event.get("object_id") != object_id:
            continue
        events.append(event)
    return events[-max(1, min(int(limit), 1000)):]

