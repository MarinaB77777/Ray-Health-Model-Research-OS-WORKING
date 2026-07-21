from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    AcquisitionStatus,
    ExposureDecision,
    InboundFilterDecision,
    SufficiencyStatus,
)
from runtime.acquisition.service_with_registry import (
    AcquisitionServiceWithRegistry,
)


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Need general scheduling advice.",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_register_and_get_request():
    service = AcquisitionServiceWithRegistry()

    service.register_request(make_request())

    stored = service.get_request("req-1")

    assert stored is not None
    assert stored.request_id == "req-1"


def test_missing_request_returns_none():
    service = AcquisitionServiceWithRegistry()

    assert service.get_request("missing") is None
    assert service.prepare_outbound_request("missing") is None
    assert service.evaluate_readiness("missing") is None


def test_allowed_outbound_prepared_not_sent_and_sets_waiting():
    service = AcquisitionServiceWithRegistry()
    service.register_request(make_request())

    result = service.prepare_outbound_request("req-1")

    stored = service.get_request("req-1")

    assert result is not None
    assert result.decision == ExposureDecision.ALLOWED
    assert stored.status == AcquisitionStatus.WAITING
    assert stored.outbound_sent is False
    assert stored.outbound_source_metadata["outbound_prepared"] is True
    assert stored.outbound_source_metadata["outbound_sent"] is False


def test_blocked_outbound_sets_blocked_status():
    service = AcquisitionServiceWithRegistry()
    service.register_request(
        make_request(
            raw_internal_question="The diagnosis is severe stress disorder."
        )
    )

    result = service.prepare_outbound_request("req-1")

    stored = service.get_request("req-1")

    assert result is not None
    assert result.decision == ExposureDecision.CANNOT_SAFELY_ANONYMIZE
    assert stored.status == AcquisitionStatus.BLOCKED


def test_inbound_allowed_for_readiness_sets_filtered():
    service = AcquisitionServiceWithRegistry()
    service.register_request(make_request())

    result = service.process_inbound_result(
        request_id="req-1",
        acquisition_result=AcquisitionResult(
            request_id="req-1",
            source_class=AcquisitionSourceClass.INTERNET,
            raw_external_result="Useful external result.",
        ),
    )

    stored = service.get_request("req-1")

    assert result is not None
    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS
    assert stored.status == AcquisitionStatus.FILTERED


def test_fake_inbound_sets_blocked():
    service = AcquisitionServiceWithRegistry()
    service.register_request(make_request())

    result = service.process_inbound_result(
        request_id="req-1",
        acquisition_result=AcquisitionResult(
            request_id="req-1",
            source_class=AcquisitionSourceClass.INTERNET,
            raw_external_result="This is a fictional invented answer.",
        ),
    )

    stored = service.get_request("req-1")

    assert result is not None
    assert result.decision == (
        InboundFilterDecision.BLOCKED_FAKE_OR_FABRICATED
    )
    assert stored.status == AcquisitionStatus.BLOCKED


def test_evaluate_readiness_insufficient_sets_needs_more_data():
    service = AcquisitionServiceWithRegistry()
    service.register_request(
        make_request(
            required_fields=["answer", "source"],
            filled_fields={"answer": "Some answer"},
        )
    )

    result = service.evaluate_readiness("req-1")
    stored = service.get_request("req-1")

    assert result is not None
    assert result.sufficiency_status == SufficiencyStatus.INSUFFICIENT
    assert stored.status == AcquisitionStatus.NEEDS_MORE_DATA
    assert stored.sufficiency_status == SufficiencyStatus.INSUFFICIENT


def test_evaluate_readiness_ready_sets_bounded_status():
    service = AcquisitionServiceWithRegistry()
    service.register_request(
        make_request(
            required_fields=["answer"],
            filled_fields={"answer": "Some answer"},
        )
    )

    result = service.evaluate_readiness("req-1")
    stored = service.get_request("req-1")

    assert result is not None
    assert result.sufficiency_status == SufficiencyStatus.BOUNDED_ANALYSIS_READY
    assert stored.status == AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS
    assert stored.sufficiency_status == (
        SufficiencyStatus.BOUNDED_ANALYSIS_READY
    )