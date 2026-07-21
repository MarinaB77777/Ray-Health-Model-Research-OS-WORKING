from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from runtime.dispatcher.contracts import (
    RuntimeDispatchDecision,
    RuntimeDispatchStatus,
)
from runtime.queue.contracts import RuntimeQueueStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CoordinatorStatus(str, Enum):
    CREATED = "created"
    WAITING_ACQUISITION = "waiting_acquisition"
    WAITING_ANALYSIS = "waiting_analysis"
    WAITING_HUMAN = "waiting_human"
    BLOCKED = "blocked"
    READY_FOR_ROUTING = "ready_for_routing"
    EXPIRED_UNRESOLVED = "expired_unresolved"


class CoordinatorSignalType(str, Enum):
    ACQUISITION_NEEDED = "acquisition_needed"
    ACQUISITION_WAITING = "acquisition_waiting"
    ACQUISITION_RESULT_RECEIVED = "acquisition_result_received"
    ANALYSIS_WAITING = "analysis_waiting"
    HUMAN_INPUT_NEEDED = "human_input_needed"
    RETRY_GUIDANCE_AVAILABLE = "retry_guidance_available"
    ROUTING_READY = "routing_ready"
    BLOCKED = "blocked"
    EXPIRED_UNRESOLVED = "expired_unresolved"


class CoordinatorBlockReason(str, Enum):
    MISSING_ACTION_ID = "missing_action_id"
    MISSING_OPERATION_ID = "missing_operation_id"
    MISSING_REQUIRED_CONTEXT = "missing_required_context"
    ACQUISITION_UNRESOLVED = "acquisition_unresolved"
    ACQUISITION_EXPIRED = "acquisition_expired"
    ANALYSIS_NOT_READY = "analysis_not_ready"
    HUMAN_INPUT_REQUIRED = "human_input_required"
    GOVERNANCE_REQUIRED = "governance_required"
    POLICY_REQUIRED = "policy_required"
    INVALID_TRANSITION = "invalid_transition"
    UNKNOWN_OPERATIONAL_STATE = "unknown_operational_state"


class CoordinatorSignal(BaseModel):
    """
    Bounded operational signal.

    signal ≠ execution
    signal ≠ permission
    signal ≠ truth
    signal ≠ final answer
    """

    signal_type: CoordinatorSignalType
    action_id: str
    operation_id: Optional[str] = None
    acquisition_id: Optional[str] = None
    coordination_group_id: Optional[str] = None
    reason: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_signal(self) -> "CoordinatorSignal":
        if not self.action_id.strip():
            raise ValueError("CoordinatorSignal.action_id must not be empty")

        if (
            self.operation_id is None
            and self.acquisition_id is None
            and self.coordination_group_id is None
            and self.reason is None
            and not self.payload
        ):
            raise ValueError(
                "CoordinatorSignal must include operation_id, acquisition_id, "
                "coordination_group_id, reason, or payload"
            )

        return self


