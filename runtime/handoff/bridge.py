from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from runtime.coordinator.contracts import (
    RuntimeCoordinationResult,
    RuntimeCoordinationStatus,
)

from runtime.handoff.contracts import (
    RuntimeHandoffDecision,
    RuntimeHandoffDirection,
    RuntimeHandoffRequest,
)

from runtime.handoff.registry import HandoffCapability
from runtime.handoff.service import RuntimeHandoffService
from runtime.intake.contracts import RuntimeTargetLayer


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeHandoffBridgeStatus(str, Enum):
    HANDOFF_DECISION_READY = "handoff_decision_ready"
    NOT_HANDOFF_READY = "not_handoff_ready"
    MISSING_DISPATCH_DECISION = "missing_dispatch_decision"
    MISSING_DISPATCH_TARGET = "missing_dispatch_target"
    UNSUPPORTED_TARGET_LAYER = "unsupported_target_layer"


class RuntimeHandoffBridgeResult(BaseModel):
    bridge_id: str

    status: RuntimeHandoffBridgeStatus

    coordination_id: str
    handoff_request: Optional[RuntimeHandoffRequest] = None
    handoff_decision: Optional[RuntimeHandoffDecision] = None

    explanation: Optional[str] = None

    routing_trace: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)

    preserve_uncertainty: bool = True
    created_at: datetime = Field(default_factory=utc_now)


TARGET_LAYER_TO_HANDOFF = {
    RuntimeTargetLayer.COMMUNICATOR: (
        "communicator",
        HandoffCapability.COMMUNICATE,
    ),
    RuntimeTargetLayer.GOVERNANCE: (
        "governance",
        HandoffCapability.REQUEST_GOVERNANCE_REVIEW,
    ),
    RuntimeTargetLayer.ANALYZER: (
        "analyzer",
        HandoffCapability.REQUEST_ANALYZER_REVIEW,
    ),
    RuntimeTargetLayer.ANALYST: (
        "analyst",
        HandoffCapability.REQUEST_ANALYST_REASONING,
    ),
    RuntimeTargetLayer.DOMAIN_RAY: (
        "domain_ray",
        HandoffCapability.ROUTE_TO_DOMAIN_RAY,
    ),
    RuntimeTargetLayer.TEMPORARY_MEMORY: (
        "temporary_memory",
        HandoffCapability.WRITE_TEMPORARY_MEMORY,
    ),
    RuntimeTargetLayer.SHARED_ACTION: (
        "shared_action",
        HandoffCapability.UPDATE_SHARED_ACTION,
    ),
}


class RuntimeHandoffBridge:
    """
    Coordinator -> Handoff bridge.

    Bridge is NOT:
    - executor;
    - adapter transport;
    - governance;
    - planner;
    - truth authority.

    Bridge only:
    - accepts a RuntimeCoordinationResult;
    - verifies HANDOFF_PREPARED;
    - extracts dispatch target;
    - builds RuntimeHandoffRequest;
    - calls RuntimeHandoffService.prepare_handoff();
    - returns bounded bridge result.
    """

    def __init__(
        self,
        handoff_service: Optional[RuntimeHandoffService] = None,
    ) -> None:
        self.handoff_service = handoff_service or RuntimeHandoffService()

    def bridge_coordination_result(
        self,
        bridge_id: str,
        coordination_result: RuntimeCoordinationResult,
    ) -> RuntimeHandoffBridgeResult:

        trace = list(coordination_result.routing_trace)
        trace.append("handoff_bridge_received_coordination_result")

        if (
            coordination_result.status
            != RuntimeCoordinationStatus.HANDOFF_PREPARED
        ):
            trace.append("handoff_bridge_not_handoff_ready")

            return RuntimeHandoffBridgeResult(
                bridge_id=bridge_id,
                status=RuntimeHandoffBridgeStatus.NOT_HANDOFF_READY,
                coordination_id=coordination_result.coordination_id,
                explanation=(
                    "Coordination result is not HANDOFF_PREPARED. "
                    "Bridge will not create handoff request."
                ),
                routing_trace=trace,
                uncertainty_notes=coordination_result.uncertainty_notes,
            )

        dispatch_decision = coordination_result.dispatch_decision

        if dispatch_decision is None:
            trace.append("handoff_bridge_missing_dispatch_decision")

            return RuntimeHandoffBridgeResult(
                bridge_id=bridge_id,
                status=RuntimeHandoffBridgeStatus.MISSING_DISPATCH_DECISION,
                coordination_id=coordination_result.coordination_id,
                explanation="Coordination result has no dispatch decision.",
                routing_trace=trace,
                uncertainty_notes=coordination_result.uncertainty_notes,
            )

        dispatch_target = dispatch_decision.dispatch_target

        if dispatch_target is None:
            trace.append("handoff_bridge_missing_dispatch_target")

            return RuntimeHandoffBridgeResult(
                bridge_id=bridge_id,
                status=RuntimeHandoffBridgeStatus.MISSING_DISPATCH_TARGET,
                coordination_id=coordination_result.coordination_id,
                explanation="Dispatch decision has no dispatch target.",
                routing_trace=trace,
                uncertainty_notes=coordination_result.uncertainty_notes,
            )

        target_layer = dispatch_target.target_layer

        if target_layer not in TARGET_LAYER_TO_HANDOFF:
            trace.append("handoff_bridge_unsupported_target_layer")

            return RuntimeHandoffBridgeResult(
                bridge_id=bridge_id,
                status=RuntimeHandoffBridgeStatus.UNSUPPORTED_TARGET_LAYER,
                coordination_id=coordination_result.coordination_id,
                explanation=(
                    "Dispatch target layer is not mapped to handoff target."
                ),
                routing_trace=trace,
                uncertainty_notes=coordination_result.uncertainty_notes,
            )

        target_id, capability = TARGET_LAYER_TO_HANDOFF[target_layer]

        trace.append("handoff_bridge_created_handoff_request")
        handoff_request = RuntimeHandoffRequest(
            handoff_id=f"handoff-{bridge_id}",
            direction=RuntimeHandoffDirection.OUTBOUND,
            target_id=target_id,
            requested_capability=capability,
            payload_ref=dispatch_target.payload_ref,
            source_queue_id=dispatch_target.source_queue_id,
            source_coordination_id=coordination_result.coordination_id,
            source_intake_id=dispatch_target.source_intake_id,
            routing_trace=trace,
            uncertainty_notes=coordination_result.uncertainty_notes,
        )


        handoff_decision = self.handoff_service.prepare_handoff(
            handoff_request
        )

        bridge_trace = list(handoff_decision.routing_trace)
        bridge_trace.append("handoff_bridge_received_handoff_decision")

        return RuntimeHandoffBridgeResult(
            bridge_id=bridge_id,
            status=RuntimeHandoffBridgeStatus.HANDOFF_DECISION_READY,
            coordination_id=coordination_result.coordination_id,
            handoff_request=handoff_request,
            handoff_decision=handoff_decision,
            explanation=(
                "Handoff decision prepared. "
                "Bridge did not execute adapter call or verify success."
            ),
            routing_trace=bridge_trace,
            uncertainty_notes=handoff_decision.uncertainty_notes,
        )