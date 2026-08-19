import pytest

from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    AcquisitionStatus,
    AcquisitionSubject,
    AcquisitionVerificationState,
    ExposureDecision,
    ExposureFilterResult,
    InboundFilterDecision,
    InboundFilterResult,
    ReadinessEvaluation,
    SufficiencyStatus,
)


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Private internal question",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_acquisition_request_requires_raw_question_or_ref():
    with pytest.raises(ValueError):
        AcquisitionRequest(
            request_id="req-1",
            source_class=AcquisitionSourceClass.STANDARD_AI_SERVICE,
        )


def test_acquisition_request_accepts_raw_question_ref():
    request = AcquisitionRequest(
        request_id="req-2",
        raw_internal_question_ref="private-ref-1",
        source_class=AcquisitionSourceClass.STANDARD_AI_SERVICE,
    )

    assert request.raw_internal_question_ref == "private-ref-1"


def test_filled_fields_outside_required_requires_metadata():
    with pytest.raises(ValueError):
        make_request(
            required_fields=["a"],
            filled_fields={"b": "value"},
        )


def test_filled_fields_outside_required_allowed_with_metadata():
    request = make_request(
        required_fields=["a"],
        filled_fields={"b": "value"},
        extra_filled_fields_metadata={
            "b": "additional contextual field"
        },
    )

    assert request.filled_fields["b"] == "value"


def test_outbound_sent_requires_metadata():
    with pytest.raises(ValueError):
        make_request(outbound_sent=True)


def test_forecast_ready_requires_forecast_status():
    with pytest.raises(ValueError):
        make_request(
            required_fields=["a"],
            filled_fields={"a": "value"},
            sufficiency_status=SufficiencyStatus.FORECAST_READY,
            status=AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
        )


def test_bounded_analysis_ready_requires_bounded_status():
    with pytest.raises(ValueError):
        make_request(
            required_fields=["a"],
            filled_fields={"a": "value"},
            sufficiency_status=SufficiencyStatus.BOUNDED_ANALYSIS_READY,
            status=AcquisitionStatus.WAITING,
        )


def test_analysis_ready_requires_required_fields():
    with pytest.raises(ValueError):
        make_request(
            sufficiency_status=SufficiencyStatus.BOUNDED_ANALYSIS_READY,
            status=AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
        )


def test_valid_bounded_analysis_ready_request():
    request = make_request(
        required_fields=["answer"],
        filled_fields={"answer": "bounded result"},
        sufficiency_status=SufficiencyStatus.BOUNDED_ANALYSIS_READY,
        status=AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
    )

    assert request.sufficiency_status == SufficiencyStatus.BOUNDED_ANALYSIS_READY


def test_valid_forecast_ready_request():
    request = make_request(
        required_fields=["answer"],
        filled_fields={"answer": "forecast result"},
        sufficiency_status=SufficiencyStatus.FORECAST_READY,
        status=AcquisitionStatus.SUFFICIENT_FOR_FORECAST,
    )

    assert request.sufficiency_status == SufficiencyStatus.FORECAST_READY


def test_allowed_exposure_requires_sanitized_payload():
    with pytest.raises(ValueError):
        ExposureFilterResult(
            request_id="req-1",
            decision=ExposureDecision.ALLOWED,
        )


def test_non_allowed_exposure_must_not_include_payload():
    with pytest.raises(ValueError):
        ExposureFilterResult(
            request_id="req-1",
            decision=ExposureDecision.BLOCKED,
            outbound_sanitized_request="should not leave",
        )


def test_sanitized_request_not_persisted_by_default():
    result = ExposureFilterResult(
        request_id="req-1",
        decision=ExposureDecision.ALLOWED,
        outbound_sanitized_request="safe external question",
        persist_sanitized_request=False,
        reason_codes=[
            AcquisitionReasonCode.OUTBOUND_SANITIZED_NOT_STORED,
        ],
    )

    assert result.persist_sanitized_request is False


def test_persist_sanitized_request_blocked_by_default():
    with pytest.raises(ValueError):
        ExposureFilterResult(
            request_id="req-1",
            decision=ExposureDecision.ALLOWED,
            outbound_sanitized_request="safe external question",
            persist_sanitized_request=True,
        )


