from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class RayRole(str, Enum):
    RESEARCH_COLLEAGUE = "research_colleague"
    PARTICIPANT_GUIDE = "participant_guide"


class SupportedLanguage(str, Enum):
    RU = "ru"
    EN = "en"
    ES = "es"


class ClaimKind(str, Enum):
    OBSERVED = "observed"
    SCIENTIFIC_EVIDENCE = "scientific_evidence"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    LIMITATION = "limitation"


class ConfidenceBand(str, Enum):
    NOT_ASSESSED = "not_assessed"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    EXECUTED = "executed"
    REJECTED = "rejected"


class MemoryScope(str, Enum):
    SESSION = "session"
    PROJECT = "project"
    RESEARCHER_PREFERENCE = "researcher_preference"
    PARTICIPANT_PREFERENCE = "participant_preference"


class LearningStatus(str, Enum):
    DRAFT = "draft"
    TRIAL = "trial"
    ACTIVE = "active"
    REJECTED = "rejected"


@dataclass(frozen=True)
class PageContext:
    role: RayRole
    owner_id: str
    page_id: str
    language: SupportedLanguage
    session_id: str | None = None
    project_id: str | None = None
    study_id: str | None = None
    entity_refs: tuple[str, ...] = ()
    selection: dict[str, Any] = field(default_factory=dict)
    allowed_capabilities: tuple[str, ...] = ()
    received_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class RayClaim:
    text: str
    kind: ClaimKind
    confidence: ConfidenceBand = ConfidenceBand.NOT_ASSESSED
    evidence_ids: tuple[str, ...] = ()
    source_record_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.kind == ClaimKind.SCIENTIFIC_EVIDENCE and not self.evidence_ids:
            raise ValueError("SCIENTIFIC_CLAIM_REQUIRES_EVIDENCE")
        if self.kind == ClaimKind.OBSERVED and not self.source_record_ids:
            raise ValueError("OBSERVED_CLAIM_REQUIRES_SOURCE_RECORD")


@dataclass
class RayActionProposal:
    action_type: str
    label: str
    payload: dict[str, Any]
    requires_confirmation: bool = True
    action_id: str = field(default_factory=lambda: str(uuid4()))
    status: ActionStatus = ActionStatus.PROPOSED
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class RayResponse:
    role: RayRole
    page_id: str
    language: SupportedLanguage
    message: str
    claims: list[RayClaim] = field(default_factory=list)
    clarification_questions: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    action_proposals: list[RayActionProposal] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    request_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        for claim in self.claims:
            claim.validate()
        return _jsonable(asdict(self))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def normalize_language(value: str | None) -> SupportedLanguage:
    normalized = (value or "ru").strip().lower()
    try:
        return SupportedLanguage(normalized)
    except ValueError as exc:
        raise ValueError("UNSUPPORTED_LANGUAGE") from exc
