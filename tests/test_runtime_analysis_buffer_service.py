import pytest

from runtime.analysis_buffer.contracts import (
    AnalysisBufferCleanedResult,
    AnalysisBufferEntry,
    AnalysisBufferOriginalRequest,
    AnalysisBufferResultType,
    AnalysisBufferStatus,
    AnalysisReadinessLevel,
    MissingInformationRequest,
    MissingInformationSource,
)

from runtime.analysis_buffer.service import AnalysisBufferService


def make_original_request() -> AnalysisBufferOriginalRequest:
    return AnalysisBufferOriginalRequest(
        original_request_id="orig-1",
        original_question="Private internal question",
        expected_answer_scope="bounded scope",
    )


def make_entry(buffer_id: str = "buf-1") -> AnalysisBufferEntry:
    return AnalysisBufferEntry(
        buffer_id=buffer_id,
        original_request=make_original_request(),
    )


def test_add_and_get_entry():
    service = AnalysisBufferService()
    entry = make_entry("buf-1")

    service.add_entry(entry)

    assert service.get_entry("buf-1") == entry


def test_attach_cleaned_result_does_not_make_sufficient():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-2"))

    updated = service.attach_cleaned_result(
        buffer_id="buf-2",
        result=AnalysisBufferCleanedResult(
            result_id="res-1",
            result_type=AnalysisBufferResultType.STANDARD_AI_RESULT,
            original_request_id="orig-1",
        ),
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.RESULT_RECEIVED
    assert updated.sufficient_for_analysis is False
    assert service.can_continue_analysis("buf-2") is False


def test_add_missing_information_request_marks_needs_more_data():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-3"))

    updated = service.add_missing_information_request(
        buffer_id="buf-3",
        request=MissingInformationRequest(
            request_id="missing-1",
            source=MissingInformationSource.HUMAN,
            reason="Need clarification",
        ),
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.NEEDS_MORE_DATA
    assert updated.needs_more_data() is True
    assert service.can_continue_analysis("buf-3") is False


def test_mark_sufficient_for_bounded_analysis():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-4"))

    updated = service.mark_sufficient_for_analysis(
        buffer_id="buf-4",
        readiness_level=AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS
    assert updated.sufficient_for_analysis is True
    assert service.can_continue_analysis("buf-4") is True


def test_mark_sufficient_for_forecast_ready():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-5"))

    updated = service.mark_sufficient_for_analysis(
        buffer_id="buf-5",
        readiness_level=AnalysisReadinessLevel.FORECAST_READY,
    )

    assert updated is not None
    assert updated.readiness_level == AnalysisReadinessLevel.FORECAST_READY
    assert service.can_continue_analysis("buf-5") is True


def test_partial_orientation_cannot_be_marked_sufficient():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-6"))

    with pytest.raises(ValueError):
        service.mark_sufficient_for_analysis(
            buffer_id="buf-6",
            readiness_level=AnalysisReadinessLevel.PARTIAL_ORIENTATION_ONLY,
        )

    saved = service.get_entry("buf-6")

    assert saved is not None
    assert saved.status == AnalysisBufferStatus.WAITING_FOR_RESULT
    assert saved.sufficient_for_analysis is False


def test_not_ready_cannot_be_marked_sufficient():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-7"))

    with pytest.raises(ValueError):
        service.mark_sufficient_for_analysis(
            buffer_id="buf-7",
            readiness_level=AnalysisReadinessLevel.NOT_READY,
        )

    saved = service.get_entry("buf-7")

    assert saved is not None
    assert saved.status == AnalysisBufferStatus.WAITING_FOR_RESULT
    assert saved.sufficient_for_analysis is False


def test_mark_governance_blocked_blocks_continuation():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-8"))

    updated = service.mark_governance_blocked(
        buffer_id="buf-8",
        reason="Governance blocked continuation",
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE
    assert service.can_continue_analysis("buf-8") is False


def test_mark_cancelled_by_human_closes_operationally():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-9"))

    updated = service.mark_cancelled_by_human(
        buffer_id="buf-9",
        reason="Human confirmed cancellation",
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.CANCELLED_BY_HUMAN
    assert updated.can_close_waiting_state() is True
    assert service.can_continue_analysis("buf-9") is False


def test_mark_expired_unresolved_does_not_continue_analysis():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-10"))

    updated = service.mark_expired_unresolved(
        buffer_id="buf-10",
        reason="Expired without sufficient data",
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED
    assert updated.sufficient_for_analysis is False
    assert updated.can_close_waiting_state() is True
    assert service.can_continue_analysis("buf-10") is False


def test_list_methods_delegate_to_store():
    service = AnalysisBufferService()

    service.add_entry(make_entry("open"))
    service.add_entry(make_entry("sufficient"))
    service.mark_sufficient_for_analysis(
        "sufficient",
        AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
    )

    service.add_entry(make_entry("unresolved"))
    service.mark_needs_more_data("unresolved")

    assert {entry.buffer_id for entry in service.list_open()} == {
        "open",
        "unresolved",
    }

    assert {
        entry.buffer_id
        for entry in service.list_sufficient_for_analysis()
    } == {"sufficient"}

    assert {entry.buffer_id for entry in service.list_unresolved()} == {
        "unresolved",
    }


def test_can_continue_analysis_false_for_missing_entry():
    service = AnalysisBufferService()

    assert service.can_continue_analysis("missing") is False


def test_remove_entry():
    service = AnalysisBufferService()
    service.add_entry(make_entry("buf-remove"))

    assert service.remove_entry("buf-remove") is True
    assert service.get_entry("buf-remove") is None
    assert service.remove_entry("buf-remove") is False