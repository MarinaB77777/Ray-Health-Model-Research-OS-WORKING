from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from temporary_memory.schemas import (
    TemporaryMemoryRecord,
    TemporaryMemoryScope,
    TemporaryMemoryStatus,
    TemporaryMemoryType,
)


class TemporaryMemoryStore:
    """
    In-memory storage for TemporaryMemoryRecord.

    Store responsibilities:
    - create/read/update/delete records
    - change lifecycle status
    - query by session/task/status/scope/type/action
    - list expired records

    Store does NOT:
    - reason
    - decide importance
    - promote to long-term memory
    - perform cleanup policy
    - perform governance checks
    """

    def __init__(self) -> None:
        self._records: dict[str, TemporaryMemoryRecord] = {}

    def add(self, record: TemporaryMemoryRecord) -> TemporaryMemoryRecord:
        self._records[record.id] = record
        return record

    def get(self, record_id: str) -> Optional[TemporaryMemoryRecord]:
        return self._records.get(record_id)

    def update(self, record: TemporaryMemoryRecord) -> TemporaryMemoryRecord:
        if record.id not in self._records:
            raise KeyError(f"Temporary memory record not found: {record.id}")

        self._records[record.id] = record
        return record

    def list_all(self) -> list[TemporaryMemoryRecord]:
        return list(self._records.values())

    def list_by_status(
        self,
        status: TemporaryMemoryStatus,
    ) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self._records.values()
            if record.status == status
        ]

    def list_active(self) -> list[TemporaryMemoryRecord]:
        return self.list_by_status(TemporaryMemoryStatus.ACTIVE)

    def list_unresolved(self) -> list[TemporaryMemoryRecord]:
        return self.list_by_status(TemporaryMemoryStatus.UNRESOLVED)

    def list_by_session(self, session_id: str) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self._records.values()
            if record.session_id == session_id
        ]

    def list_by_task(self, task_id: str) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self._records.values()
            if record.task_id == task_id
        ]

    def list_by_scope(
        self,
        scope: TemporaryMemoryScope,
    ) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self._records.values()
            if record.scope == scope
        ]

    def list_by_type(
        self,
        record_type: TemporaryMemoryType,
    ) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self._records.values()
            if record.record_type == record_type
        ]

    def list_by_action(
        self,
        related_action_id: str,
    ) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self._records.values()
            if record.related_action_id == related_action_id
        ]

    def list_expired(
        self,
        now: Optional[datetime] = None,
    ) -> list[TemporaryMemoryRecord]:
        current_time = now or datetime.now(timezone.utc)

        return [
            record
            for record in self._records.values()
            if record.is_expired(current_time)
        ]

    def mark_used(self, record_id: str) -> TemporaryMemoryRecord:
        record = self._require(record_id)
        record.mark_used()
        return record

    def mark_unresolved(self, record_id: str) -> TemporaryMemoryRecord:
        record = self._require(record_id)
        record.mark_unresolved()
        return record

    def mark_expired(self, record_id: str) -> TemporaryMemoryRecord:
        record = self._require(record_id)
        record.mark_expired()
        return record

    def delete(self, record_id: str, reason: str) -> TemporaryMemoryRecord:
        record = self._require(record_id)
        record.mark_deleted(reason)
        return record

    def purge_deleted(self) -> int:
        deleted_ids = [
            record_id
            for record_id, record in self._records.items()
            if record.status == TemporaryMemoryStatus.DELETED
        ]

        for record_id in deleted_ids:
            del self._records[record_id]

        return len(deleted_ids)

    def clear(self) -> None:
        self._records.clear()

    def _require(self, record_id: str) -> TemporaryMemoryRecord:
        record = self.get(record_id)

        if record is None:
            raise KeyError(f"Temporary memory record not found: {record_id}")

        return record