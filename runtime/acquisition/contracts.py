# runtime/acquisition/contracts.py

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AcquisitionSourceClass(str, Enum):
    HUMAN_PRIMARY = "human_primary"
    EXTERNAL_HUMAN = "external_human"
    INTERNET = "internet"
    OFFICIAL_SOURCE = "official_source"
    SCIENTIFIC_SOURCE = "scientific_source"
    STANDARD_AI_SERVICE = "standard_ai_service"
    SENSOR = "sensor"
    INTERNAL_RAY_LAYER = "internal_ray_layer"


class AcquisitionStatus(str, Enum):
    CREATED = "created"
    WAITING = "waiting"
    RESULT_RECEIVED = "result_received"
    FILTERED = "filtered"
    NEEDS_MORE_DATA = "needs_more_data"
    SUFFICIENT_FOR_BOUNDED_ANALYSIS = "sufficient_for_bounded_analysis"
    SUFFICIENT_FOR_FORECAST = "sufficient_for_forecast"
    BLOCKED = "blocked"
    FAILED = "failed"
    UNRESOLVED = "unresolved"
    CLOSED = "closed"


class ExposureDecision(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    NEEDS_HUMAN_PERMISSION = "needs_human_permission"
    CANNOT_SAFELY_ANONYMIZE = "cannot_safely_anonymize"


class InboundFilterDecision(str, Enum):
    ALLOWED_FOR_ORIENTATION = "allowed_for_orientation"
    ALLOWED_FOR_READINESS = "allowed_for_readiness"
    BLOCKED_UNSAFE = "blocked_unsafe"
    BLOCKED_FAKE_OR_FABRICATED = "blocked_fake_or_fabricated"
    BLOCKED_IRRELEVANT = "blocked_irrelevant"
    BLOCKED_LOW_SOURCE_QUALITY = "blocked_low_source_quality"


class SufficiencyStatus(str, Enum):
    NOT_EVALUATED = "not_evaluated"
    INSUFFICIENT = "insufficient"
    PARTIAL_ORIENTATION_ONLY = "partial_orientation_only"
    BOUNDED_ANALYSIS_READY = "bounded_analysis_ready"
    FORECAST_READY = "forecast_ready"


class AcquisitionReasonCode(str, Enum):
    RAW_QUESTION_INTERNAL_ONLY = "raw_question_internal_only"
    OUTBOUND_SANITIZED_NOT_STORED = "outbound_sanitized_not_stored"
    HUMAN_PERMISSION_REQUIRED = "human_permission_required"
    PRIVACY_POLICY_UNKNOWN = "privacy_policy_unknown"
    UNSAFE_EXTERNAL_RESULT = "unsafe_external_result"
    FAKE_CONTENT_REJECTED = "fake_content_rejected"
    SOURCE_CLASS_MISMATCH = "source_class_mismatch"
    OFFICIAL_SOURCE_REQUIRED = "official_source_required"
    SCIENTIFIC_SOURCE_REQUIRED = "scientific_source_required"
    MISSING_REQUIRED_FIELDS = "missing_required_fields"
    CLEANED_NOT_TRUSTED = "cleaned_not_trusted"
    TRUSTED_NOT_VERIFIED = "trusted_not_verified"
    NO_DATA_ASK_OR_ACQUIRE = "no_data_ask_or_acquire"
    OUTBOUND_METADATA_REQUIRED = "outbound_metadata_required"
    VERIFIED_REQUIRES_TRUSTED = "verified_requires_trusted"
    FIELD_OUTSIDE_REQUIRED_FIELDS = "field_outside_required_fields"
    FORECAST_REQUIRES_HIGH_SUFFICIENCY = "forecast_requires_high_sufficiency"
    ANALYSIS_READY_REQUIRES_REQUIRED_FIELDS = (
        "analysis_ready_requires_required_fields"
    )


class AcquisitionRequest(BaseModel):
    """
    Internal Ray acquisition request.

    raw_internal_question is internal-only and must never be sent outside Ray
    directly. External requests must be produced through Exposure Filter.
    """

    request_id: str

    raw_internal_question: Optional[str] = None
    raw_internal_question_ref: Optional[str] = None

    source_class: AcquisitionSourceClass
    created_at: datetime = Field(default_factory=utc_now)

    domain: Optional[str] = None
    importance_level: Optional[str] = None
    risk_level: Optional[str] = None

    required_fields: list[str] = Field(default_factory=list)
    filled_fields: dict[str, Any] = Field(default_factory=dict)
    extra_filled_fields_metadata: dict[str, Any] = Field(default_factory=dict)

    status: AcquisitionStatus = AcquisitionStatus.CREATED
    sufficiency_status: SufficiencyStatus = SufficiencyStatus.NOT_EVALUATED

    reason_codes: list[AcquisitionReasonCode] = Field(default_factory=list)

    outbound_sent: bool = False
    outbound_source_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_question_reference(self) -> "AcquisitionRequest":
        if not self.raw_internal_question and not self.raw_internal_question_ref:
            raise ValueError(
                "Either raw_internal_question or raw_internal_question_ref "
                "is required."
            )
        return self

    @model_validator(mode="after")
    def validate_filled_fields(self) -> "AcquisitionRequest":
        required = set(self.required_fields)
        filled = set(self.filled_fields.keys())

        outside = filled - required
        if outside and not self.extra_filled_fields_metadata:
            raise ValueError(
                "filled_fields contains fields outside required_fields "
                "without metadata: "
                f"{sorted(outside)}"
            )
        return self

    @model_validator(mode="after")
    def validate_outbound_metadata(self) -> "AcquisitionRequest":
        if self.outbound_sent and not self.outbound_source_metadata:
            raise ValueError(
                "outbound_sent=True requires outbound_source_metadata."
            )
        return self

    @model_validator(mode="after")
    def validate_sufficiency_requires_required_fields(
        self,
    ) -> "AcquisitionRequest":
        if self.sufficiency_status in {
            SufficiencyStatus.BOUNDED_ANALYSIS_READY,
            SufficiencyStatus.FORECAST_READY,
        } and not self.required_fields:
            raise ValueError(
                "Analysis-ready sufficiency requires required_fields."
            )
        return self

    @model_validator(mode="after")
    def validate_sufficiency_status_alignment(
        self,
    ) -> "AcquisitionRequest":
        if (
            self.sufficiency_status
            == SufficiencyStatus.BOUNDED_ANALYSIS_READY
            and self.status
            != AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS
        ):
            raise ValueError(
                "BOUNDED_ANALYSIS_READY requires "
                "status=SUFFICIENT_FOR_BOUNDED_ANALYSIS."
            )

        if (
            self.sufficiency_status == SufficiencyStatus.FORECAST_READY
            and self.status != AcquisitionStatus.SUFFICIENT_FOR_FORECAST
        ):
            raise ValueError(
                "FORECAST_READY requires status=SUFFICIENT_FOR_FORECAST."
            )

        return self


class ExposureFilterResult(BaseModel):
    """
    Outbound exposure filter result.

    outbound_sanitized_request is temporary/in-flight only.
    It must not be persisted by default.
    """

    request_id: str
    decision: ExposureDecision

    outbound_sanitized_request: Optional[str] = None
    persist_sanitized_request: bool = False

    reason_codes: list[AcquisitionReasonCode] = Field(default_factory=list)
    exposure_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_persistence_policy(self) -> "ExposureFilterResult":
        if self.persist_sanitized_request:
            raise ValueError(
                "persist_sanitized_request=True is not allowed by default. "
                "Use a separate governed audit/debug policy if needed."
            )
        return self

    @model_validator(mode="after")
    def validate_allowed_has_payload(self) -> "ExposureFilterResult":
        if (
            self.decision == ExposureDecision.ALLOWED
            and not self.outbound_sanitized_request
        ):
            raise ValueError(
                "ALLOWED exposure decision requires "
                "outbound_sanitized_request."
            )
        return self

    @model_validator(mode="after")
    def validate_blocked_has_no_payload(self) -> "ExposureFilterResult":
        if (
            self.decision != ExposureDecision.ALLOWED
            and self.outbound_sanitized_request is not None
        ):
            raise ValueError(
                "Non-ALLOWED exposure decision must not include "
                "outbound_sanitized_request."
            )
        return self


class AcquisitionResult(BaseModel):
    """
    Raw external/source result.

    Raw external result is not trusted and not verified by default.
    """

    request_id: str
    source_class: AcquisitionSourceClass
    received_at: datetime = Field(default_factory=utc_now)

    raw_external_result: Optional[str] = None
    source_metadata: dict[str, Any] = Field(default_factory=dict)

    trusted: bool = False
    verified: bool = False

    @model_validator(mode="after")
    def validate_verified_requires_trusted(self) -> "AcquisitionResult":
        if self.verified and not self.trusted:
            raise ValueError("verified=True requires trusted=True.")
        return self


class InboundFilterResult(BaseModel):
    """
    Inbound result filter.

    cleaned_result means safe/relevant enough for the declared next layer,
    not true and not verified.
    """

    request_id: str
    decision: InboundFilterDecision

    cleaned_result: Optional[str] = None

    reason_codes: list[AcquisitionReasonCode] = Field(default_factory=list)
    filter_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_allowed_has_cleaned_result(self) -> "InboundFilterResult":
        if self.decision in {
            InboundFilterDecision.ALLOWED_FOR_ORIENTATION,
            InboundFilterDecision.ALLOWED_FOR_READINESS,
        } and not self.cleaned_result:
            raise ValueError(
                "Allowed inbound filter decision requires cleaned_result."
            )
        return self


class ReadinessEvaluation(BaseModel):
    """
    Readiness/completeness evaluation.

    Readiness decides sufficiency, not truth.
    """

    request_id: str
    sufficiency_status: SufficiencyStatus

    missing_required_fields: list[str] = Field(default_factory=list)
    allowed_next_step: Optional[str] = None

    reason_codes: list[AcquisitionReasonCode] = Field(default_factory=list)
    readiness_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_missing_fields_for_insufficient(
        self,
    ) -> "ReadinessEvaluation":
        if (
            self.sufficiency_status == SufficiencyStatus.INSUFFICIENT
            and not self.missing_required_fields
        ):
            raise ValueError(
                "INSUFFICIENT readiness should include "
                "missing_required_fields."
            )
        return self

    @model_validator(mode="after")
    def validate_forecast_readiness(self) -> "ReadinessEvaluation":
        if (
            self.sufficiency_status == SufficiencyStatus.FORECAST_READY
            and self.missing_required_fields
        ):
            raise ValueError(
                "FORECAST_READY cannot have missing_required_fields."
            )
        return self