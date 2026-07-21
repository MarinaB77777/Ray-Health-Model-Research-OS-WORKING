from runtime.acquisition.buffer_bridge import (
    AcquisitionBufferBridge,
)
from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    ExposureDecision,
    SufficiencyStatus,
)
from runtime.acquisition.exposure_filter import ExposureFilter
from runtime.acquisition.readiness_checker import ReadinessChecker
from runtime.acquisition.result_filter import ResultFilter
from runtime.acquisition.retry_bridge import RetryBridge
from runtime.acquisition.retry_policy import RetryNextStep
from runtime.analysis_buffer.contracts import (
    AnalysisBufferEntry,
    AnalysisBufferOriginalRequest,
    AnalysisBufferStatus,
)


def make_buffer_entry(
    status: AnalysisBufferStatus = (
        AnalysisBufferStatus.WAITING_FOR_RESULT
    ),
) -> AnalysisBufferEntry:
    kwargs = {}

    if status == AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED:
        kwargs["expiration_reason"] = "expired"

    return AnalysisBufferEntry(
        buffer_id="buffer-1",
        status=status,
        original_request=AnalysisBufferOriginalRequest(
            original_request_id="orig-1",
            original_question="Private internal question",
        ),
        **kwargs,
    )


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": (
            "Need general scheduling advice."
        ),
        "source_class": (
            AcquisitionSourceClass.STANDARD_AI_SERVICE
        ),
    }

    data.update(kwargs)

    return AcquisitionRequest(**data)


def test_fake_or_fabricated_content_must_not_enter_system():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        AcquisitionResult(
            request_id="req-1",
            source_class=AcquisitionSourceClass.INTERNET,
            raw_external_result=(
                "This is a fictional invented hallucinated answer."
            ),
        )
    )

    assert (
        result.decision.value
        == "blocked_fake_or_fabricated"
    )


def test_readiness_checker_is_not_forecast_authority():
    checker = ReadinessChecker()

    result = checker.evaluate(
        make_request(
            required_fields=["answer"],
            filled_fields={"answer": "Some answer"},
        )
    )

    assert (
        result.sufficiency_status
        == SufficiencyStatus.BOUNDED_ANALYSIS_READY
    )

    assert (
        result.readiness_metadata[
            "ready_for_forecast"
        ]
        is False
    )


def test_exposure_filter_does_not_export_raw_private_question():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        make_request(
            raw_internal_question=(
                "My husband Michael has stress symptoms."
            )
        )
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert (
        "Michael"
        not in result.outbound_sanitized_request
    )

    assert (
        "a family member"
        in result.outbound_sanitized_request
    )


def test_retry_bridge_does_not_treat_result_received_as_no_response():
    retry_bridge = RetryBridge()

    decision = retry_bridge.handle_buffer_state(
        make_buffer_entry(
            AnalysisBufferStatus.RESULT_RECEIVED
        )
    )

    assert (
        decision.next_step
        == RetryNextStep.BLOCKED_BY_POLICY
    )


def test_retry_bridge_does_not_mutate_analysis_buffer():
    retry_bridge = RetryBridge()

    buffer_entry = make_buffer_entry()

    original_status = buffer_entry.status
    original_results = list(buffer_entry.cleaned_results)

    retry_bridge.handle_buffer_state(buffer_entry)

    assert buffer_entry.status == original_status
    assert (
        buffer_entry.cleaned_results
        == original_results
    )


def test_buffer_bridge_does_not_store_acquisition_inside_buffer():
    bridge = AcquisitionBufferBridge()

    buffer_entry = make_buffer_entry()

    request = make_request()

    bridge.prepare_outbound_from_buffer(
        buffer_entry=buffer_entry,
        acquisition_request=request,
    )

    assert not hasattr(
        buffer_entry,
        "acquisition_request",
    )


def test_expired_unresolved_is_not_fake_completion():
    retry_bridge = RetryBridge()

    decision = retry_bridge.handle_buffer_state(
        make_buffer_entry(
            AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED
        )
    )

    assert (
        decision.next_step
        == RetryNextStep.MARK_UNRESOLVED
    )