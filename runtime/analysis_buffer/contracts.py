from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisBufferStatus(str, Enum):
    WAITING_FOR_RESULT = "waiting_for_result"
    RESULT_RECEIVED = "result_received"
    NEEDS_MORE_DATA = "needs_more_data"
    SUFFICIENT_FOR_ANALYSIS = "sufficient_for_analysis"
    BLOCKED_BY_GOVERNANCE = "blocked_by_governance"
    CANCELLED_BY_HUMAN = "cancelled_by_human"
    EXPIRED_BUT_UNRESOLVED = "expired_but_unresolved"


class AnalysisBufferResultType(str, Enum):
    CLEANED_EXTERNAL_RESULT = "cleaned_external_result"
    HUMAN_CLARIFICATION = "human_clarification"
    SENSOR_DATA = "sensor_data"
    PROJECTION_SIGNAL = "projection_signal"
    RELIABLE_SOURCE_RESULT = "reliable_source_result"
    STANDARD_AI_RESULT = "standard_ai_result"


class AnalysisEvidenceState(str, Enum):
    """Evidence state is not a universal truth rank."""

    UNVERIFIED = "unverified"
    SOURCE_ATTESTED = "source_attested"
    CORROBORATED = "corroborated"
    VERIFIED_WITHIN_DECLARED_SCOPE = "verified_within_declared_scope"


class AnalysisSubject(str, Enum):
    HUMAN_HEALTH = "human_health"
    RAY_SELF_HEALTH = "ray_self_health"
    EXTERNAL_WORLD = "external_world"
    ENVIRONMENT = "environment"
    UNSPECIFIED = "unspecified"


class AnalysisReadinessLevel(str, Enum):
    NOT_READY = "not_ready"
    PARTIAL_ORIENTATION_ONLY = "partial_orientation_only"
    BOUNDED_ANALYSIS_READY = "bounded_analysis_ready"
    FORECAST_READY = "forecast_ready"


class MissingInformationSource(str, Enum):
    HUMAN = "human"
    SENSOR = "sensor"
    PROJECTION = "projection"
    STANDARD_AI = "standard_ai"
    INTERNET_RELIABLE_SOURCE = "internet_reliable_source"
    DOCUMENT = "document"


class AnalysisBufferOriginalRequest(BaseModel):
    original_request_id: str

    private_context_ref: Optional[str] = None
    original_question: Optional[str] = None

    expected_answer_scope: Optional[str] = None
    task_table_ref: Optional[str] = None

    created_at: datetime = Field(default_factory=utc_now)


class AnalysisBufferSanitizedRequest(BaseModel):
    sanitized_request_id: str

    original_request_id: str
    sanitized_payload_ref: Optional[str] = None
    sanitized_question: Optional[str] = None

    removed_private_context: bool = True
    external_exposure_allowed: bool = False

    created_at: datetime = Field(default_factory=utc_now)


class AnalysisBufferCleanedResult(BaseModel):
    """Bounded evidence carried through the analytical waiting zone.

    A cleaned result never becomes a universal truth merely because it is safe,
    relevant, corroborated, or even verified within a declared source scope.
    `result_is_verified_truth` is retained only for stored-data/API compatibility;
    new code should use `evidence_state` plus `truth_authority_ref` and provenance.
    """

    result_id: str

    result_type: AnalysisBufferResultType

    original_request_id: str
    sanitized_request_id: Optional[str] = None

    cleaned_payload_ref: Optional[str] = None
    cleaned_payload: dict[str, Any] = Field(default_factory=dict)

    subject: AnalysisSubject = AnalysisSubject.UNSPECIFIED
    evidence_state: AnalysisEvidenceState = AnalysisEvidenceState.UNVERIFIED
    truth_authority_ref: Optional[str] = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    observed_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    source_reliability_note: Optional[str] = None
    scope_match_note: Optional[str] = None

    # Legacy compatibility only. This flag may describe that an authoritative
    # source verified the bounded claim; it never makes Analysis Buffer itself a
    # truth authority.
    result_is_verified_truth: bool = False
    result_is_sufficient_for_analysis: bool = False

    uncertainty_notes: list[str] = Field(default_factory=list)

    received_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_truth_typing(self) -> "AnalysisBufferCleanedResult":
        if self.result_is_verified_truth:
            if (
                self.evidence_state
                != AnalysisEvidenceState.VERIFIED_WITHIN_DECLARED_SCOPE
            ):
                raise ValueError(
                    "Legacy result_is_verified_truth=True requires "
                    "evidence_state=VERIFIED_WITHIN_DECLARED_SCOPE"
                )
            if not self.truth_authority_ref or not self.truth_authority_ref.strip():
                raise ValueError(
                    "Verified bounded evidence requires truth_authority_ref"
                )
            if not self.provenance:
                raise ValueError(
                    "Verified bounded evidence requires provenance"
                )

        if (
            self.evidence_state
            == AnalysisEvidenceState.VERIFIED_WITHIN_DECLARED_SCOPE
            and not self.truth_authority_ref
        ):
            raise ValueError(
                "VERIFIED_WITHIN_DECLARED_SCOPE requires truth_authority_ref"
            )

        if self.valid_until is not None and self.observed_at is not None:
            if self.valid_until < self.observed_at:
                raise ValueError("valid_until cannot precede observed_at")

        return self


