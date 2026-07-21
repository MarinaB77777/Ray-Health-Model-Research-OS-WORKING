from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IntakeSourceType(str, Enum):
    HUMAN_CHAT = "human_chat"
    HUMAN_VOICE = "human_voice"
    MICROPHONE = "microphone"
    SMS = "sms"
    EMAIL = "email"
    FILE = "file"
    SENSOR_EVENT = "sensor_event"
    ACQUISITION_REQUEST = "acquisition_request"
    EXTERNAL_PROCESSING_RESULT = "external_processing_result"
    SYSTEM_EVENT = "system_event"
    DOMAIN_RAY = "domain_ray"
    ANALYST = "analyst"
    ANALYZER = "analyzer"
    GOVERNANCE = "governance"


class IntakePayloadType(str, Enum):
    MESSAGE = "message"
    TASK_REQUEST = "task_request"
    CLARIFICATION_RESPONSE = "clarification_response"
    FILE_UPLOAD = "file_upload"
    SENSOR_SIGNAL = "sensor_signal"
    EXTERNAL_RESULT = "external_result"
    SYSTEM_NOTIFICATION = "system_notification"
    ACQUISITION_SIGNAL = "acquisition_signal"
    UNKNOWN = "unknown"


class IntakeTrustStatus(str, Enum):
    UNVERIFIED = "unverified"
    PARTIALLY_VERIFIED = "partially_verified"
    VERIFIED = "verified"
    CONFLICTING = "conflicting"
    STALE = "stale"
    REJECTED = "rejected"


class IntakeLifecycleStatus(str, Enum):
    RECEIVED = "received"
    NORMALIZED = "normalized"
    ROUTED = "routed"
    BLOCKED = "blocked"
    NEEDS_CLARIFICATION = "needs_clarification"
    EXPIRED = "expired"
    DISCARDED = "discarded"


class RuntimeAuthorityBoundary(str, Enum):
    INTAKE_ONLY = "intake_only"
    ROUTING_ALLOWED = "routing_allowed"
    COORDINATION_ALLOWED = "coordination_allowed"
    EXECUTION_PREPARATION_ALLOWED = "execution_preparation_allowed"
    REQUIRES_GOVERNANCE = "requires_governance"
    REQUIRES_HUMAN_CONFIRMATION = "requires_human_confirmation"
    BLOCKED = "blocked"


class RuntimeTargetLayer(str, Enum):
    RUNTIME = "runtime"
    ANALYZER = "analyzer"
    ANALYST = "analyst"
    GOVERNANCE = "governance"
    COMMUNICATOR = "communicator"
    DOMAIN_RAY = "domain_ray"
    TEMPORARY_MEMORY = "temporary_memory"
    SHARED_ACTION = "shared_action"


class IntakeSourceMetadata(BaseModel):
    source_type: IntakeSourceType

    source_id: Optional[str] = None
    channel_id: Optional[str] = None
    device_id: Optional[str] = None
    human_id: Optional[str] = None

    received_at: datetime = Field(default_factory=utc_now)
    source_timestamp: Optional[datetime] = None

    reliability_note: Optional[str] = None
    freshness_note: Optional[str] = None


class IntakeGovernanceSurface(BaseModel):
    contains_personal_data: bool = False
    contains_sensitive_data: bool = False

    external_exposure_requested: bool = False
    memory_write_requested: bool = False
    execution_requested: bool = False

    human_confirmation_required: bool = False
    governance_required: bool = False

    allowed_scope: Optional[str] = None
    restriction_reason: Optional[str] = None


class IntakeRoutingHints(BaseModel):
    target_domain: Optional[str] = None
    target_layer: Optional[RuntimeTargetLayer] = None

    suggested_priority: Optional[str] = None

    requires_analyzer: bool = False
    requires_analyst: bool = False
    requires_governance: bool = False
    requires_communicator: bool = False


class IntakeEvent(BaseModel):
    intake_id: str

    payload_type: IntakePayloadType = IntakePayloadType.UNKNOWN
    payload: dict[str, Any] = Field(default_factory=dict)

    source: IntakeSourceMetadata

    trust_status: IntakeTrustStatus = IntakeTrustStatus.UNVERIFIED
    lifecycle_status: IntakeLifecycleStatus = (
        IntakeLifecycleStatus.RECEIVED
    )

    routing_hints: IntakeRoutingHints = Field(
        default_factory=IntakeRoutingHints
    )

    governance_surface: IntakeGovernanceSurface = Field(
        default_factory=IntakeGovernanceSurface
    )

    authority_boundary: RuntimeAuthorityBoundary = (
        RuntimeAuthorityBoundary.INTAKE_ONLY
    )

    uncertainty_notes: list[str] = Field(default_factory=list)
    conflict_notes: list[str] = Field(default_factory=list)

    parent_intake_id: Optional[str] = None
    related_action_id: Optional[str] = None
    related_task_id: Optional[str] = None

    expires_at: Optional[datetime] = None

    def is_trusted_reality(self) -> bool:
        """
        Intake is not truth by default.
        """
        return self.trust_status == IntakeTrustStatus.VERIFIED

    def requires_boundary_check(self) -> bool:
        return (
            self.governance_surface.governance_required
            or self.governance_surface.human_confirmation_required
            or self.governance_surface.execution_requested
            or self.governance_surface.external_exposure_requested
            or self.governance_surface.memory_write_requested
            or self.authority_boundary in {
                RuntimeAuthorityBoundary.REQUIRES_GOVERNANCE,
                RuntimeAuthorityBoundary.REQUIRES_HUMAN_CONFIRMATION,
                RuntimeAuthorityBoundary.BLOCKED,
            }
        )

    def can_runtime_route(self) -> bool:

        if self.lifecycle_status in {
            IntakeLifecycleStatus.BLOCKED,
            IntakeLifecycleStatus.EXPIRED,
            IntakeLifecycleStatus.DISCARDED,
        }:
            return False

        return self.authority_boundary in {
            RuntimeAuthorityBoundary.ROUTING_ALLOWED,
            RuntimeAuthorityBoundary.COORDINATION_ALLOWED,
            RuntimeAuthorityBoundary.EXECUTION_PREPARATION_ALLOWED,
        }


class IntakeNormalizationResult(BaseModel):
    intake_id: str
    normalized: bool

    lifecycle_status: IntakeLifecycleStatus
    trust_status: IntakeTrustStatus

    normalized_payload: dict[str, Any] = Field(
        default_factory=dict
    )

    warnings: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    conflict_notes: list[str] = Field(default_factory=list)

    routing_hints: IntakeRoutingHints = Field(
        default_factory=IntakeRoutingHints
    )

    governance_surface: IntakeGovernanceSurface = Field(
        default_factory=IntakeGovernanceSurface
    )