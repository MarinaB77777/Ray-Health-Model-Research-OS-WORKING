from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import json

from .contracts import RayRole


class RayAuditLog:
    """Append-only metadata audit. Dialogue and participant payloads are excluded."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(
        self,
        *,
        event_type: str,
        role: RayRole,
        owner_id: str,
        page_id: str,
        request_id: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        forbidden = {"message", "raw_answers", "raw_data", "raw_sensor_stream"}
        safe_details = {
            key: value
            for key, value in (details or {}).items()
            if key not in forbidden
        }
        event = {
            "event_type": event_type,
            "role": role.value,
            "owner_id": owner_id,
            "page_id": page_id,
            "request_id": request_id,
            "status": status,
            "details": safe_details,
            "occurred_at": datetime.now(UTC).isoformat(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
