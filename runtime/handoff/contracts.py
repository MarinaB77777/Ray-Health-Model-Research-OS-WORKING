from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone

from runtime.handoff.registry import (
    HandoffCapability,
    HandoffBoundaryRule,
    HandoffTruthLimit,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeHandoffDirection(str, Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class RuntimeHandoffStatus(str, Enum):
    PREPARED = "prepared"
    REQUIRES_GOVERNANCE = "requires_governance"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    BLOCKED = "blocked"
    TARGET_UNAVAILABLE = "target_unavailable"
    TARGET_NOT_FOUND = "target_not_found"
    CAPABILITY_NOT_DECLARED = "capability_not_declared"
    INVALID_REQUEST = "invalid_request"


class RuntimeHandoffRequest(BaseModel):
    handoff_id: str
    direction: RuntimeHandoffDirection

    target_id: str
    requested_capability: HandoffCapability

    payload_ref: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)

    source_queue_id: Optional[str] = None
    source_coordination_id: Optional[str] = None
    source_intake_id: Optional[str] = None

    requires_governance: bool = False
    requires_confirmation: bool = False

    routing_trace: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)


class RuntimeHandoffDecision(BaseModel):
    handoff_id: str
    status: RuntimeHandoffStatus

    target_id: Optional[str] = None
    requested_capability: Optional[HandoffCapability] = None

    requires_governance: bool = False
    requires_confirmation: bool = False

    visible_boundary_rules: list[HandoffBoundaryRule] = Field(default_factory=list)
    truth_limits: list[HandoffTruthLimit] = Field(default_factory=list)

    explanation: Optional[str] = None

    routing_trace: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)

    preserve_uncertainty: bool = True
    decided_at: datetime = Field(default_factory=utc_now)


class RuntimeHandoffResult(BaseModel):
    handoff_id: str
    direction: RuntimeHandoffDirection

    status: RuntimeHandoffStatus

    decision: RuntimeHandoffDecision

    adapter_response_ref: Optional[str] = None
    adapter_response_payload: dict[str, Any] = Field(default_factory=dict)

    result_is_verified_reality: bool = False
    result_is_execution_success: bool = False
    result_is_ray_truth: bool = False

    routing_trace: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)


class RuntimeHandoffInvariant(BaseModel):
    name: str
    description: str
    preserved: bool = True


RUNTIME_HANDOFF_INVARIANTS: list[RuntimeHandoffInvariant] = [
    RuntimeHandoffInvariant(
        name="handoff_is_bidirectional",
        description=(
            "Handoff supports outbound Runtime-to-target flow and inbound "
            "target-response-to-Runtime-boundary flow."
        ),
    ),
    RuntimeHandoffInvariant(
        name="handoff_registry_is_not_governance",
        description=(
            "Registry checks target/capability/boundary visibility, "
            "but does not grant permission or approve execution."
        ),
    ),
    RuntimeHandoffInvariant(
        name="handoff_is_not_execution",
        description="Prepared or attempted handoff does not execute actions.",
    ),
    RuntimeHandoffInvariant(
        name="handoff_result_is_operational_only",
        description=(
            "Handoff allowed/prepared/sent is not success, verified truth, "
            "real-world outcome, human agreement, or memory authority."
        ),
    ),
    RuntimeHandoffInvariant(
        name="adapter_response_is_not_verified_reality",
        description=(
            "Adapter responses must return through Runtime boundary and must "
            "not be promoted to verified reality automatically."
        ),
    ),
    RuntimeHandoffInvariant(
        name="truth_limits_must_be_preserved",
        description="Truth limits attached by registry must remain visible.",
    ),
]