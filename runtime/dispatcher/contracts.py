from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from runtime.queue.contracts import (
    RuntimeQueueItem,
    RuntimeQueueItemType,
)

from runtime.intake.contracts import RuntimeTargetLayer


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeDispatchStatus(str, Enum):
    SELECTED = "selected"
    NOT_READY = "not_ready"
    BLOCKED = "blocked"
    NO_READY_ITEMS = "no_ready_items"
    INVALID_QUEUE_STATE = "invalid_queue_state"


class RuntimeDispatchReason(str, Enum):
    READY_FOR_HANDOFF = "ready_for_handoff"
    QUEUE_ITEM_NOT_PROCESSABLE = "queue_item_not_processable"
    QUEUE_ITEM_BLOCKED = "queue_item_blocked"
    QUEUE_ITEM_WAITING = "queue_item_waiting"
    QUEUE_ITEM_TERMINAL = "queue_item_terminal"
    NO_AVAILABLE_READY_ITEMS = "no_available_ready_items"
    MISSING_TARGET_LAYER = "missing_target_layer"
    INVALID_TARGET_LAYER = "invalid_target_layer"


class RuntimeDispatchTarget(BaseModel):
    target_layer: RuntimeTargetLayer
    target_domain: Optional[str] = None
    item_type: RuntimeQueueItemType

    source_queue_id: str
    source_intake_id: Optional[str] = None
    related_action_id: Optional[str] = None
    related_task_id: Optional[str] = None

    payload_ref: Optional[str] = None


class RuntimeDispatchDecision(BaseModel):
    queue_id: Optional[str] = None

    dispatch_status: RuntimeDispatchStatus
    dispatch_reason: RuntimeDispatchReason

    dispatch_target: Optional[RuntimeDispatchTarget] = None

    explanation: Optional[str] = None
    uncertainty_notes: list[str] = Field(default_factory=list)
    routing_trace: list[str] = Field(default_factory=list)

    preserve_uncertainty: bool = True
    decided_at: datetime = Field(default_factory=utc_now)


class RuntimeDispatcherInvariant(BaseModel):
    name: str
    description: str
    preserved: bool = True


RUNTIME_DISPATCHER_INVARIANTS: list[RuntimeDispatcherInvariant] = [
    RuntimeDispatcherInvariant(
        name="dispatcher_is_not_planner",
        description=(
            "Dispatcher selects operational handoff targets; "
            "it does not reason or plan."
        ),
    ),
    RuntimeDispatcherInvariant(
        name="dispatcher_is_not_executor",
        description="Dispatching does not execute real-world actions.",
    ),
    RuntimeDispatcherInvariant(
        name="dispatcher_is_not_governance",
        description=(
            "Dispatcher does not grant permissions or override governance."
        ),
    ),
    RuntimeDispatcherInvariant(
        name="dispatch_is_not_success",
        description=(
            "A dispatched item only means handoff was selected, "
            "not that outcome succeeded."
        ),
    ),
    RuntimeDispatcherInvariant(
        name="no_ready_item_means_no_dispatch",
        description=(
            "Dispatcher must not invent work when no processable queue item exists."
        ),
    ),
]


def can_dispatch_queue_item(
    item: RuntimeQueueItem,
    now: Optional[datetime] = None,
) -> bool:
    return item.can_be_processed(now)


def build_dispatch_target(
    item: RuntimeQueueItem,
) -> Optional[RuntimeDispatchTarget]:

    if item.target_layer is None:
        return None

    return RuntimeDispatchTarget(
        target_layer=item.target_layer,
        target_domain=item.target_domain,
        item_type=item.item_type,
        source_queue_id=item.queue_id,
        source_intake_id=item.source_intake_id,
        related_action_id=item.related_action_id,
        related_task_id=item.related_task_id,
        payload_ref=item.payload_ref,
    )


def dispatch_decision_from_queue_item(
    item: RuntimeQueueItem,
    now: Optional[datetime] = None,
) -> RuntimeDispatchDecision:

    now = now or utc_now()

    if item.is_terminal():
        return RuntimeDispatchDecision(
            queue_id=item.queue_id,
            dispatch_status=RuntimeDispatchStatus.NOT_READY,
            dispatch_reason=RuntimeDispatchReason.QUEUE_ITEM_TERMINAL,
            explanation="Terminal queue item cannot be dispatched.",
            routing_trace=item.routing_trace,
            uncertainty_notes=item.uncertainty_notes,
        )

    if item.is_blocked():
        return RuntimeDispatchDecision(
            queue_id=item.queue_id,
            dispatch_status=RuntimeDispatchStatus.BLOCKED,
            dispatch_reason=RuntimeDispatchReason.QUEUE_ITEM_BLOCKED,
            explanation="Blocked queue item cannot be dispatched.",
            routing_trace=item.routing_trace,
            uncertainty_notes=item.uncertainty_notes,
        )

    if item.is_waiting():
        return RuntimeDispatchDecision(
            queue_id=item.queue_id,
            dispatch_status=RuntimeDispatchStatus.NOT_READY,
            dispatch_reason=RuntimeDispatchReason.QUEUE_ITEM_WAITING,
            explanation="Waiting queue item cannot be dispatched.",
            routing_trace=item.routing_trace,
            uncertainty_notes=item.uncertainty_notes,
        )

    if not item.can_be_processed(now):
        return RuntimeDispatchDecision(
            queue_id=item.queue_id,
            dispatch_status=RuntimeDispatchStatus.NOT_READY,
            dispatch_reason=RuntimeDispatchReason.QUEUE_ITEM_NOT_PROCESSABLE,
            explanation="Queue item is not processable at this time.",
            routing_trace=item.routing_trace,
            uncertainty_notes=item.uncertainty_notes,
        )

    target = build_dispatch_target(item)

    if target is None:
        return RuntimeDispatchDecision(
            queue_id=item.queue_id,
            dispatch_status=RuntimeDispatchStatus.INVALID_QUEUE_STATE,
            dispatch_reason=RuntimeDispatchReason.MISSING_TARGET_LAYER,
            explanation=(
                "Dispatch target cannot be built without target_layer."
            ),
            routing_trace=item.routing_trace,
            uncertainty_notes=item.uncertainty_notes,
        )

    return RuntimeDispatchDecision(
        queue_id=item.queue_id,
        dispatch_status=RuntimeDispatchStatus.SELECTED,
        dispatch_reason=RuntimeDispatchReason.READY_FOR_HANDOFF,
        dispatch_target=target,
        explanation="Queue item selected for bounded operational handoff.",
        routing_trace=item.routing_trace,
        uncertainty_notes=item.uncertainty_notes,
    )