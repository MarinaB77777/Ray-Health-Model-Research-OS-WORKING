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

from runtime.analysis_buffer.store import AnalysisBufferStore


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
    store = AnalysisBufferStore()
    entry = make_entry("buf-1")

    store.add_entry(entry)

    assert store.get_entry("buf-1") == entry


def test_attach_cleaned_result_does_not_make_sufficient():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-2"))

    updated = store.attach_cleaned_result(
        buffer_id="buf-2",
        result=AnalysisBufferCleanedResult(
            result_id="res-1",
            result_type=AnalysisBufferResultType.STANDARD_AI_RESULT,
            original_request_id="orig-1",
        ),
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.RESULT_RECEIVED
    assert updated.result_arrived() is True
    assert updated.sufficient_for_analysis is False


def test_add_missing_information_request_marks_needs_more_data():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-3"))

    updated = store.add_missing_information_request(
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


def test_mark_sufficient_for_analysis():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-4"))

    updated = store.mark_sufficient_for_analysis(
        buffer_id="buf-4",
        readiness_level=AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS
    assert updated.sufficient_for_analysis is True
    assert updated.can_close_waiting_state() is True


def test_mark_governance_blocked():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-5"))

    updated = store.mark_governance_blocked(
        buffer_id="buf-5",
        reason="Governance denied continuation",
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE
    assert updated.governance_block_reason == "Governance denied continuation"


def test_mark_cancelled_by_human():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-6"))

    updated = store.mark_cancelled_by_human(
        buffer_id="buf-6",
        reason="Human confirmed task is no longer relevant",
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.CANCELLED_BY_HUMAN
    assert updated.cancellation_reason == (
        "Human confirmed task is no longer relevant"
    )


def test_mark_expired_unresolved():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-7"))

    updated = store.mark_expired_unresolved(
        buffer_id="buf-7",
        reason="Context window expired without sufficient data",
    )

    assert updated is not None
    assert updated.status == AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED
    assert updated.expiration_reason == (
        "Context window expired without sufficient data"
    )
    assert updated.sufficient_for_analysis is False


def test_list_waiting_includes_result_received_and_needs_more_data():
    store = AnalysisBufferStore()

    store.add_entry(make_entry("waiting"))

    store.add_entry(make_entry("received"))
    store.attach_cleaned_result(
        "received",
        AnalysisBufferCleanedResult(
            result_id="res-2",
            result_type=AnalysisBufferResultType.CLEANED_EXTERNAL_RESULT,
            original_request_id="orig-1",
        ),
    )

    store.add_entry(make_entry("needs-more"))
    store.mark_needs_more_data("needs-more")

    ids = {entry.buffer_id for entry in store.list_waiting()}

    assert ids == {"waiting", "received", "needs-more"}


def test_list_open_excludes_closed_operational_states():
    store = AnalysisBufferStore()

    store.add_entry(make_entry("open-waiting"))

    store.add_entry(make_entry("closed-sufficient"))
    store.mark_sufficient_for_analysis(
        "closed-sufficient",
        AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
    )

    store.add_entry(make_entry("closed-expired"))
    store.mark_expired_unresolved(
        "closed-expired",
        "Expired but unresolved",
    )

    ids = {entry.buffer_id for entry in store.list_open()}

    assert ids == {"open-waiting"}


def test_list_unresolved_includes_needs_more_data_and_expired_unresolved():
    store = AnalysisBufferStore()

    store.add_entry(make_entry("needs-more"))
    store.mark_needs_more_data("needs-more")

    store.add_entry(make_entry("expired"))
    store.mark_expired_unresolved(
        "expired",
        "Expired unresolved",
    )

    ids = {entry.buffer_id for entry in store.list_unresolved()}

    assert ids == {"needs-more", "expired"}


def test_remove_entry():
    store = AnalysisBufferStore()
    store.add_entry(make_entry("buf-remove"))

    assert store.remove_entry("buf-remove") is True
    assert store.get_entry("buf-remove") is None
    assert store.remove_entry("buf-remove") is False