class CoordinatorRecord(BaseModel):
    """
    Runtime Coordinator record.

    action_id owns runtime/task continuity.
    operation_id/acquisition_id owns bounded operational step.
    Coordinator links and routes only.

    This record is NOT:
    - truth storage;
    - memory;
    - Analyst reasoning;
    - Governance verdict;
    - execution result;
    - final task state.
    """

    coordinator_id: str
    action_id: str
    status: CoordinatorStatus = CoordinatorStatus.CREATED

    operation_id: Optional[str] = None
    acquisition_id: Optional[str] = None
    coordination_group_id: Optional[str] = None

    block_reason: Optional[CoordinatorBlockReason] = None
    last_signal: Optional[CoordinatorSignalType] = None

    requires_runtime_action: bool = False
    requires_human_input: bool = False
    requires_governance: bool = False
    requires_analysis: bool = False

    unresolved: bool = False

    metadata: dict[str, Any] = Field(default_factory=dict)
    signals: list[CoordinatorSignal] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    expires_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_record(self) -> "CoordinatorRecord":
        if not self.coordinator_id.strip():
            raise ValueError("CoordinatorRecord.coordinator_id must not be empty")

        if not self.action_id.strip():
            raise ValueError("CoordinatorRecord.action_id must not be empty")

        if self.status == CoordinatorStatus.BLOCKED and self.block_reason is None:
            raise ValueError("BLOCKED CoordinatorRecord requires block_reason")

        if self.status == CoordinatorStatus.EXPIRED_UNRESOLVED and not self.unresolved:
            raise ValueError("EXPIRED_UNRESOLVED requires unresolved=True")

        if self.requires_human_input:
            if (
                self.last_signal != CoordinatorSignalType.HUMAN_INPUT_NEEDED
                and self.block_reason != CoordinatorBlockReason.HUMAN_INPUT_REQUIRED
                and self.status != CoordinatorStatus.WAITING_HUMAN
            ):
                raise ValueError(
                    "requires_human_input=True requires HUMAN_INPUT_NEEDED signal, "
                    "HUMAN_INPUT_REQUIRED block_reason, or WAITING_HUMAN status"
                )

        if self.status == CoordinatorStatus.READY_FOR_ROUTING:
            if self.unresolved:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinatorRecord cannot have unresolved=True"
                )

            if self.requires_human_input:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinatorRecord cannot require human input"
                )

            if self.requires_governance:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinatorRecord cannot require governance"
                )

            if self.requires_analysis:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinatorRecord cannot require analysis"
                )

            if self.block_reason is not None:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinatorRecord cannot have block_reason"
                )

        if self.requires_runtime_action:
            if (
                self.last_signal is None
                and self.block_reason is None
                and self.status == CoordinatorStatus.CREATED
            ):
                raise ValueError(
                    "requires_runtime_action=True requires signal, "
                    "block_reason, or non-CREATED status"
                )

        return self

    def touch(self) -> None:
        self.updated_at = utc_now()


class CoordinationGroup(BaseModel):
    """
    Bounded group of related operation flows.

    Group ≠ truth bundle
    Group ≠ reasoning bundle
    Group ≠ final decision bundle
    Group ≠ task completion bundle
    """

    coordination_group_id: str
    action_id: str

    operation_ids: list[str] = Field(default_factory=list)
    acquisition_ids: list[str] = Field(default_factory=list)

    status: CoordinatorStatus = CoordinatorStatus.CREATED
    unresolved: bool = False
    block_reason: Optional[CoordinatorBlockReason] = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_group(self) -> "CoordinationGroup":
        if not self.coordination_group_id.strip():
            raise ValueError("CoordinationGroup.coordination_group_id must not be empty")

        if not self.action_id.strip():
            raise ValueError("CoordinationGroup.action_id must not be empty")

        if self.status != CoordinatorStatus.CREATED:
            if not self.operation_ids and not self.acquisition_ids:
                raise ValueError(
                    "CoordinationGroup must contain at least one operation_id "
                    "or acquisition_id when status is not CREATED"
                )

        if self.status == CoordinatorStatus.BLOCKED and self.block_reason is None:
            raise ValueError("BLOCKED CoordinationGroup requires block_reason")

        if self.status == CoordinatorStatus.EXPIRED_UNRESOLVED and not self.unresolved:
            raise ValueError(
                "EXPIRED_UNRESOLVED CoordinationGroup requires unresolved=True"
            )

        if self.status == CoordinatorStatus.READY_FOR_ROUTING:
            if self.unresolved:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinationGroup cannot have unresolved=True"
                )

            if self.block_reason is not None:
                raise ValueError(
                    "READY_FOR_ROUTING CoordinationGroup cannot have block_reason"
                )

        return self

    def touch(self) -> None:
        self.updated_at = utc_now()


