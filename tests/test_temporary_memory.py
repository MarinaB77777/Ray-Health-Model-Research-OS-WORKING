from datetime import datetime, timedelta, timezone

import pytest

from temporary_memory.memory_store import TemporaryMemoryStore
from temporary_memory.routing import TemporaryMemoryRouter
from temporary_memory.schemas import (
    MemoryFreshness,
    MemoryTruthType,
    TemporaryMemoryRecord,
    TemporaryMemoryStatus,
    TemporaryMemoryType,
    WORKING_MEMORY_CLASS,
)


def test_add_and_get_record() -> None:
    store = TemporaryMemoryStore()
    record = TemporaryMemoryRecord(
        record_type=TemporaryMemoryType.NEXT_QUESTION,
        payload={"question": "Need clarification"},
        truth_type=MemoryTruthType.OPERATIONAL_STATE,
        provenance_refs=("clarification:1",),
    )
    store.add(record)
    loaded = store.get(record.id)
    assert loaded is not None
    assert loaded.id == record.id
    assert loaded.record_type == TemporaryMemoryType.NEXT_QUESTION
    assert loaded.memory_class == WORKING_MEMORY_CLASS


def test_store_rejects_duplicate_record_id() -> None:
    store = TemporaryMemoryStore()
    record = TemporaryMemoryRecord()
    store.add(record)
    with pytest.raises(ValueError):
        store.add(record)


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


def test_do_not_use_removes_record_from_reusable_routing() -> None:
    store = TemporaryMemoryStore()
    record = TemporaryMemoryRecord(record_type=TemporaryMemoryType.WARNING)
    store.add(record)
    store.mark_do_not_use(record.id, "human requested non-use")
    assert store.list_reusable() == []
    assert TemporaryMemoryRouter(store.list_all()).warnings() == []
    assert store.get(record.id).status == TemporaryMemoryStatus.DO_NOT_USE


def test_invalidation_is_not_rewritten_as_expiry() -> None:
    store = TemporaryMemoryStore()
    record = TemporaryMemoryRecord()
    store.add(record)
    store.invalidate(record.id, "superseded by verified correction")
    assert store.get(record.id).status == TemporaryMemoryStatus.INVALIDATED
    assert store.list_expired() == []


def test_stale_record_is_not_reused() -> None:
    store = TemporaryMemoryStore()
    record = TemporaryMemoryRecord(
        record_type=TemporaryMemoryType.NEXT_QUESTION,
        freshness=MemoryFreshness.STALE,
    )
    store.add(record)
    assert TemporaryMemoryRouter(store.list_all()).next_questions() == []


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


def test_raw_inner_core_keys_are_rejected() -> None:
    store = TemporaryMemoryStore()
    for forbidden in (
        "heart_of_ray",
        "heart_of_human",
        "raw_inner_core",
        "ray_self_health_authority_raw",
    ):
        with pytest.raises(PermissionError):
            store.add(TemporaryMemoryRecord(payload={forbidden: {"secret": "x"}}))


def test_working_memory_cannot_self_promote() -> None:
    store = TemporaryMemoryStore()
    with pytest.raises(PermissionError):
        store.add(TemporaryMemoryRecord(promotion_allowed=True))


def test_working_store_rejects_other_memory_class() -> None:
    store = TemporaryMemoryStore()
    with pytest.raises(PermissionError):
        store.add(TemporaryMemoryRecord(memory_class="semantic"))
