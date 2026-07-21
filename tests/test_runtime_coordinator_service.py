from runtime.coordinator.contracts import (
    RuntimeCoordinationStatus,
)

from runtime.coordinator.runtime_service import RuntimeCoordinatorService

from runtime.intake.contracts import RuntimeTargetLayer

from runtime.queue.contracts import (
    RuntimeQueueBlockReason,
    RuntimeQueueItem,
    RuntimeQueueItemType,
    RuntimeQueueStatus,
)

from runtime.queue.service import RuntimeQueueService


def make_ready_item(queue_id: str = "q1") -> RuntimeQueueItem:
    return RuntimeQueueItem(
        queue_id=queue_id,
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        status=RuntimeQueueStatus.READY,
        target_layer=RuntimeTargetLayer.ANALYZER,
    )


def test_coordinate_next_prepares_handoff_and_marks_in_progress():
    queue_service = RuntimeQueueService()
    queue_service.enqueue(make_ready_item("q1"))

    coordinator = RuntimeCoordinatorService(
        queue_service=queue_service,
    )

    result = coordinator.coordinate_next(coordination_id="c1")
    item = queue_service.get_item("q1")

    assert result.status == RuntimeCoordinationStatus.HANDOFF_PREPARED
    assert item is not None
    assert item.status == RuntimeQueueStatus.IN_PROGRESS
    assert "coordinator_applied_explicit_queue_status_update" in result.routing_trace


def test_coordinate_next_no_ready_items_does_not_invent_work():
    queue_service = RuntimeQueueService()

    coordinator = RuntimeCoordinatorService(
        queue_service=queue_service,
    )

    result = coordinator.coordinate_next(coordination_id="c2")

    assert result.status == RuntimeCoordinationStatus.NO_WORK
    assert result.dispatch_decision is not None
    assert result.dispatch_decision.queue_id is None


def test_coordinate_next_does_not_dispatch_blocked_item():
    queue_service = RuntimeQueueService()

    queue_service.enqueue(
        RuntimeQueueItem(
            queue_id="blocked",
            item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
            status=RuntimeQueueStatus.BLOCKED,
            block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
            target_layer=RuntimeTargetLayer.ANALYZER,
        )
    )

    coordinator = RuntimeCoordinatorService(
        queue_service=queue_service,
    )

    result = coordinator.coordinate_next(coordination_id="c3")
    item = queue_service.get_item("blocked")

    assert result.status == RuntimeCoordinationStatus.NO_WORK
    assert item is not None
    assert item.status == RuntimeQueueStatus.BLOCKED


def test_coordinate_next_preserves_first_ready_selection():
    queue_service = RuntimeQueueService()

    queue_service.enqueue(make_ready_item("first"))
    queue_service.enqueue(make_ready_item("second"))

    coordinator = RuntimeCoordinatorService(
        queue_service=queue_service,
    )

    result = coordinator.coordinate_next(coordination_id="c4")

    first = queue_service.get_item("first")
    second = queue_service.get_item("second")

    assert result.status == RuntimeCoordinationStatus.HANDOFF_PREPARED
    assert result.dispatch_decision is not None
    assert result.dispatch_decision.queue_id == "first"

    assert first is not None
    assert first.status == RuntimeQueueStatus.IN_PROGRESS

    assert second is not None
    assert second.status == RuntimeQueueStatus.READY


def test_coordinate_next_handoff_prepared_is_not_success():
    queue_service = RuntimeQueueService()
    queue_service.enqueue(make_ready_item("q-success-boundary"))

    coordinator = RuntimeCoordinatorService(
        queue_service=queue_service,
    )

    result = coordinator.coordinate_next(coordination_id="c5")

    assert result.status == RuntimeCoordinationStatus.HANDOFF_PREPARED
    assert result.explanation is not None
    assert "does not mean execution or success" in result.explanation