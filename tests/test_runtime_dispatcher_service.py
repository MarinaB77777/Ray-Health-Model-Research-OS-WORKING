from datetime import timedelta

from runtime.dispatcher.contracts import (
    RuntimeDispatchReason,
    RuntimeDispatchStatus,
)

from runtime.dispatcher.service import (
    RuntimeDispatcherService,
)

from runtime.intake.contracts import RuntimeTargetLayer

from runtime.queue.contracts import (
    RuntimeQueueBlockReason,
    RuntimeQueueItem,
    RuntimeQueueItemType,
    RuntimeQueueStatus,
    utc_now,
)

from runtime.queue.service import RuntimeQueueService


def make_ready_item(
    queue_id: str = "q1",
) -> RuntimeQueueItem:
    return RuntimeQueueItem(
        queue_id=queue_id,
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        status=RuntimeQueueStatus.READY,
        target_layer=RuntimeTargetLayer.ANALYZER,
    )


def build_dispatcher() -> RuntimeDispatcherService:
    queue_service = RuntimeQueueService()
    return RuntimeDispatcherService(
        queue_service=queue_service,
    )


def test_list_ready_items_returns_processable_items():
    dispatcher = build_dispatcher()

    dispatcher.queue_service.enqueue(
        make_ready_item("ready-1")
    )

    dispatcher.queue_service.enqueue(
        RuntimeQueueItem(
            queue_id="blocked-1",
            item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
            status=RuntimeQueueStatus.BLOCKED,
            block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
            target_layer=RuntimeTargetLayer.ANALYZER,
        )
    )

    ready = dispatcher.list_ready_items()

    assert [item.queue_id for item in ready] == ["ready-1"]


def test_dispatch_queue_item_returns_dispatch_decision():
    dispatcher = build_dispatcher()

    item = make_ready_item("dispatch-1")

    decision = dispatcher.dispatch_queue_item(item)

    assert decision.queue_id == "dispatch-1"
    assert decision.dispatch_status == RuntimeDispatchStatus.SELECTED
    assert (
        decision.dispatch_reason
        == RuntimeDispatchReason.READY_FOR_HANDOFF
    )

    assert decision.dispatch_target is not None
    assert (
        decision.dispatch_target.target_layer
        == RuntimeTargetLayer.ANALYZER
    )


def test_select_next_dispatch_returns_no_ready_items():
    dispatcher = build_dispatcher()

    decision = dispatcher.select_next_dispatch()

    assert (
        decision.dispatch_status
        == RuntimeDispatchStatus.NO_READY_ITEMS
    )

    assert (
        decision.dispatch_reason
        == RuntimeDispatchReason.NO_AVAILABLE_READY_ITEMS
    )

    assert decision.dispatch_target is None

    assert decision.routing_trace == [
        "dispatcher_checked_ready_queue",
    ]


def test_select_next_dispatch_selects_first_ready_item():
    dispatcher = build_dispatcher()

    dispatcher.queue_service.enqueue(
        make_ready_item("ready-first")
    )

    dispatcher.queue_service.enqueue(
        make_ready_item("ready-second")
    )

    decision = dispatcher.select_next_dispatch()

    assert decision.queue_id == "ready-first"

    assert (
        decision.dispatch_status
        == RuntimeDispatchStatus.SELECTED
    )

    assert (
        decision.dispatch_reason
        == RuntimeDispatchReason.READY_FOR_HANDOFF
    )

    assert decision.dispatch_target is not None

    assert (
        decision.dispatch_target.source_queue_id
        == "ready-first"
    )


def test_dispatcher_preserves_operational_trace():
    dispatcher = build_dispatcher()

    item = make_ready_item("trace-1")

    item.routing_trace.append(
        "queue_marked_ready"
    )

    dispatcher.queue_service.enqueue(item)

    decision = dispatcher.select_next_dispatch()

    assert decision.routing_trace == [
        "queue_marked_ready",
        "dispatcher_selected_ready_item",
    ]


def test_dispatcher_preserves_uncertainty_notes():
    dispatcher = build_dispatcher()

    item = make_ready_item("uncertainty-1")

    item.uncertainty_notes.append(
        "source freshness low"
    )

    dispatcher.queue_service.enqueue(item)

    decision = dispatcher.select_next_dispatch()

    assert decision.uncertainty_notes == [
        "source freshness low",
    ]


def test_dispatcher_does_not_dispatch_waiting_item():
    dispatcher = build_dispatcher()

    dispatcher.queue_service.enqueue(
        RuntimeQueueItem(
            queue_id="waiting-1",
            item_type=RuntimeQueueItemType.GOVERNANCE_REVIEW,
            status=RuntimeQueueStatus.WAITING_GOVERNANCE,
            block_reason=(
                RuntimeQueueBlockReason.GOVERNANCE_REQUIRED
            ),
            target_layer=RuntimeTargetLayer.GOVERNANCE,
        )
    )

    decision = dispatcher.select_next_dispatch()

    assert (
        decision.dispatch_status
        == RuntimeDispatchStatus.NO_READY_ITEMS
    )


def test_dispatcher_does_not_dispatch_future_ready_item():
    dispatcher = build_dispatcher()

    item = make_ready_item("future-1")

    item.ready_at = utc_now() + timedelta(minutes=10)

    dispatcher.queue_service.enqueue(item)

    decision = dispatcher.select_next_dispatch()

    assert (
        decision.dispatch_status
        == RuntimeDispatchStatus.NO_READY_ITEMS
    )


def test_dispatcher_does_not_invent_work():
    dispatcher = build_dispatcher()

    decision = dispatcher.select_next_dispatch()

    assert decision.dispatch_target is None

    assert (
        decision.dispatch_reason
        == RuntimeDispatchReason.NO_AVAILABLE_READY_ITEMS
    )


def test_dispatcher_selection_is_not_hidden_prioritization():
    dispatcher = build_dispatcher()

    dispatcher.queue_service.enqueue(
        make_ready_item("first")
    )

    dispatcher.queue_service.enqueue(
        make_ready_item("second")
    )

    dispatcher.queue_service.enqueue(
        make_ready_item("third")
    )

    decision = dispatcher.select_next_dispatch()

    assert decision.queue_id == "first"