def test_verified_requires_trusted():
    with pytest.raises(ValueError):
        AcquisitionResult(
            request_id="req-1",
            source_class=AcquisitionSourceClass.INTERNET,
            raw_external_result="some result",
            trusted=False,
            verified=True,
            verification_state=(
                AcquisitionVerificationState.VERIFIED_WITHIN_DECLARED_SCOPE
            ),
            verification_scope="bounded claim",
            verification_authority_ref="official_source:test",
            provenance={"source": "test"},
        )


def test_verified_requires_scope_authority_and_provenance():
    with pytest.raises(ValueError):
        AcquisitionResult(
            request_id="req-verified-missing-scope",
            source_class=AcquisitionSourceClass.OFFICIAL_SOURCE,
            trusted=True,
            verified=True,
            verification_state=(
                AcquisitionVerificationState.VERIFIED_WITHIN_DECLARED_SCOPE
            ),
        )


def test_verified_result_is_bounded_to_declared_scope():
    result = AcquisitionResult(
        request_id="req-verified",
        source_class=AcquisitionSourceClass.OFFICIAL_SOURCE,
        raw_external_result="official bounded result",
        subject=AcquisitionSubject.EXTERNAL_WORLD,
        trusted=True,
        verified=True,
        verification_state=(
            AcquisitionVerificationState.VERIFIED_WITHIN_DECLARED_SCOPE
        ),
        verification_scope="document authenticity and declared field value",
        verification_authority_ref="official_source:registry:v1",
        provenance={"document_id": "doc-1", "retrieved_by": "acquisition"},
    )

    assert result.verified is True
    assert result.subject == AcquisitionSubject.EXTERNAL_WORLD
    assert result.verification_scope.startswith("document authenticity")


def test_trusted_source_is_not_silently_promoted_to_verified():
    result = AcquisitionResult(
        request_id="req-trusted",
        source_class=AcquisitionSourceClass.SCIENTIFIC_SOURCE,
        trusted=True,
        verified=False,
    )

    assert result.verified is False
    assert (
        result.verification_state
        == AcquisitionVerificationState.TRUSTED_SOURCE_ONLY
    )


def test_cleaned_result_not_verified_truth_by_contract():
    result = AcquisitionResult(
        request_id="req-1",
        source_class=AcquisitionSourceClass.INTERNET,
        raw_external_result="some result",
    )

    assert result.trusted is False
    assert result.verified is False
    assert result.verification_state == AcquisitionVerificationState.UNVERIFIED


def test_allowed_inbound_filter_requires_cleaned_result():
    with pytest.raises(ValueError):
        InboundFilterResult(
            request_id="req-1",
            decision=InboundFilterDecision.ALLOWED_FOR_READINESS,
        )


def test_inbound_filter_orientation_requires_cleaned_result():
    with pytest.raises(ValueError):
        InboundFilterResult(
            request_id="req-1",
            decision=InboundFilterDecision.ALLOWED_FOR_ORIENTATION,
        )


def test_valid_inbound_filter_cleaned_not_truth():
    result = InboundFilterResult(
        request_id="req-1",
        decision=InboundFilterDecision.ALLOWED_FOR_ORIENTATION,
        cleaned_result="cleaned but not verified",
        reason_codes=[
            AcquisitionReasonCode.CLEANED_NOT_TRUSTED,
        ],
    )

    assert result.cleaned_result == "cleaned but not verified"


def test_insufficient_readiness_requires_missing_fields():
    with pytest.raises(ValueError):
        ReadinessEvaluation(
            request_id="req-1",
            sufficiency_status=SufficiencyStatus.INSUFFICIENT,
        )


def test_forecast_ready_cannot_have_missing_fields():
    with pytest.raises(ValueError):
        ReadinessEvaluation(
            request_id="req-1",
            sufficiency_status=SufficiencyStatus.FORECAST_READY,
            missing_required_fields=["field"],
        )


def test_valid_readiness_bounded_analysis():
    evaluation = ReadinessEvaluation(
        request_id="req-1",
        sufficiency_status=SufficiencyStatus.BOUNDED_ANALYSIS_READY,
        allowed_next_step="analyst_answer_builder",
    )

    assert evaluation.sufficiency_status == SufficiencyStatus.BOUNDED_ANALYSIS_READY
