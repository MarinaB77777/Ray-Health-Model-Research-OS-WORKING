from runtime.coordinator.contracts import (
    RuntimeCoordinationResult,
    RuntimeCoordinationReason,
    RuntimeCoordinationStatus,
)

from runtime.dispatcher.contracts import (
    RuntimeDispatchDecision,
    RuntimeDispatchReason,
    RuntimeDispatchStatus,
    RuntimeDispatchTarget,
)

from runtime.handoff.bridge import (
    RuntimeHandoffBridge,
    RuntimeHandoffBridgeStatus,
)

from runtime.handoff.contracts import RuntimeHandoffStatus

from runtime.intake.contracts import RuntimeTargetLayer

from runtime.queue.contracts import (
    RuntimeQueueItemType,
    RuntimeQueueStatus,
)


def make_handoff_ready_coordination(
    target_layer: RuntimeTargetLayer = RuntimeTargetLayer.ANALYZER,
) -> RuntimeCoordinationResult:
    dispatch_target = RuntimeDispatchTarget(
        target_layer=target_layer,
        target_domain="readiness",
        item_type=RuntimeQueueItemType.ANALYZER_REQUEST,
        source_queue_id="q1",
        source_intake_id="intake-1",
        payload_ref="payload-1",
    )

    dispatch_decision = RuntimeDispatchDecision(
        queue_id="q1",
        dispatch_status=RuntimeDispatchStatus.SELECTED,
        dispatch_reason=RuntimeDispatchReason.READY_FOR_HANDOFF,
        dispatch_target=dispatch_target,
        routing_trace=["dispatcher_selected_ready_item"],
        uncertainty_notes=["source not verified"],
    )

    return RuntimeCoordinationResult(
        coordination_id="coord-1",
        status=RuntimeCoordinationStatus.HANDOFF_PREPARED,
        reason=RuntimeCoordinationReason.DISPATCH_SELECTED,
        dispatch_decision=dispatch_decision,
        next_queue_status=RuntimeQueueStatus.IN_PROGRESS,
        routing_trace=[
            "dispatcher_selected_ready_item",
            "coordinator_received_dispatch_decision",
            "coordinator_prepared_handoff",
        ],
        uncertainty_notes=["source not verified"],
    )


def test_bridge_rejects_not_handoff_ready_coordination():
    bridge = RuntimeHandoffBridge()

    coordination = RuntimeCoordinationResult(
        coordination_id="coord-no-work",
        status=RuntimeCoordinationStatus.NO_WORK,
        reason=RuntimeCoordinationReason.NO_READY_DISPATCH,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b1",
        coordination_result=coordination,
    )

    assert result.status == RuntimeHandoffBridgeStatus.NOT_HANDOFF_READY
    assert result.handoff_request is None
    assert result.handoff_decision is None


def test_bridge_rejects_missing_dispatch_decision():
    bridge = RuntimeHandoffBridge()

    coordination = RuntimeCoordinationResult(
        coordination_id="coord-missing-dispatch",
        status=RuntimeCoordinationStatus.HANDOFF_PREPARED,
        reason=RuntimeCoordinationReason.DISPATCH_SELECTED,
        dispatch_decision=None,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b2",
        coordination_result=coordination,
    )

    assert result.status == (
        RuntimeHandoffBridgeStatus.MISSING_DISPATCH_DECISION
    )
    assert result.handoff_request is None
    assert result.handoff_decision is None


def test_bridge_rejects_missing_dispatch_target():
    bridge = RuntimeHandoffBridge()

    dispatch_decision = RuntimeDispatchDecision(
        queue_id="q-missing-target",
        dispatch_status=RuntimeDispatchStatus.SELECTED,
        dispatch_reason=RuntimeDispatchReason.READY_FOR_HANDOFF,
        dispatch_target=None,
    )

    coordination = RuntimeCoordinationResult(
        coordination_id="coord-missing-target",
        status=RuntimeCoordinationStatus.HANDOFF_PREPARED,
        reason=RuntimeCoordinationReason.DISPATCH_SELECTED,
        dispatch_decision=dispatch_decision,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b3",
        coordination_result=coordination,
    )

    assert result.status == RuntimeHandoffBridgeStatus.MISSING_DISPATCH_TARGET
    assert result.handoff_request is None
    assert result.handoff_decision is None


def test_bridge_creates_handoff_request_for_analyzer():
    bridge = RuntimeHandoffBridge()

    coordination = make_handoff_ready_coordination(
        target_layer=RuntimeTargetLayer.ANALYZER,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b4",
        coordination_result=coordination,
    )

    assert result.status == RuntimeHandoffBridgeStatus.HANDOFF_DECISION_READY
    assert result.handoff_request is not None
    assert result.handoff_request.target_id == "analyzer"
    assert result.handoff_request.source_coordination_id == "coord-1"
    assert result.handoff_request.source_queue_id == "q1"
    assert result.handoff_request.source_intake_id == "intake-1"
    assert result.handoff_request.payload_ref == "payload-1"

    assert result.handoff_decision is not None
    assert result.handoff_decision.status == RuntimeHandoffStatus.PREPARED


def test_bridge_maps_communicator_target():
    bridge = RuntimeHandoffBridge()

    coordination = make_handoff_ready_coordination(
        target_layer=RuntimeTargetLayer.COMMUNICATOR,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b5",
        coordination_result=coordination,
    )

    assert result.status == RuntimeHandoffBridgeStatus.HANDOFF_DECISION_READY
    assert result.handoff_request is not None
    assert result.handoff_request.target_id == "communicator"
    assert result.handoff_decision is not None
    assert result.handoff_decision.status == RuntimeHandoffStatus.PREPARED


def test_bridge_maps_governance_target_to_governance_review():
    bridge = RuntimeHandoffBridge()

    coordination = make_handoff_ready_coordination(
        target_layer=RuntimeTargetLayer.GOVERNANCE,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b6",
        coordination_result=coordination,
    )

    assert result.status == RuntimeHandoffBridgeStatus.HANDOFF_DECISION_READY
    assert result.handoff_request is not None
    assert result.handoff_request.target_id == "governance"
    assert result.handoff_decision is not None
    assert result.handoff_decision.status == RuntimeHandoffStatus.PREPARED


def test_bridge_preserves_trace_and_uncertainty():
    bridge = RuntimeHandoffBridge()

    coordination = make_handoff_ready_coordination()

    result = bridge.bridge_coordination_result(
        bridge_id="b7",
        coordination_result=coordination,
    )

    assert result.uncertainty_notes == ["source not verified"]

    assert "handoff_bridge_received_coordination_result" in result.routing_trace
    assert "handoff_bridge_created_handoff_request" in result.routing_trace
    assert "handoff_service_received_request" in result.routing_trace
    assert "handoff_bridge_received_handoff_decision" in result.routing_trace


def test_bridge_does_not_execute_adapter_call():
    bridge = RuntimeHandoffBridge()

    coordination = make_handoff_ready_coordination(
        target_layer=RuntimeTargetLayer.COMMUNICATOR,
    )

    result = bridge.bridge_coordination_result(
        bridge_id="b8",
        coordination_result=coordination,
    )

    assert result.status == RuntimeHandoffBridgeStatus.HANDOFF_DECISION_READY
    assert result.handoff_decision is not None
    assert result.handoff_decision.status == RuntimeHandoffStatus.PREPARED
    assert "Bridge did not execute adapter call" in result.explanation