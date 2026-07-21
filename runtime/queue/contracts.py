from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime, timezone

from runtime.intake.contracts import RuntimeTargetLayer


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeQueueStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    WAITING_GOVERNANCE = "waiting_governance"
    WAITING_HUMAN_CONFIRMATION = "waiting_human_confirmation"
    WAITING_CLARIFICATION = "waiting_clarification"
    WAITING_DEPENDENCY = "waiting_dependency"
    DEFERRED = "deferred"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class RuntimeQueuePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class RuntimeQueueItemType(str, Enum):
    INTAKE_ROUTE = "intake_route"
    CLARIFICATION_REQUEST = "clarification_request"
    GOVERNANCE_REVIEW = "governance_review"
    ANALYZER_REQUEST = "analyzer_request"
    ANALYST_REQUEST = "analyst_request"
    COMMUNICATION_TRIGGER = "communication_trigger"
    EXECUTION_PREPARATION = "execution_preparation"
    COORDINATION_STEP = "coordination_step"


class RuntimeQueueBlockReason(str, Enum):
    GOVERNANCE_REQUIRED = "governance_required"
    HUMAN_CONFIRMATION_REQUIRED = "human_confirmation_required"
    CLARIFICATION_REQUIRED = "clarification_required"
    DEPENDENCY_WAIT = "dependency_wait"
    EXPIRED = "expired"
    CANCELLED_BY_HUMAN = "cancelled_by_human"
    AUTHORITY_BLOCKED = "authority_blocked"
    INVALID_STATE = "invalid_state"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class RuntimeQueueItem(BaseModel):
    queue_id: str

    item_type: RuntimeQueueItemType
    status: RuntimeQueueStatus = RuntimeQueueStatus.PENDING
    priority: RuntimeQueuePriority = RuntimeQueuePriority.NORMAL

    source_intake_id: Optional[str] = None
    related_action_id: Optional[str] = None
    related_task_id: Optional[str] = None
    parent_queue_id: Optional[str] = None

    target_layer: Optional[RuntimeTargetLayer] = None
    target_domain: Optional[str] = None

    payload_ref: Optional[str] = None

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    ready_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    retry_count: int = 0
    max_retries: int = 0

    block_reason: Optional[RuntimeQueueBlockReason] = None
    waiting_for: Optional[str] = None

    explanation: Optional[str] = None
    uncertainty_notes: list[str] = Field(default_factory=list)
    routing_trace: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_queue_invariants(self) -> "RuntimeQueueItem":
        if (
            self.status == RuntimeQueueStatus.BLOCKED
            and self.block_reason is None
        ):
            raise ValueError(
                "BLOCKED queue item requires block_reason"
            )

        if (
            self.status != RuntimeQueueStatus.BLOCKED
            and self.block_reason is not None
        ):
            if self.status not in {
                RuntimeQueueStatus.WAITING_GOVERNANCE,
                RuntimeQueueStatus.WAITING_HUMAN_CONFIRMATION,
                RuntimeQueueStatus.WAITING_CLARIFICATION,
                RuntimeQueueStatus.WAITING_DEPENDENCY,
                RuntimeQueueStatus.EXPIRED,
                RuntimeQueueStatus.CANCELLED,
            }:
                raise ValueError(
                    "block_reason is only allowed for blocked, waiting, "
                    "expired, or cancelled queue items"
                )

        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")

        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")

        if self.retry_count > self.max_retries:
            raise ValueError(
                "retry_count must not exceed max_retries"
            )

        return self

    def update_timestamp(self) -> None:
        self.updated_at = utc_now()

    def is_terminal(self) -> bool:
        return self.status in {
            RuntimeQueueStatus.COMPLETED,
            RuntimeQueueStatus.EXPIRED,
            RuntimeQueueStatus.CANCELLED,
        }

    def is_blocked(self) -> bool:
        return self.status == RuntimeQueueStatus.BLOCKED

    def is_waiting(self) -> bool:
        return self.status in {
            RuntimeQueueStatus.WAITING_GOVERNANCE,
            RuntimeQueueStatus.WAITING_HUMAN_CONFIRMATION,
            RuntimeQueueStatus.WAITING_CLARIFICATION,
            RuntimeQueueStatus.WAITING_DEPENDENCY,
            RuntimeQueueStatus.DEFERRED,
        }

    def can_be_processed(self, now: Optional[datetime] = None) -> bool:
        now = now or utc_now()

        if self.is_terminal():
            return False

        if self.is_blocked():
            return False

        if self.status not in {
            RuntimeQueueStatus.PENDING,
            RuntimeQueueStatus.READY,
        }:
            return False

        if self.expires_at is not None and now >= self.expires_at:
            return False

        if self.ready_at is not None and now < self.ready_at:
            return False

        return True


class RuntimeQueueDecision(BaseModel):
    queue_id: str

    accepted: bool
    status: RuntimeQueueStatus

    block_reason: Optional[RuntimeQueueBlockReason] = None
    explanation: Optional[str] = None

    requires_governance: bool = False
    requires_human_confirmation: bool = False
    requires_clarification: bool = False
    waiting_for_dependency: bool = False

    preserve_uncertainty: bool = True

    decided_at: datetime = Field(default_factory=utc_now)


class RuntimeQueueInvariant(BaseModel):
    name: str
    description: str
    preserved: bool = True


RUNTIME_QUEUE_INVARIANTS: list[RuntimeQueueInvariant] = [
    RuntimeQueueInvariant(
        name="queue_is_not_planner",
        description="Runtime Queue does not perform reasoning or planning.",
    ),
    RuntimeQueueInvariant(
        name="queue_is_not_governance",
        description="Queue status does not grant permissions.",
    ),
    RuntimeQueueInvariant(
        name="queued_is_not_approved",
        description=(
            "Being queued does not mean approved, verified, or executable."
        ),
    ),
    RuntimeQueueInvariant(
        name="ready_is_not_executed",
        description=(
            "Ready state means operationally ready for next step, "
            "not executed."
        ),
    ),
    RuntimeQueueInvariant(
        name="completed_is_not_successful_outcome",
        description=(
            "Completed queue handling does not prove real-world success."
        ),
    ),
    RuntimeQueueInvariant(
        name="priority_is_operational_not_psychological",
        description=(
            "Queue priority is operational scheduling priority, "
            "not hidden human profiling."
        ),
    ),
]