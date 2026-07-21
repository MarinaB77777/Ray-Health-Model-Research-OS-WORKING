from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Optional


class SessionStatus(str, Enum):
    CREATED = "CREATED"
    ANSWERS_RECEIVED = "ANSWERS_RECEIVED"
    RUN_COMPLETED = "RUN_COMPLETED"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    PARTIAL_RESULT = "PARTIAL_RESULT"
    EXPORT_READY = "EXPORT_READY"
    EXPORT_BLOCKED = "EXPORT_BLOCKED"
    RUN_FAILED = "RUN_FAILED"
    INVALIDATED = "INVALIDATED"
    CLOSED = "CLOSED"


@dataclass
class ParticipantSession:
    session_id: str
    participant_id: str
    status: SessionStatus = SessionStatus.CREATED
    subject_link_id: Optional[str] = None
    study_id: Optional[str] = None
    participant_role: Optional[str] = None
    synchronization_reference: Optional[str] = None
    agreement_id: Optional[str] = None
    agreement_version: Optional[str] = None
    agreement_signed_at: Optional[datetime] = None
    collection_agreement_status: Optional[str] = None    

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    closed_at: Optional[datetime] = None

    answers: dict = field(default_factory=dict)
    # Identity/metadata describing the submitted domain dataset.
    # Does not contain analysis results.
    domain_data_identity: dict = field(default_factory=dict)
    answer_revision_count: int = 0
    answer_merge_history: list = field(default_factory=list)
    questionnaire_submissions: list = field(default_factory=list)
    research_answer_records: list = field(default_factory=list)
    run_count: int = 0
    run_history: list = field(default_factory=list)

    engine_version: str = "mvp-1"
    engine_snapshot_schema_version: str = "mvp-1"
    public_output_schema_version: str = "mvp-1"
    export_schema_version: str = "mvp-1"

    raw_engine_result: dict = field(default_factory=dict)
    public_output: dict = field(default_factory=dict)

    next_question_snapshots: list = field(default_factory=list)
    acquisition_request_snapshots: dict = field(default_factory=dict)

    uncertainty_snapshot: dict = field(default_factory=dict)

    export_generated: bool = False
    export_policy_version: str = "mvp-1"

    invalidated: bool = False
    invalidation_reason: Optional[str] = None
