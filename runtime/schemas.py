
# runtime/schemas.py

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ----------------------------
# Runtime lifecycle
# ----------------------------

class RuntimeStatus(str, Enum):
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    EXECUTING = "executing"
    AWAITING_HUMAN = "awaiting_human"
    AWAITING_EXTERNAL = "awaiting_external"
    RETRY_PENDING = "retry_pending"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELED = "canceled"
    BLOCKED_BY_GOVERNANCE = "blocked_by_governance"
    BLOCKED_BY_HUMAN = "blocked_by_human"
    NEEDS_REANALYSIS = "needs_reanalysis"


class RuntimeEventType(str, Enum):
    ACTION_RECEIVED = "action_received"
    GOVERNANCE_VERDICT_RECEIVED = "governance_verdict_received"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    HUMAN_RESPONSE_REQUIRED = "human_response_required"
    HUMAN_RESPONSE_RECEIVED = "human_response_received"
    EXTERNAL_RESPONSE_REQUIRED = "external_response_required"
    EXTERNAL_RESPONSE_RECEIVED = "external_response_received"
    RETRY_SCHEDULED = "retry_scheduled"
    DEADLINE_EXPIRED = "deadline_expired"
    REANALYSIS_REQUESTED = "reanalysis_requested"
    CLARIFICATION_REQUESTED = "clarification_requested"


# ----------------------------
# Governance MVP v4.1 snapshot
# Runtime reads this, never mutates it.
# ----------------------------

class GovernanceDecisionStatus(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    NOT_ENOUGH_DATA = "not_enough_data"


class GovernanceVisibilityLevel(str, Enum):
    INTERNAL_ONLY = "internal_only"
    TRUSTED_HUMAN = "trusted_human"
    HUMAN_SAFE = "human_safe"
    PUBLIC_FILTERED = "public_filtered"
    EXTERNAL_MINIMAL = "external_minimal"


class GovernanceTargetAudience(str, Enum):
    INTERNAL_RAY = "internal_ray"
    PRIMARY_HUMAN = "primary_human"
    TRUSTED_PERSON = "trusted_person"
    EXTERNAL_PERSON = "external_person"
    EXTERNAL_AI = "external_ai"
    INTERNET = "internet"
    EMERGENCY_CONTACT = "emergency_contact"


class GovernanceVerdictSnapshot(BaseModel):
    """
    Runtime-side read-only snapshot of GovernanceVerdict.

    IMPORTANT:
    Runtime must NOT collapse these axes into one flat status.
    """
    governance_decision_status: GovernanceDecisionStatus
    governance_visibility_level: GovernanceVisibilityLevel
    governance_target_audience: GovernanceTargetAudience
    governance_confirmation_required: bool = False

    allowed_action_scopes: List[str] = Field(default_factory=list)
    blocked_action_scopes: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    reason_codes: List[str] = Field(default_factory=list)

    external_targets: List[str] = Field(default_factory=list)
    memory_targets: List[str] = Field(default_factory=list)

    trace_id: Optional[str] = None
    policy_sources: List[str] = Field(default_factory=list)
    policy_versions: Dict[str, str] = Field(default_factory=dict)


# ----------------------------
# Runtime action record
# ----------------------------

class RuntimeActionClass(str, Enum):
    INFORMATIONAL = "informational"
    INTERACTION = "interaction"
    SCHEDULING = "scheduling"
    OPERATIONAL = "operational"
    COMMUNICATION = "communication"
    MEMORY = "memory"
    EMERGENCY = "emergency"


class RuntimeRiskLevel(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuntimeActionRecord(BaseModel):
    action_id: str
    schema_version: str = "runtime_action_v0.2"

    action_class: RuntimeActionClass
    risk_level: RuntimeRiskLevel = RuntimeRiskLevel.LOW

    created_by_type: str
    created_by_id: Optional[str] = None

    domain_owner: Optional[str] = None
    assigned_executor: Optional[str] = None

    title: Optional[str] = None
    summary: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

    human_confirmation_status: Optional[str] = None
    human_awareness_status: Optional[str] = None
    human_prohibition_active: bool = False

    governance_verdict: Optional[GovernanceVerdictSnapshot] = None

    runtime_status: RuntimeStatus = RuntimeStatus.NOT_STARTED
    retry_count: int = 0
    max_retries: int = 0

    deadline_at: Optional[str] = None
    expires_at: Optional[str] = None
    timeout_at: Optional[str] = None

    runtime_notes: List[str] = Field(default_factory=list)


# ----------------------------
# Events / execution results
# ----------------------------

class RuntimeEvent(BaseModel):
    event_id: str
    action_id: str
    event_type: RuntimeEventType

    previous_status: Optional[RuntimeStatus] = None
    new_status: Optional[RuntimeStatus] = None

    created_by: str = "runtime"
    created_at: Optional[str] = None

    payload: Dict[str, Any] = Field(default_factory=dict)
    note: Optional[str] = None


class RuntimeExecutionResult(BaseModel):
    action_id: str
    status: RuntimeStatus

    success: bool = False
    blocked: bool = False

    message: Optional[str] = None
    error_code: Optional[str] = None

    events: List[RuntimeEvent] = Field(default_factory=list)

    reanalysis_requested: bool = False
    clarification_requested: bool = False
    awaiting_human: bool = False
    awaiting_external: bool = False