class CoordinatorOutput(BaseModel):
    """
    Operational output returned to Runtime / authorized layer.

    ready_for_next_route means:
    routing may continue to the next authorized layer.

    It does NOT mean:
    - ready for final answer;
    - verified truth;
    - safe;
    - solved;
    - understood;
    - completed.
    """

    coordinator_id: str
    action_id: str
    status: CoordinatorStatus

    operation_id: Optional[str] = None
    acquisition_id: Optional[str] = None
    coordination_group_id: Optional[str] = None

    ready_for_next_route: bool = False

    signals: list[CoordinatorSignal] = Field(default_factory=list)
    block_reason: Optional[CoordinatorBlockReason] = None

    requires_runtime_action: bool = False
    requires_human_input: bool = False
    requires_governance: bool = False
    requires_analysis: bool = False

    unresolved: bool = False

    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_output(self) -> "CoordinatorOutput":
        if not self.coordinator_id.strip():
            raise ValueError("CoordinatorOutput.coordinator_id must not be empty")

        if not self.action_id.strip():
            raise ValueError("CoordinatorOutput.action_id must not be empty")

        if self.status == CoordinatorStatus.BLOCKED and self.block_reason is None:
            raise ValueError("BLOCKED CoordinatorOutput requires block_reason")

        if self.status == CoordinatorStatus.EXPIRED_UNRESOLVED and not self.unresolved:
            raise ValueError("EXPIRED_UNRESOLVED CoordinatorOutput requires unresolved=True")

        if self.ready_for_next_route:
            if self.status != CoordinatorStatus.READY_FOR_ROUTING:
                raise ValueError(
                    "ready_for_next_route=True requires status READY_FOR_ROUTING"
                )

            if self.unresolved:
                raise ValueError(
                    "ready_for_next_route=True cannot coexist with unresolved=True"
                )

            if self.requires_human_input:
                raise ValueError(
                    "ready_for_next_route=True cannot coexist with "
                    "requires_human_input=True"
                )

            if self.requires_governance:
                raise ValueError(
                    "ready_for_next_route=True cannot coexist with "
                    "requires_governance=True"
                )

            if self.requires_analysis:
                raise ValueError(
                    "ready_for_next_route=True cannot coexist with requires_analysis=True"
                )

            if self.block_reason is not None:
                raise ValueError(
                    "ready_for_next_route=True cannot coexist with block_reason"
                )

        if self.requires_runtime_action:
            if (
                not self.signals
                and self.block_reason is None
                and self.status == CoordinatorStatus.CREATED
            ):
                raise ValueError(
                    "requires_runtime_action=True requires signals, "
                    "block_reason, or non-CREATED status"
                )

        return self


FORBIDDEN_COORDINATOR_MEANING_STATUSES = {
    "understood",
    "solved",
    "decided",
    "safe",
    "important",
    "true",
    "best_action_selected",
    "completed",
    "verified",
    "confirmed_truth",
}


COORDINATOR_BOUNDARY_RULES = {
    "COORDINATOR_ROUTES_OPERATIONAL_STATE_ONLY",
    "COORDINATOR_DOES_NOT_INFER_OPERATIONAL_TRUTH",
    "COORDINATOR_DOES_NOT_CREATE_GOALS",
    "COORDINATOR_DOES_NOT_EXECUTE_ACTIONS",
    "COORDINATOR_DOES_NOT_GRANT_PERMISSION",
    "COORDINATOR_DOES_NOT_REPLACE_RUNTIME",
    "COORDINATOR_DOES_NOT_REPLACE_ANALYST",
    "COORDINATOR_DOES_NOT_REPLACE_GOVERNANCE",
    "COORDINATOR_DOES_NOT_WRITE_MEMORY",
    "READY_FOR_ROUTING_IS_NOT_READY_FOR_FINAL_ANSWER",
    "UNRESOLVED_IS_NOT_SOLVED",
    "SIGNAL_IS_NOT_EXECUTION",
}


class RuntimeCoordinationStatus(str, Enum):
    NO_WORK = "no_work"
    HANDOFF_PREPARED = "handoff_prepared"
    WAITING = "waiting"
    BLOCKED = "blocked"
    FAILED = "failed"


