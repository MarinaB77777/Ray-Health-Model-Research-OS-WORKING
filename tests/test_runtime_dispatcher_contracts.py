from datetime import timedelta

from runtime.dispatcher.contracts import (
    RuntimeDispatchReason,
    RuntimeDispatchStatus,
    build_dispatch_target,
    can_dispatch_queue_item,
    dispatch_decision_from_queue_item,
)

from runtime.intake.contracts import RuntimeTargetLayer

from runtime.queue.contracts import (
    RuntimeQueueBlockReason,
    RuntimeQueueItem,
    RuntimeQueueItemType,
    RuntimeQueueStatus,
    utc_now,
)


def make_queue_item(
    queue_id: str = "q1",
    status: RuntimeQueueStatus = RuntimeQueueStatus.READY,
    target_layer: RuntimeTargetLayer | None = RuntimeTargetLayer.ANALYZER,
) -> RuntimeQueueItem:
    return RuntimeQueueItem(
        queue_id=queue_id,
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        status=status,
        target_layer=target_layer,
    )


def test_can_dispatch_ready_item():
    item = make_queue_item()

    assert can_dispatch_queue_item(item) is True


def test_cannot_dispatch_future_ready_item():
    item = make_queue_item(
        queue_id="q-future",
        status=RuntimeQueueStatus.READY,
    )
    item.ready_at = utc_now() + timedelta(minutes=10)

    assert can_dispatch_queue_item(item) is False


def test_build_dispatch_target_from_queue_item():
    item = RuntimeQueueItem(
        queue_id="q-target",
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        status=RuntimeQueueStatus.READY,
        target_layer=RuntimeTargetLayer.ANALYZER,
        target_domain="readiness",
        source_intake_id="intake-1",
        related_action_id="action-1",
        related_task_id="task-1",
        payload_ref="payload-1",
    )

    target = build_dispatch_target(item)

    assert target is not None
    assert target.target_layer == RuntimeTargetLayer.ANALYZER
    assert target.target_domain == "readiness"
    assert target.item_type == RuntimeQueueItemType.ANALYZER_REQUEST
    assert target.source_queue_id == "q-target"
    assert target.source_intake_id == "intake-1"
    assert target.related_action_id == "action-1"
    assert target.related_task_id == "task-1"
    assert target.payload_ref == "payload-1"


def test_build_dispatch_target_returns_none_without_target_layer():
    item = make_queue_item(
        queue_id="q-missing-target",
        target_layer=None,
    )

    target = build_dispatch_target(item)

    assert target is None


def test_dispatch_ready_item_selected():
    item = make_queue_item(queue_id="q-ready")

    decision = dispatch_decision_from_queue_item(item)

    assert decision.queue_id == "q-ready"
    assert decision.dispatch_status == RuntimeDispatchStatus.SELECTED
    assert decision.dispatch_reason == RuntimeDispatchReason.READY_FOR_HANDOFF
    assert decision.dispatch_target is not None
    assert decision.dispatch_target.source_queue_id == "q-ready"


def test_dispatch_terminal_item_not_ready():
    item = make_queue_item(
        queue_id="q-terminal",
        status=RuntimeQueueStatus.COMPLETED,
    )

    decision = dispatch_decision_from_queue_item(item)

    assert decision.dispatch_status == RuntimeDispatchStatus.NOT_READY
    assert decision.dispatch_reason == RuntimeDispatchReason.QUEUE_ITEM_TERMINAL
    assert decision.dispatch_target is None


def test_dispatch_blocked_item_blocked():
    item = RuntimeQueueItem(
        queue_id="q-blocked",
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        status=RuntimeQueueStatus.BLOCKED,
        block_reason=RuntimeQueueBlockReason.AUTHORITY_BLOCKED,
        target_layer=RuntimeTargetLayer.ANALYZER,
    )

    decision = dispatch_decision_from_queue_item(item)

    assert decision.dispatch_status == RuntimeDispatchStatus.BLOCKED
    assert decision.dispatch_reason == RuntimeDispatchReason.QUEUE_ITEM_BLOCKED
    assert decision.dispatch_target is None


def test_dispatch_waiting_item_not_ready():
    item = RuntimeQueueItem(
        queue_id="q-waiting",
        item_type=RuntimeQueueItemType.GOVERNANCE_REVIEW,
        status=RuntimeQueueStatus.WAITING_GOVERNANCE,
        block_reason=RuntimeQueueBlockReason.GOVERNANCE_REQUIRED,
        target_layer=RuntimeTargetLayer.GOVERNANCE,
    )

    decision = dispatch_decision_from_queue_item(item)

    assert decision.dispatch_status == RuntimeDispatchStatus.NOT_READY
    assert decision.dispatch_reason == RuntimeDispatchReason.QUEUE_ITEM_WAITING
    assert decision.dispatch_target is None


def test_dispatch_not_processable_item_not_ready():
    item = make_queue_item(queue_id="q-not-processable")
    item.ready_at = utc_now() + timedelta(minutes=10)

    decision = dispatch_decision_from_queue_item(item)

    assert decision.dispatch_status == RuntimeDispatchStatus.NOT_READY
    assert decision.dispatch_reason == (
        RuntimeDispatchReason.QUEUE_ITEM_NOT_PROCESSABLE
    )
    assert decision.dispatch_target is None


def test_dispatch_missing_target_layer_invalid_queue_state():
    item = make_queue_item(
        queue_id="q-missing-target",
        target_layer=None,
    )

    decision = dispatch_decision_from_queue_item(item)

    assert decision.dispatch_status == RuntimeDispatchStatus.INVALID_QUEUE_STATE
    assert decision.dispatch_reason == RuntimeDispatchReason.MISSING_TARGET_LAYER
    assert decision.dispatch_target is None


def test_dispatch_preserves_uncertainty_and_routing_trace():
    item = make_queue_item(queue_id="q-trace")
    item.uncertainty_notes.append("source was unverified")
    item.routing_trace.append("routed_from_intake")

    decision = dispatch_decision_from_queue_item(item)

    assert decision.uncertainty_notes == ["source was unverified"]
    assert decision.routing_trace == ["routed_from_intake"]
    assert decision.preserve_uncertainty is True