from __future__ import annotations

from datetime import datetime, timezone

from temporary_memory.memory_store import TemporaryMemoryStore
from temporary_memory.schemas import (
    TemporaryMemoryRecord,
    TemporaryMemoryStatus,
)


class TemporaryMemoryCleanup:
    """
    Cleanup lifecycle helper for TemporaryMemoryStore.

    Cleanup responsibilities:
    - mark expired records as expired
    - purge records already marked as deleted

    Cleanup does NOT:
    - reason
    - promote records
    - decide importance
    - perform governance checks
    - rewrite payloads
    """

    def __init__(self, store: TemporaryMemoryStore) -> None:
        self.store = store

    def expire_records(
        self,
        now: datetime | None = None,
    ) -> list[TemporaryMemoryRecord]:
        current_time = now or datetime.now(timezone.utc)

        expired_records = self.store.list_expired(current_time)

        for record in expired_records:
            if record.status != TemporaryMemoryStatus.DELETED:
                record.mark_expired()
                self.store.update(record)

        return expired_records

    def purge_deleted(self) -> int:
        return self.store.purge_deleted()