# runtime/event_log.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from runtime.schemas import RuntimeEvent, RuntimeEventType, RuntimeStatus
from runtime.statuses import require_valid_transition


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_runtime_event(
    *,
    action_id: str,
    event_type: RuntimeEventType,
    previous_status: Optional[RuntimeStatus] = None,
    new_status: Optional[RuntimeStatus] = None,
    created_by: str = "runtime",
    payload: Optional[Dict[str, Any]] = None,
    note: Optional[str] = None,
) -> RuntimeEvent:
    """
    Creates a RuntimeEvent.

    Runtime events are append-only facts.
    They do NOT rewrite Analyst or Governance data.
    """

    if previous_status is not None and new_status is not None:
        require_valid_transition(previous_status, new_status)

    return RuntimeEvent(
        event_id=str(uuid4()),
        action_id=action_id,
        event_type=event_type,
        previous_status=previous_status,
        new_status=new_status,
        created_by=created_by,
        created_at=utc_now_iso(),
        payload=payload or {},
        note=note,
    )


class RuntimeEventLog:
    """
    MVP in-memory event log.

    Later this can be replaced with DB-backed storage.
    """

    def __init__(self) -> None:
        self._events: list[RuntimeEvent] = []

    def append(self, event: RuntimeEvent) -> RuntimeEvent:
        self._events.append(event)
        return event

    def create_and_append(
        self,
        *,
        action_id: str,
        event_type: RuntimeEventType,
        previous_status: Optional[RuntimeStatus] = None,
        new_status: Optional[RuntimeStatus] = None,
        created_by: str = "runtime",
        payload: Optional[Dict[str, Any]] = None,
        note: Optional[str] = None,
    ) -> RuntimeEvent:
        event = create_runtime_event(
            action_id=action_id,
            event_type=event_type,
            previous_status=previous_status,
            new_status=new_status,
            created_by=created_by,
            payload=payload,
            note=note,
        )
        return self.append(event)

    def list_for_action(self, action_id: str) -> list[RuntimeEvent]:
        return [event for event in self._events if event.action_id == action_id]

    def all_events(self) -> list[RuntimeEvent]:
        return list(self._events)