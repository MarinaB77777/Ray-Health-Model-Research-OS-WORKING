from runtime.acquisition.buffer_bridge import AcquisitionBufferBridge
from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionSourceClass,
    ExposureDecision,
    InboundFilterDecision,
    SufficiencyStatus,
)
from runtime.analysis_buffer.contracts import (
    AnalysisBufferEntry,
    AnalysisBufferOriginalRequest,
)


def make_buffer_entry() -> AnalysisBufferEntry:
    return AnalysisBufferEntry(
        buffer_id="buffer-1",
        original_request=AnalysisBufferOriginalRequest(
            original_request_id="orig-1",
            original_question="Private original question",
        ),
    )


def make_acquisition_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Need general scheduling advice.",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_bridge_prepares_outbound_without_buffer_owning_acquisition():
    bridge = AcquisitionBufferBridge()

    buffer_entry = make_buffer_entry()
    acquisition_request = make_acquisition_request()

    result = bridge.prepare_outbound_from_buffer(
        buffer_entry=buffer_entry,
        acquisition_request=acquisition_request,
    )

    assert result.decision == ExposureDecision.ALLOWED
    assert result.outbound_sanitized_request is not None
    assert not hasattr(buffer_entry, "acquisition_request")


def test_bridge_blocks_outbound_when_privacy_policy_unknown():
    bridge = AcquisitionBufferBridge()

    result = bridge.prepare_outbound_from_buffer(
        buffer_entry=make_buffer_entry(),
        acquisition_request=make_acquisition_request(),
        privacy_policy_known=False,
    )

    assert result.decision == ExposureDecision.NEEDS_HUMAN_PERMISSION


def test_bridge_processes_inbound_without_building_answer():
    bridge = AcquisitionBufferBridge()

    result = bridge.process_inbound_for_buffer(
        buffer_entry=make_buffer_entry(),
        acquisition_request=make_acquisition_request(),
        raw_external_result="Useful external result.",
        source_class=AcquisitionSourceClass.INTERNET,
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS
    assert result.cleaned_result == "Useful external result."


def test_bridge_rejects_fake_inbound_result():
    bridge = AcquisitionBufferBridge()

    result = bridge.process_inbound_for_buffer(
        buffer_entry=make_buffer_entry(),
        acquisition_request=make_acquisition_request(),
        raw_external_result="This is a fictional invented answer.",
        source_class=AcquisitionSourceClass.INTERNET,
    )

    assert result.decision == InboundFilterDecision.BLOCKED_FAKE_OR_FABRICATED


def test_bridge_evaluates_readiness_from_explicit_acquisition_request():
    bridge = AcquisitionBufferBridge()

    acquisition_request = make_acquisition_request(
        required_fields=["answer", "source"],
        filled_fields={
            "answer": "Some answer",
            "source": "official source",
        },
    )

    result = bridge.evaluate_buffer_readiness(
        buffer_entry=make_buffer_entry(),
        acquisition_request=acquisition_request,
    )

    assert result.sufficiency_status == SufficiencyStatus.BOUNDED_ANALYSIS_READY
    assert result.readiness_metadata["ready_for_analysis"] is True


def test_bridge_does_not_mutate_buffer_entry():
    bridge = AcquisitionBufferBridge()

    buffer_entry = make_buffer_entry()
    acquisition_request = make_acquisition_request()

    original_status = buffer_entry.status
    original_readiness = buffer_entry.readiness_level

    bridge.prepare_outbound_from_buffer(
        buffer_entry=buffer_entry,
        acquisition_request=acquisition_request,
    )

    assert buffer_entry.status == original_status
    assert buffer_entry.readiness_level == original_readiness
    assert buffer_entry.cleaned_results == []