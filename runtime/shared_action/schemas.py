from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ActionType(str, Enum):
    human_task = "human_task"
    ray_support_task = "ray_support_task"
    clarification_request = "clarification_request"
    predictive_analysis = "predictive_analysis"
    governance_check = "governance_check"
    domain_delegation = "domain_delegation"
    reminder = "reminder"
    workflow_step = "workflow_step"
    external_request = "external_request"
    communication_action = "communication_action"
    system_maintenance = "system_maintenance"


class ActionSource(str, Enum):
    human = "human"
    runtime = "runtime"
    domain_ray = "domain_ray"
    analyst_ray = "analyst_ray"
    governance = "governance"
    predictive_layer = "predictive_layer"
    scheduler = "scheduler"
    external_system = "external_system"
    sensor_layer = "sensor_layer"


class OwnerType(str, Enum):
    human = "human"
    runtime = "runtime"
    domain_ray = "domain_ray"
    analyst_ray = "analyst_ray"
    shared = "shared"
    unassigned = "unassigned"


class ActionStatus(str, Enum):
    candidate = "candidate"
    proposed = "proposed"
    accepted = "accepted"
    assigned = "assigned"
    in_progress = "in_progress"
    awaiting_human = "awaiting_human"
    awaiting_human_confirmation = "awaiting_human_confirmation"
    awaiting_governance = "awaiting_governance"
    blocked = "blocked"
    completed = "completed"
    canceled = "canceled"
    expired = "expired"
    forbidden_by_human = "forbidden_by_human"
    duplicate_detected = "duplicate_detected"
    archived = "archived"


class BlockReason(str, Enum):
    governance = "governance"
    runtime = "runtime"
    dependency = "dependency"
    external = "external"
    human = "human"
    resource_limit = "resource_limit"
    uncertainty = "uncertainty"
    safety = "safety"


class Priority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"
    emergency = "emergency"


class VisibilityScope(str, Enum):
    internal_only = "internal_only"
    trusted_human = "trusted_human"
    human_safe = "human_safe"
    public_filtered = "public_filtered"
    external_minimal = "external_minimal"


class VerificationStatus(str, Enum):
    verified = "verified"
    partially_verified = "partially_verified"
    estimated = "estimated"
    unverified = "unverified"
    unknown = "unknown"
    conflicting = "conflicting"


class NotificationState(str, Enum):
    not_needed = "not_needed"
    pending = "pending"
    batched = "batched"
    sent = "sent"
    acknowledged = "acknowledged"
    dismissed = "dismissed"
    expired = "expired"
    suppressed = "suppressed"


class InterruptionCost(str, Enum):
    minimal = "minimal"
    low = "low"
    moderate = "moderate"
    high = "high"
    critical_only = "critical_only"


class SharedActionRecord(BaseModel):
    """
    Shared Action Table record.

    Coordination layer only.
    Not memory, not reasoning, not Inner Core, not universal truth.
    """

    # Identity
    action_id: str
    parent_action_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    expires_at: Optional[datetime] = None

    # Type / routing
    action_type: ActionType
    domain: Optional[str] = None
    source: ActionSource
    source_ref_id: Optional[str] = None

    # Ownership
    owner_type: OwnerType = OwnerType.unassigned
    owner_id: Optional[str] = None

    # Lifecycle
    status: ActionStatus
    block_reason: Optional[BlockReason] = None
    requires_confirmation: bool = False
    forbidden_by_human: bool = False

    # Coordination
    priority: Priority = Priority.normal
    deadline: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list)
    active_modes: List[str] = Field(default_factory=list)
    active_profiles: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None

    # Governance surface
    allowed: Optional[bool] = None
    restricted: bool = False
    visibility_scope: VisibilityScope = VisibilityScope.internal_only
    governance_verdict_ref_id: Optional[str] = None

    # Predictive bridge
    predictive_task_id: Optional[str] = None
    option_group_id: Optional[str] = None
    selected_option: Optional[str] = None
    analysis_ref_id: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.unknown

    # Communication surface
    interruption_cost: InterruptionCost = InterruptionCost.low
    batched_group: Optional[str] = None
    notification_state: NotificationState = NotificationState.not_needed
    communication_ref_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_invariants(self) -> "SharedActionRecord":
        if self.status == ActionStatus.assigned:
            if self.owner_type == OwnerType.unassigned or not self.owner_id:
                raise ValueError(
                    "assigned status requires owner_type != unassigned and valid owner_id"
                )

        if self.status == ActionStatus.in_progress:
            if self.owner_type == OwnerType.unassigned or not self.owner_id:
                raise ValueError(
                    "in_progress status requires owner_type != unassigned and valid owner_id"
                )

        if self.status == ActionStatus.blocked and self.block_reason is None:
            raise ValueError("blocked status requires block_reason")

        if self.status != ActionStatus.blocked and self.block_reason is not None:
            raise ValueError("block_reason is only allowed when status == blocked")

        if self.status == ActionStatus.forbidden_by_human:
            if not self.forbidden_by_human:
                raise ValueError(
                    "forbidden_by_human status requires forbidden_by_human=True"
                )

        if self.forbidden_by_human and self.status != ActionStatus.forbidden_by_human:
            raise ValueError(
                "forbidden_by_human=True requires status == forbidden_by_human"
            )

        if self.relevance_score is not None:
            if not 0.0 <= self.relevance_score <= 1.0:
                raise ValueError("relevance_score must be between 0.0 and 1.0")

        return self