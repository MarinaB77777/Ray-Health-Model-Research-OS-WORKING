import pytest
from datetime import timedelta

from runtime.queue.contracts import (
    RuntimeQueueItem,
    RuntimeQueueStatus,
    RuntimeQueuePriority,
    RuntimeQueueItemType,
    RuntimeQueueBlockReason,
    utc_now,
)

from runtime.intake.contracts import RuntimeTargetLayer


def test_queue_item_defaults_are_safe():
    item = RuntimeQueueItem(
        queue_id="q1",
        item_type=RuntimeQueueItemType.INTAKE_ROUTE,
    )

    assert item.status == RuntimeQueueStatus.PENDING
    assert item.priority == RuntimeQueuePriority.NORMAL
    assert item.retry_count == 0
    assert item.max_retries == 0
    assert item.block_reason is None
    assert item.can_be_processed() is True


def test_target_layer_uses_runtime_target_layer_enum():
    item = RuntimeQueueItem(
        queue_id="q2",
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        target_layer=RuntimeTargetLayer.ANALYZER,
    )

    assert item.target_layer == RuntimeTargetLayer.ANALYZER


def test_blocked_item_requires_block_reason():
    with pytest.raises(ValueError):
        RuntimeQueueItem(
            queue_id="q3",
            item_type=RuntimeQueueItemType.INTAKE_ROUTE,
            status=RuntimeQueueStatus.BLOCKED,
        )


def test_blocked_item_is_not_processable():
    item = RuntimeQueueItem(
        queue_id="q4",
        item_type=RuntimeQueueItemType.INTAKE_ROUTE,
        status=RuntimeQueueStatus.BLOCKED,
        block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
    )

    assert item.is_blocked() is True
    assert item.can_be_processed() is False


def test_block_reason_not_allowed_for_pending_item():
    with pytest.raises(ValueError):
        RuntimeQueueItem(
            queue_id="q5",
            item_type=RuntimeQueueItemType.INTAKE_ROUTE,
            status=RuntimeQueueStatus.PENDING,
            block_reason=RuntimeQueueBlockReason.INVALID_STATE,
        )


def test_block_reason_allowed_for_waiting_item():
    item = RuntimeQueueItem(
        queue_id="q6",
        item_type=RuntimeQueueItemType.GOVERNANCE_REVIEW,
        status=RuntimeQueueStatus.WAITING_GOVERNANCE,
        block_reason=RuntimeQueueBlockReason.GOVERNANCE_REQUIRED,
    )

    assert item.is_waiting() is True
    assert item.can_be_processed() is False


def test_terminal_items_are_not_processable():
    for status in {
        RuntimeQueueStatus.COMPLETED,
        RuntimeQueueStatus.EXPIRED,
        RuntimeQueueStatus.CANCELLED,
    }:
        item = RuntimeQueueItem(
            queue_id=f"q-terminal-{status.value}",
            item_type=RuntimeQueueItemType.COORDINATION_STEP,
            status=status,
            block_reason=(
                RuntimeQueueBlockReason.EXPIRED
                if status == RuntimeQueueStatus.EXPIRED
                else RuntimeQueueBlockReason.CANCELLED_BY_HUMAN
                if status == RuntimeQueueStatus.CANCELLED
                else None
            ),
        )

        assert item.is_terminal() is True
        assert item.can_be_processed() is False


def test_ready_item_can_be_processed():
    item = RuntimeQueueItem(
        queue_id="q7",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
    )

    assert item.can_be_processed() is True


def test_future_ready_at_blocks_processing():
    item = RuntimeQueueItem(
        queue_id="q8",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
        ready_at=utc_now() + timedelta(minutes=10),
    )

    assert item.can_be_processed() is False


def test_expired_item_blocks_processing_by_time():
    item = RuntimeQueueItem(
        queue_id="q9",
        item_type=RuntimeQueueItemType.COORDINATION_STEP,
        status=RuntimeQueueStatus.READY,
        expires_at=utc_now() - timedelta(seconds=1),
    )

    assert item.can_be_processed() is False


def test_retry_count_must_not_be_negative():
    with pytest.raises(ValueError):
        RuntimeQueueItem(
            queue_id="q10",
            item_type=RuntimeQueueItemType.COORDINATION_STEP,
            retry_count=-1,
        )


def test_max_retries_must_not_be_negative():
    with pytest.raises(ValueError):
        RuntimeQueueItem(
            queue_id="q11",
            item_type=RuntimeQueueItemType.COORDINATION_STEP,
            max_retries=-1,
        )


def test_retry_count_must_not_exceed_max_retries():
    with pytest.raises(ValueError):
        RuntimeQueueItem(
            queue_id="q12",
            item_type=RuntimeQueueItemType.COORDINATION_STEP,
            retry_count=2,
            max_retries=1,
        )