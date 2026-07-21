from datetime import datetime, timedelta, timezone

from temporary_memory.memory_store import TemporaryMemoryStore
from temporary_memory.schemas import (
    TemporaryMemoryRecord,
    TemporaryMemoryStatus,
    TemporaryMemoryType,
)


def test_add_and_get_record() -> None:
    store = TemporaryMemoryStore()

    record = TemporaryMemoryRecord(
        record_type=TemporaryMemoryType.NEXT_QUESTION,
        payload={"question": "Need clarification"},
    )

    store.add(record)

    loaded = store.get(record.id)

    assert loaded is not None
    assert loaded.id == record.id
    assert loaded.record_type == TemporaryMemoryType.NEXT_QUESTION


def test_mark_used() -> None:
    store = TemporaryMemoryStore()

    record = TemporaryMemoryRecord()

    store.add(record)

    store.mark_used(record.id)

    updated = store.get(record.id)

    assert updated is not None
    assert updated.status == TemporaryMemoryStatus.USED


def test_mark_unresolved() -> None:
    store = TemporaryMemoryStore()

    record = TemporaryMemoryRecord()

    store.add(record)

    store.mark_unresolved(record.id)

    updated = store.get(record.id)

    assert updated is not None
    assert updated.status == TemporaryMemoryStatus.UNRESOLVED


def test_delete_marks_deleted() -> None:
    store = TemporaryMemoryStore()

    record = TemporaryMemoryRecord()

    store.add(record)

    store.delete(record.id, "cleanup")

    updated = store.get(record.id)

    assert updated is not None
    assert updated.status == TemporaryMemoryStatus.DELETED
    assert updated.deletion_reason == "cleanup"


def test_purge_deleted_removes_records() -> None:
    store = TemporaryMemoryStore()

    record = TemporaryMemoryRecord()

    store.add(record)

    store.delete(record.id, "cleanup")

    purged_count = store.purge_deleted()

    assert purged_count == 1
    assert store.get(record.id) is None


def test_list_expired() -> None:
    store = TemporaryMemoryStore()

    expired_record = TemporaryMemoryRecord(
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    active_record = TemporaryMemoryRecord(
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(expired_record)
    store.add(active_record)

    expired = store.list_expired(datetime.now(timezone.utc))

    assert len(expired) == 1
    assert expired[0].id == expired_record.id