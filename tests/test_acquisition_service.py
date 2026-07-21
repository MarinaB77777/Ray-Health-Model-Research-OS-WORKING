from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    ExposureDecision,
    InboundFilterDecision,
    SufficiencyStatus,
)

from runtime.acquisition.service import AcquisitionService


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Need general scheduling advice.",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_service_prepares_safe_outbound_request():
    service = AcquisitionService()

    result = service.prepare_outbound_request(
        make_request(),
    )

    assert result.decision == ExposureDecision.ALLOWED
    assert result.outbound_sanitized_request is not None
    assert result.persist_sanitized_request is False


def test_service_blocks_outbound_when_privacy_policy_unknown():
    service = AcquisitionService()

    result = service.prepare_outbound_request(
        make_request(),
        privacy_policy_known=False,
    )

    assert result.decision == ExposureDecision.NEEDS_HUMAN_PERMISSION


def test_service_processes_safe_inbound_result():
    service = AcquisitionService()

    result = service.process_inbound_result(
        AcquisitionResult(
            request_id="req-1",
            source_class=AcquisitionSourceClass.INTERNET,
            raw_external_result="Useful external result.",
        )
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS
    assert result.cleaned_result == "Useful external result."


def test_service_blocks_fake_inbound_result():
    service = AcquisitionService()

    result = service.process_inbound_result(
        AcquisitionResult(
            request_id="req-1",
            source_class=AcquisitionSourceClass.INTERNET,
            raw_external_result="This is a fictional invented answer.",
        )
    )

    assert result.decision == InboundFilterDecision.BLOCKED_FAKE_OR_FABRICATED


def test_service_evaluates_insufficient_readiness():
    service = AcquisitionService()

    request = make_request(
        required_fields=["answer", "source"],
        filled_fields={"answer": "Some answer"},
    )

    result = service.evaluate_readiness(request)

    assert result.sufficiency_status == SufficiencyStatus.INSUFFICIENT
    assert result.missing_required_fields == ["source"]


def test_service_evaluates_bounded_analysis_ready():
    service = AcquisitionService()

    request = make_request(
        required_fields=["answer", "source"],
        filled_fields={
            "answer": "Some answer",
            "source": "official source",
        },
    )

    result = service.evaluate_readiness(request)

    assert result.sufficiency_status == SufficiencyStatus.BOUNDED_ANALYSIS_READY
    assert result.readiness_metadata["ready_for_analysis"] is True
    assert result.readiness_metadata["ready_for_forecast"] is False