class RuntimeCoordinationReason(str, Enum):
    NO_READY_DISPATCH = "no_ready_dispatch"
    DISPATCH_SELECTED = "dispatch_selected"
    DISPATCH_NOT_READY = "dispatch_not_ready"
    DISPATCH_BLOCKED = "dispatch_blocked"
    INVALID_DISPATCH_STATE = "invalid_dispatch_state"


class RuntimeCoordinationResult(BaseModel):
    coordination_id: str

    status: RuntimeCoordinationStatus
    reason: RuntimeCoordinationReason

    dispatch_decision: Optional[RuntimeDispatchDecision] = None
    next_queue_status: Optional[RuntimeQueueStatus] = None

    explanation: Optional[str] = None
    routing_trace: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)

    preserve_uncertainty: bool = True
    created_at: datetime = Field(default_factory=utc_now)


def coordination_result_from_dispatch(
    coordination_id: str,
    dispatch_decision: RuntimeDispatchDecision,
) -> RuntimeCoordinationResult:
    trace = list(dispatch_decision.routing_trace)
    trace.append("coordinator_received_dispatch_decision")

    if dispatch_decision.dispatch_status == RuntimeDispatchStatus.NO_READY_ITEMS:
        return RuntimeCoordinationResult(
            coordination_id=coordination_id,
            status=RuntimeCoordinationStatus.NO_WORK,
            reason=RuntimeCoordinationReason.NO_READY_DISPATCH,
            dispatch_decision=dispatch_decision,
            explanation="No ready dispatch available for coordination.",
            routing_trace=trace,
            uncertainty_notes=dispatch_decision.uncertainty_notes,
        )

    if dispatch_decision.dispatch_status == RuntimeDispatchStatus.SELECTED:
        trace.append("coordinator_prepared_handoff")

        return RuntimeCoordinationResult(
            coordination_id=coordination_id,
            status=RuntimeCoordinationStatus.HANDOFF_PREPARED,
            reason=RuntimeCoordinationReason.DISPATCH_SELECTED,
            dispatch_decision=dispatch_decision,
            next_queue_status=RuntimeQueueStatus.IN_PROGRESS,
            explanation=(
                "Bounded operational handoff prepared. "
                "This does not mean execution or success."
            ),
            routing_trace=trace,
            uncertainty_notes=dispatch_decision.uncertainty_notes,
        )

    if dispatch_decision.dispatch_status == RuntimeDispatchStatus.BLOCKED:
        return RuntimeCoordinationResult(
            coordination_id=coordination_id,
            status=RuntimeCoordinationStatus.BLOCKED,
            reason=RuntimeCoordinationReason.DISPATCH_BLOCKED,
            dispatch_decision=dispatch_decision,
            explanation="Dispatch is blocked and cannot be coordinated.",
            routing_trace=trace,
            uncertainty_notes=dispatch_decision.uncertainty_notes,
        )

    if dispatch_decision.dispatch_status == RuntimeDispatchStatus.NOT_READY:
        return RuntimeCoordinationResult(
            coordination_id=coordination_id,
            status=RuntimeCoordinationStatus.WAITING,
            reason=RuntimeCoordinationReason.DISPATCH_NOT_READY,
            dispatch_decision=dispatch_decision,
            explanation="Dispatch is not ready for coordination.",
            routing_trace=trace,
            uncertainty_notes=dispatch_decision.uncertainty_notes,
        )

    return RuntimeCoordinationResult(
        coordination_id=coordination_id,
        status=RuntimeCoordinationStatus.FAILED,
        reason=RuntimeCoordinationReason.INVALID_DISPATCH_STATE,
        dispatch_decision=dispatch_decision,
        explanation="Invalid dispatch state for coordination.",
        routing_trace=trace,
        uncertainty_notes=dispatch_decision.uncertainty_notes,
    )