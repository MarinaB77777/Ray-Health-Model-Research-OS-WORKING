from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4


class TemporaryMemoryStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    UNRESOLVED = "unresolved"
    EXPIRED = "expired"
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


@dataclass
class TemporaryMemoryRecord:
    id: str = field(default_factory=lambda: str(uuid4()))

    record_type: TemporaryMemoryType = TemporaryMemoryType.RUNTIME_COORDINATION
    status: TemporaryMemoryStatus = TemporaryMemoryStatus.ACTIVE
    scope: TemporaryMemoryScope = TemporaryMemoryScope.SESSION
    source: TemporaryMemorySource = TemporaryMemorySource.RUNTIME

    session_id: Optional[str] = None
    task_id: Optional[str] = None
    related_action_id: Optional[str] = None
    related_verdict_id: Optional[str] = None

    # Operational payload only.
    # Do not store raw Inner Core content, raw sensor logs,
    # raw dialogue archives, hidden diagnostic markers,
    # permanent personality conclusions, or unvalidated long-term assumptions.
    payload: dict[str, Any] = field(default_factory=dict)

    payload_summary: Optional[str] = None
    retention_reason: Optional[str] = None
    promotion_allowed: bool = False
    sensitivity_level: TemporaryMemorySensitivity = TemporaryMemorySensitivity.MEDIUM

    priority: int = 0
    tags: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    deletion_reason: Optional[str] = None

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        if self.status in {
            TemporaryMemoryStatus.EXPIRED,
            TemporaryMemoryStatus.DELETED,
        }:
            return True

        if self.expires_at is None:
            return False

        current_time = now or datetime.now(timezone.utc)
        return current_time >= self.expires_at

    def mark_used(self) -> None:
        self.status = TemporaryMemoryStatus.USED
        self.updated_at = datetime.now(timezone.utc)

    def mark_unresolved(self) -> None:
        self.status = TemporaryMemoryStatus.UNRESOLVED
        self.updated_at = datetime.now(timezone.utc)

    def mark_expired(self) -> None:
        self.status = TemporaryMemoryStatus.EXPIRED
        self.updated_at = datetime.now(timezone.utc)

    def mark_deleted(self, reason: str) -> None:
        self.status = TemporaryMemoryStatus.DELETED
        self.deletion_reason = reason
        self.updated_at = datetime.now(timezone.utc)