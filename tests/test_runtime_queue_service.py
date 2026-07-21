from datetime import timedelta

from runtime.queue.contracts import (
    RuntimeQueueItem,
    RuntimeQueueStatus,
    RuntimeQueueItemType,
    RuntimeQueueBlockReason,
    utc_now,
)

from runtime.queue.service import RuntimeQueueService


def make_item(
    queue_id: str = "q1",
    status: RuntimeQueueStatus = RuntimeQueueStatus.PENDING,
) -> RuntimeQueueItem:
    return RuntimeQueueItem(
        queue_id=queue_id,
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=status,
    )


def test_enqueue_does_not_mean_approved():
    service = RuntimeQueueService()
    item = make_item("q1")

    queued = service.enqueue(item)

    assert queued.queue_id == "q1"
    assert queued.status == RuntimeQueueStatus.PENDING
    assert service.get_item("q1") is not None


def test_list_pending_exposes_store_pending_items():
    service = RuntimeQueueService()

    service.enqueue(make_item("pending"))
    service.enqueue(make_item("ready", RuntimeQueueStatus.READY))

    pending = service.list_pending()

    assert [item.queue_id for item in pending] == ["pending"]


def test_mark_waiting_governance():
    service = RuntimeQueueService()
    service.enqueue(make_item("q2"))

    item = service.mark_waiting_governance("q2")

    assert item is not None
    assert item.status == RuntimeQueueStatus.WAITING_GOVERNANCE
    assert item.block_reason == RuntimeQueueBlockReason.GOVERNANCE_REQUIRED


def test_mark_waiting_human_confirmation():
    service = RuntimeQueueService()
    service.enqueue(make_item("q3"))

    item = service.mark_waiting_human_confirmation("q3")

    assert item is not None
    assert item.status == RuntimeQueueStatus.WAITING_HUMAN_CONFIRMATION
    assert item.block_reason == (
        RuntimeQueueBlockReason.HUMAN_CONFIRMATION_REQUIRED
    )


def test_mark_waiting_clarification():
    service = RuntimeQueueService()
    service.enqueue(make_item("q4"))

    item = service.mark_waiting_clarification("q4")

    assert item is not None
    assert item.status == RuntimeQueueStatus.WAITING_CLARIFICATION
    assert item.block_reason == RuntimeQueueBlockReason.CLARIFICATION_REQUIRED


def test_mark_waiting_dependency():
    service = RuntimeQueueService()
    service.enqueue(make_item("q5"))

    item = service.mark_waiting_dependency(
        queue_id="q5",
        dependency_ref="dep-1",
    )

    assert item is not None
    assert item.status == RuntimeQueueStatus.WAITING_DEPENDENCY
    assert item.block_reason == RuntimeQueueBlockReason.DEPENDENCY_WAIT
    assert item.waiting_for == "dep-1"


def test_mark_blocked():
    service = RuntimeQueueService()
    service.enqueue(make_item("q6"))

    item = service.mark_blocked(
        queue_id="q6",
        block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
    )

    assert item is not None
    assert item.status == RuntimeQueueStatus.BLOCKED
    assert item.block_reason == RuntimeQueueBlockReason.AUTHORITY_BLOCKED
    assert item.can_be_processed() is False


def test_mark_ready_clears_waiting_block_reason():
    service = RuntimeQueueService()
    service.enqueue(make_item("q7"))

    service.mark_waiting_clarification("q7")
    item = service.mark_ready("q7")

    assert item is not None
    assert item.status == RuntimeQueueStatus.READY
    assert item.block_reason is None
    assert item.can_be_processed() is True


def test_mark_in_progress_is_not_real_world_success():
    service = RuntimeQueueService()
    service.enqueue(make_item("q8", RuntimeQueueStatus.READY))

    item = service.mark_in_progress("q8")

    assert item is not None
    assert item.status == RuntimeQueueStatus.IN_PROGRESS
    assert item.can_be_processed() is False


def test_mark_completed_is_not_real_world_outcome():
    service = RuntimeQueueService()
    service.enqueue(make_item("q9", RuntimeQueueStatus.IN_PROGRESS))

    item = service.mark_completed("q9")

    assert item is not None
    assert item.status == RuntimeQueueStatus.COMPLETED
    assert item.is_terminal() is True


def test_expire_due_items_marks_expired_not_deleted():
    service = RuntimeQueueService()

    item = RuntimeQueueItem(
        queue_id="q10",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
        expires_at=utc_now() - timedelta(seconds=1),
    )

    service.enqueue(item)

    expired_ids = service.expire_due_items()

    saved = service.get_item("q10")

    assert expired_ids == ["q10"]
    assert saved is not None
    assert saved.status == RuntimeQueueStatus.EXPIRED
    assert saved.block_reason == RuntimeQueueBlockReason.EXPIRED


def test_remove_item_deletes_from_queue_store():
    service = RuntimeQueueService()
    service.enqueue(make_item("q11"))

    assert service.remove_item("q11") is True
    assert service.get_item("q11") is None