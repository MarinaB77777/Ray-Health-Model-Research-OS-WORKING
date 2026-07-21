import pytest

from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    AcquisitionStatus,
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
        )


def test_cleaned_result_not_verified_truth_by_contract():
    result = AcquisitionResult(
        request_id="req-1",
        source_class=AcquisitionSourceClass.INTERNET,
        raw_external_result="some result",
    )

    assert result.trusted is False
    assert result.verified is False


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