class MissingInformationRequest(BaseModel):
    request_id: str

    source: MissingInformationSource
    reason: str

    required: bool = True
    optional: bool = False

    question: Optional[str] = None
    payload_scope: Optional[str] = None

    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_missing_information_request(
        self,
    ) -> "MissingInformationRequest":
        if self.required and self.optional:
            raise ValueError(
                "MissingInformationRequest cannot be both required and optional"
            )

        return self


class AnalysisBufferEntry(BaseModel):
    buffer_id: str

    status: AnalysisBufferStatus = AnalysisBufferStatus.WAITING_FOR_RESULT
    readiness_level: AnalysisReadinessLevel = AnalysisReadinessLevel.NOT_READY

    original_request: AnalysisBufferOriginalRequest
    sanitized_request: Optional[AnalysisBufferSanitizedRequest] = None

    cleaned_results: list[AnalysisBufferCleanedResult] = Field(
        default_factory=list
    )

    missing_information_requests: list[MissingInformationRequest] = Field(
        default_factory=list
    )

    sufficient_for_analysis: bool = False

    governance_block_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    expiration_reason: Optional[str] = None

    routing_trace: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    expires_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_analysis_buffer_entry(self) -> "AnalysisBufferEntry":
        if (
            self.status == AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS
            and not self.sufficient_for_analysis
        ):
            raise ValueError(
                "SUFFICIENT_FOR_ANALYSIS status requires "
                "sufficient_for_analysis=True"
            )

        if (
            self.sufficient_for_analysis
            and self.readiness_level == AnalysisReadinessLevel.NOT_READY
        ):
            raise ValueError(
                "sufficient_for_analysis=True requires readiness above NOT_READY"
            )

        if (
            self.status == AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE
            and self.governance_block_reason is None
        ):
            raise ValueError(
                "BLOCKED_BY_GOVERNANCE requires governance_block_reason"
            )

        if (
            self.status == AnalysisBufferStatus.CANCELLED_BY_HUMAN
            and self.cancellation_reason is None
        ):
            raise ValueError(
                "CANCELLED_BY_HUMAN requires cancellation_reason"
            )

        if (
            self.status == AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED
            and self.expiration_reason is None
        ):
            raise ValueError(
                "EXPIRED_BUT_UNRESOLVED requires expiration_reason"
            )

        return self

    def update_timestamp(self) -> None:
        self.updated_at = utc_now()

    def result_arrived(self) -> bool:
        return len(self.cleaned_results) > 0

    def needs_more_data(self) -> bool:
        return (
            self.status == AnalysisBufferStatus.NEEDS_MORE_DATA
            or len(self.missing_information_requests) > 0
        )

    def can_close_waiting_state(self) -> bool:
        return self.status in {
            AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS,
            AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE,
            AnalysisBufferStatus.CANCELLED_BY_HUMAN,
            AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED,
        }


class AnalysisBufferInvariant(BaseModel):
    name: str
    description: str
    preserved: bool = True


ANALYSIS_BUFFER_INVARIANTS: list[AnalysisBufferInvariant] = [
    AnalysisBufferInvariant(
        name="analysis_buffer_is_not_memory",
        description=(
            "Analysis Buffer is a temporary analytical waiting zone, "
            "not long-term memory."
        ),
    ),
    AnalysisBufferInvariant(
        name="analysis_buffer_is_not_truth_authority",
        description=(
            "Buffered results do not become verified truth automatically."
        ),
    ),
    AnalysisBufferInvariant(
        name="verification_is_typed_and_bounded",
        description=(
            "Verification applies only within an explicit authority scope and "
            "must preserve subject, provenance, and uncertainty."
        ),
    ),
    AnalysisBufferInvariant(
        name="result_arrival_is_not_sufficiency",
        description=(
            "Arrival of a result does not mean sufficient_for_analysis."
        ),
    ),
    AnalysisBufferInvariant(
        name="external_result_is_not_ray_truth",
        description=(
            "External or Standard AI result must remain bounded evidence."
        ),
    ),
    AnalysisBufferInvariant(
        name="expiration_is_not_fake_completion",
        description=(
            "Expired unresolved request must preserve uncertainty, "
            "not fabricate completion."
        ),
    ),
    AnalysisBufferInvariant(
        name="no_data_requires_acquisition_or_clarification",
        description=(
            "Missing required data should trigger clarification/acquisition "
            "or explicit insufficient-data state, not invention."
        ),
    ),
    AnalysisBufferInvariant(
        name="original_request_stays_private",
        description=(
            "Original internal request remains inside analytical zone; "
            "only sanitized request may leave."
        ),
    ),
]