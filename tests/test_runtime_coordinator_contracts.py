from runtime.coordinator.contracts import (
    RuntimeCoordinationReason,
    RuntimeCoordinationStatus,
    coordination_result_from_dispatch,
)

from runtime.dispatcher.contracts import (
    RuntimeDispatchDecision,
    RuntimeDispatchReason,
    RuntimeDispatchStatus,
)

from runtime.queue.contracts import RuntimeQueueStatus


def make_dispatch_decision(
    status: RuntimeDispatchStatus,
    reason: RuntimeDispatchReason,
) -> RuntimeDispatchDecision:
    return RuntimeDispatchDecision(
        queue_id="q1",
        dispatch_status=status,
        dispatch_reason=reason,
        routing_trace=["dispatcher_trace"],
        uncertainty_notes=["uncertainty preserved"],
    )


def test_selected_dispatch_becomes_handoff_prepared():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.SELECTED,
        RuntimeDispatchReason.READY_FOR_HANDOFF,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c1",
        dispatch_decision=dispatch,
    )

    assert result.status == RuntimeCoordinationStatus.HANDOFF_PREPARED
    assert result.reason == RuntimeCoordinationReason.DISPATCH_SELECTED
    assert result.next_queue_status == RuntimeQueueStatus.IN_PROGRESS


def test_no_ready_dispatch_becomes_no_work():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.NO_READY_ITEMS,
        RuntimeDispatchReason.NO_AVAILABLE_READY_ITEMS,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c2",
        dispatch_decision=dispatch,
    )

    assert result.status == RuntimeCoordinationStatus.NO_WORK
    assert result.reason == RuntimeCoordinationReason.NO_READY_DISPATCH
    assert result.next_queue_status is None


def test_blocked_dispatch_becomes_blocked_coordination():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.BLOCKED,
        RuntimeDispatchReason.QUEUE_ITEM_BLOCKED,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c3",
        dispatch_decision=dispatch,
    )

    assert result.status == RuntimeCoordinationStatus.BLOCKED
    assert result.reason == RuntimeCoordinationReason.DISPATCH_BLOCKED
    assert result.next_queue_status is None


def test_not_ready_dispatch_becomes_waiting_coordination():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.NOT_READY,
        RuntimeDispatchReason.QUEUE_ITEM_WAITING,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c4",
        dispatch_decision=dispatch,
    )

    assert result.status == RuntimeCoordinationStatus.WAITING
    assert result.reason == RuntimeCoordinationReason.DISPATCH_NOT_READY
    assert result.next_queue_status is None


def test_invalid_dispatch_state_becomes_failed_coordination():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.INVALID_QUEUE_STATE,
        RuntimeDispatchReason.MISSING_TARGET_LAYER,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c5",
        dispatch_decision=dispatch,
    )

    assert result.status == RuntimeCoordinationStatus.FAILED
    assert result.reason == RuntimeCoordinationReason.INVALID_DISPATCH_STATE


def test_trace_is_preserved_and_extended():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.SELECTED,
        RuntimeDispatchReason.READY_FOR_HANDOFF,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c6",
        dispatch_decision=dispatch,
    )

    assert result.routing_trace == [
        "dispatcher_trace",
        "coordinator_received_dispatch_decision",
        "coordinator_prepared_handoff",
    ]


def test_uncertainty_notes_are_preserved():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.SELECTED,
        RuntimeDispatchReason.READY_FOR_HANDOFF,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c7",
        dispatch_decision=dispatch,
    )

    assert result.uncertainty_notes == ["uncertainty preserved"]
    assert result.preserve_uncertainty is True


def test_next_queue_status_is_only_suggested_not_mutation():
    dispatch = make_dispatch_decision(
        RuntimeDispatchStatus.SELECTED,
        RuntimeDispatchReason.READY_FOR_HANDOFF,
    )

    result = coordination_result_from_dispatch(
        coordination_id="c8",
        dispatch_decision=dispatch,
    )

    assert result.next_queue_status == RuntimeQueueStatus.IN_PROGRESS
    assert result.dispatch_decision == dispatch