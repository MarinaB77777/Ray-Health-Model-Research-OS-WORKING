from datetime import timedelta
import pytest

from runtime.queue.contracts import (
    RuntimeQueueItem,
    RuntimeQueueStatus,
    RuntimeQueueItemType,
    RuntimeQueueBlockReason,
    utc_now,
)

from runtime.queue.store import RuntimeQueueStore


def make_item(
    queue_id: str = "q1",
    status: RuntimeQueueStatus = RuntimeQueueStatus.PENDING,
) -> RuntimeQueueItem:
    return RuntimeQueueItem(
        queue_id=queue_id,
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=status,
    )


def test_add_and_get_item():
    store = RuntimeQueueStore()
    item = make_item("q1")

    store.add_item(item)

    assert store.get_item("q1") == item


def test_update_status_is_validation_safe():
    store = RuntimeQueueStore()
    item = make_item("q2")
    store.add_item(item)

    with pytest.raises(ValueError):
        store.update_status(
            queue_id="q2",
            status=RuntimeQueueStatus.BLOCKED,
            block_reason=None,
        )

    saved = store.get_item("q2")

    assert saved is not None
    assert saved.status == RuntimeQueueStatus.PENDING
    assert saved.block_reason is None


def test_mark_blocked_sets_reason():
    store = RuntimeQueueStore()
    store.add_item(make_item("q3"))

    item = store.mark_blocked(
        queue_id="q3",
        block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
    )

    assert item is not None
    assert item.status == RuntimeQueueStatus.BLOCKED
    assert item.block_reason == RuntimeQueueBlockReason.AUTHORITY_BLOCKED
    assert item.can_be_processed() is False


def test_waiting_governance_is_listed_as_waiting():
    store = RuntimeQueueStore()
    store.add_item(make_item("q4"))

    store.mark_waiting_governance("q4")

    waiting = store.list_waiting()

    assert len(waiting) == 1
    assert waiting[0].queue_id == "q4"
    assert waiting[0].status == RuntimeQueueStatus.WAITING_GOVERNANCE


def test_waiting_dependency_sets_dependency_ref_safely():
    store = RuntimeQueueStore()
    store.add_item(make_item("q5"))

    item = store.mark_waiting_dependency(
        queue_id="q5",
        dependency_ref="dep-1",
    )

    assert item is not None
    assert item.status == RuntimeQueueStatus.WAITING_DEPENDENCY
    assert item.block_reason == RuntimeQueueBlockReason.DEPENDENCY_WAIT
    assert item.waiting_for == "dep-1"


def test_mark_ready_clears_block_reason():
    store = RuntimeQueueStore()
    store.add_item(make_item("q6"))

    store.mark_waiting_clarification("q6")
    item = store.mark_ready("q6")

    assert item is not None
    assert item.status == RuntimeQueueStatus.READY
    assert item.block_reason is None
    assert item.can_be_processed() is True


def test_list_ready_uses_can_be_processed():
    store = RuntimeQueueStore()

    ready = RuntimeQueueItem(
        queue_id="ready",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
    )

    future_ready = RuntimeQueueItem(
        queue_id="future",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
        ready_at=utc_now() + timedelta(minutes=10),
    )

    blocked = RuntimeQueueItem(
        queue_id="blocked",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.BLOCKED,
        block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
    )

    store.add_item(ready)
    store.add_item(future_ready)
    store.add_item(blocked)

    ready_items = store.list_ready()

    assert [item.queue_id for item in ready_items] == ["ready"]


def test_expire_due_items_marks_expired():
    store = RuntimeQueueStore()

    item = RuntimeQueueItem(
        queue_id="q7",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
        expires_at=utc_now() - timedelta(seconds=1),
    )

    store.add_item(item)

    expired_ids = store.expire_due_items()

    expired = store.get_item("q7")

    assert expired_ids == ["q7"]
    assert expired is not None
    assert expired.status == RuntimeQueueStatus.EXPIRED
    assert expired.block_reason == RuntimeQueueBlockReason.EXPIRED


def test_expire_due_items_does_not_expire_blocked_item():
    store = RuntimeQueueStore()

    item = RuntimeQueueItem(
        queue_id="q8",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.BLOCKED,
        block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
        expires_at=utc_now() - timedelta(seconds=1),
    )

    store.add_item(item)

    expired_ids = store.expire_due_items()

    saved = store.get_item("q8")

    assert expired_ids == []
    assert saved is not None
    assert saved.status == RuntimeQueueStatus.BLOCKED


def test_list_terminal_contains_completed_expired_cancelled():
    store = RuntimeQueueStore()

    store.add_item(make_item("completed", RuntimeQueueStatus.COMPLETED))

    store.add_item(
        RuntimeQueueItem(
            queue_id="expired",
            item_type=RuntimeQueueItemType.COORDINATION_STEP,
            status=RuntimeQueueStatus.EXPIRED,
            block_reason=RuntimeQueueBlockReason.EXPIRED,
        )
    )

    store.add_item(
        RuntimeQueueItem(
            queue_id="cancelled",
            item_type=RuntimeQueueItemType.COORDINATION_STEP,
            status=RuntimeQueueStatus.CANCELLED,
            block_reason=RuntimeQueueBlockReason.CANCELLED_BY_HUMAN,
        )
    )

    ids = {item.queue_id for item in store.list_terminal()}

    assert ids == {"completed", "expired", "cancelled"}


def test_remove_item():
    store = RuntimeQueueStore()
    store.add_item(make_item("q9"))

    assert store.remove_item("q9") is True
    assert store.get_item("q9") is None
    assert store.remove_item("q9") is False