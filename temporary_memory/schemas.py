from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4


WORKING_MEMORY_CLASS = "working_operational"
FORBIDDEN_PAYLOAD_KEYS = {
    "heart_of_ray",
    "heart_of_human",
    "raw_inner_core",
    "inner_core_payload",
    "ray_self_health_authority_raw",
}


class TemporaryMemoryStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    UNRESOLVED = "unresolved"
    EXPIRED = "expired"
    DO_NOT_USE = "do_not_use"
    INVALIDATED = "invalidated"
    DELETED = "deleted"


class TemporaryMemoryScope(str, Enum):
    SESSION = "session"
    TASK = "task"
    RUNTIME = "runtime"
    PLANNER = "planner"


class TemporaryMemorySource(str, Enum):
    EXTERNAL_CORE = "external_core"
    ANALYZER = "analyzer"
    ANALYST = "analyst"
    GOVERNANCE = "governance"
    RUNTIME = "runtime"
    PLANNER = "planner"
    COMMUNICATION = "communication"
    CALIBRATION = "calibration"
    DOMAIN_RAY = "domain_ray"
    RAY_SELF_HEALTH = "ray_self_health"


class TemporaryMemoryType(str, Enum):
    NEXT_QUESTION = "next_question"
    BLOCKER = "blocker"
    AWAITING_HUMAN = "awaiting_human"
    RETRY_CONTEXT = "retry_context"
    UNCERTAINTY_FLAG = "uncertainty_flag"
    FORECAST_RESTRICTION = "forecast_restriction"
    DIALOGUE_CONTEXT = "dialogue_context"
    PLANNER_NOTE = "planner_note"
    RUNTIME_COORDINATION = "runtime_coordination"
    WARNING = "warning"
    SAFETY_ROUTING_FLAG = "safety_routing_flag"
    CALIBRATION_NOTE = "calibration_note"


class TemporaryMemorySensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MemoryTruthType(str, Enum):
    OPERATIONAL_STATE = "operational_state"
    HUMAN_DECLARATION = "human_declaration"
    HUMAN_PERMISSION = "human_permission"
    OBSERVATION = "observation"
    EXTERNAL_CLAIM = "external_claim"
    VERIFIED_EXTERNAL_FACT = "verified_external_fact"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    PREDICTION = "prediction"
    PROJECTION_DERIVED = "projection_derived"
    CALIBRATION_CANDIDATE = "calibration_candidate"


class MemoryFreshness(str, Enum):
    CURRENT = "current"
    REVIEW_REQUIRED = "review_required"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass
class TemporaryMemoryRecord:
    """Backward-compatible record for Working / Operational Memory only.

    The package name `temporary_memory` is retained to avoid breaking existing
    imports. It is not a universal Ray memory and cannot represent Heart content,
    long-term semantic/episodic/relational memory, or raw Self-Health authority.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    record_type: TemporaryMemoryType = TemporaryMemoryType.RUNTIME_COORDINATION
    status: TemporaryMemoryStatus = TemporaryMemoryStatus.ACTIVE
    scope: TemporaryMemoryScope = TemporaryMemoryScope.SESSION
    source: TemporaryMemorySource = TemporaryMemorySource.RUNTIME

    session_id: Optional[str] = None
    task_id: Optional[str] = None
    related_action_id: Optional[str] = None
    related_verdict_id: Optional[str] = None

    memory_class: str = WORKING_MEMORY_CLASS
    truth_type: MemoryTruthType = MemoryTruthType.OPERATIONAL_STATE
    subject: str = "system"
    purpose: str = "operational_coordination"
    provenance_refs: tuple[str, ...] = ()
    freshness: MemoryFreshness = MemoryFreshness.CURRENT
    confidence: Optional[float] = None

    # Operational payload only. Raw Inner Core content is forbidden.
    payload: dict[str, Any] = field(default_factory=dict)

    payload_summary: Optional[str] = None
    retention_reason: Optional[str] = None
    # Legacy field retained for serialization/API compatibility. True is rejected:
    # Working Memory cannot self-promote into another memory class or Heart.
    promotion_allowed: bool = False
    sensitivity_level: TemporaryMemorySensitivity = TemporaryMemorySensitivity.MEDIUM

    priority: int = 0
    tags: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    deletion_reason: Optional[str] = None

    def validate(self) -> None:
        if self.memory_class != WORKING_MEMORY_CLASS:
            raise PermissionError("TEMPORARY_MEMORY_IS_WORKING_MEMORY_ONLY")
        if self.promotion_allowed:
            raise PermissionError("WORKING_MEMORY_CANNOT_SELF_PROMOTE")
        if not self.subject.strip() or not self.purpose.strip():
            raise ValueError("WORKING_MEMORY_SUBJECT_AND_PURPOSE_REQUIRED")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("WORKING_MEMORY_CONFIDENCE_OUT_OF_RANGE")
        if len(self.provenance_refs) != len(set(self.provenance_refs)):
            raise ValueError("WORKING_MEMORY_PROVENANCE_REFS_MUST_BE_UNIQUE")
        self._assert_no_raw_inner_core(self.payload)

    @classmethod
    def _assert_no_raw_inner_core(cls, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if str(key).lower() in FORBIDDEN_PAYLOAD_KEYS:
                    raise PermissionError("RAW_INNER_CORE_FORBIDDEN_IN_WORKING_MEMORY")
                cls._assert_no_raw_inner_core(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                cls._assert_no_raw_inner_core(item)

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        if self.status in {
            TemporaryMemoryStatus.EXPIRED,
            TemporaryMemoryStatus.INVALIDATED,
            TemporaryMemoryStatus.DELETED,
        }:
            return True
        if self.expires_at is None:
            return False
        current_time = now or datetime.now(timezone.utc)
        return current_time >= self.expires_at

    def is_reusable(self) -> bool:
        return (
            self.status in {TemporaryMemoryStatus.ACTIVE, TemporaryMemoryStatus.UNRESOLVED}
            and self.freshness == MemoryFreshness.CURRENT
            and not self.is_expired()
        )

    def mark_used(self) -> None:
        self.status = TemporaryMemoryStatus.USED
        self.updated_at = datetime.now(timezone.utc)

    def mark_unresolved(self) -> None:
        self.status = TemporaryMemoryStatus.UNRESOLVED
        self.updated_at = datetime.now(timezone.utc)

    def mark_do_not_use(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("DO_NOT_USE_REASON_REQUIRED")
        self.status = TemporaryMemoryStatus.DO_NOT_USE
        self.deletion_reason = reason
        self.updated_at = datetime.now(timezone.utc)

    def invalidate(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("INVALIDATION_REASON_REQUIRED")
        self.status = TemporaryMemoryStatus.INVALIDATED
        self.deletion_reason = reason
        self.updated_at = datetime.now(timezone.utc)

    def mark_expired(self) -> None:
        self.status = TemporaryMemoryStatus.EXPIRED
        self.updated_at = datetime.now(timezone.utc)

    def mark_deleted(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("DELETION_REASON_REQUIRED")
        self.status = TemporaryMemoryStatus.DELETED
        self.deletion_reason = reason
        self.updated_at = datetime.now(timezone.utc)
