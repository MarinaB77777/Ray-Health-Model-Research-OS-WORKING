import pytest

from runtime.analysis_buffer.contracts import (
    ANALYSIS_BUFFER_INVARIANTS,
    AnalysisBufferCleanedResult,
    AnalysisBufferEntry,
    AnalysisBufferOriginalRequest,
    AnalysisBufferResultType,
    AnalysisBufferSanitizedRequest,
    AnalysisBufferStatus,
    AnalysisReadinessLevel,
    MissingInformationRequest,
    MissingInformationSource,
)


def make_original_request() -> AnalysisBufferOriginalRequest:
    return AnalysisBufferOriginalRequest(
        original_request_id="orig-1",
        original_question="Private internal question",
        expected_answer_scope="bounded answer scope",
        task_table_ref="task-table-1",
    )


def test_result_arrival_is_not_sufficiency():
    entry = AnalysisBufferEntry(
        buffer_id="buf-1",
        original_request=make_original_request(),
        cleaned_results=[
            AnalysisBufferCleanedResult(
                result_id="res-1",
                result_type=AnalysisBufferResultType.STANDARD_AI_RESULT,
                original_request_id="orig-1",
            )
        ],
    )

    assert entry.result_arrived() is True
    assert entry.sufficient_for_analysis is False
    assert entry.status == AnalysisBufferStatus.WAITING_FOR_RESULT


def test_sufficient_for_analysis_requires_readiness_above_not_ready():
    with pytest.raises(ValueError):
        AnalysisBufferEntry(
            buffer_id="buf-2",
            original_request=make_original_request(),
            sufficient_for_analysis=True,
            readiness_level=AnalysisReadinessLevel.NOT_READY,
        )


def test_sufficient_status_requires_sufficient_flag():
    with pytest.raises(ValueError):
        AnalysisBufferEntry(
            buffer_id="buf-3",
            original_request=make_original_request(),
            status=AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS,
            readiness_level=AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
            sufficient_for_analysis=False,
        )


def test_valid_sufficient_for_analysis_entry():
    entry = AnalysisBufferEntry(
        buffer_id="buf-4",
        original_request=make_original_request(),
        status=AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS,
        readiness_level=AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
        sufficient_for_analysis=True,
    )

    assert entry.can_close_waiting_state() is True


def test_missing_information_cannot_be_required_and_optional():
    with pytest.raises(ValueError):
        MissingInformationRequest(
            request_id="missing-1",
            source=MissingInformationSource.HUMAN,
            reason="Need clarification",
            required=True,
            optional=True,
        )


def test_missing_information_marks_needs_more_data():
    entry = AnalysisBufferEntry(
        buffer_id="buf-5",
        original_request=make_original_request(),
        missing_information_requests=[
            MissingInformationRequest(
                request_id="missing-2",
                source=MissingInformationSource.SENSOR,
                reason="Need fresh sensor data",
            )
        ],
    )

    assert entry.needs_more_data() is True


def test_governance_block_requires_reason():
    with pytest.raises(ValueError):
        AnalysisBufferEntry(
            buffer_id="buf-6",
            original_request=make_original_request(),
            status=AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE,
        )


def test_cancelled_by_human_requires_reason():
    with pytest.raises(ValueError):
        AnalysisBufferEntry(
            buffer_id="buf-7",
            original_request=make_original_request(),
            status=AnalysisBufferStatus.CANCELLED_BY_HUMAN,
        )


def test_expired_but_unresolved_requires_reason():
    with pytest.raises(ValueError):
        AnalysisBufferEntry(
            buffer_id="buf-8",
            original_request=make_original_request(),
            status=AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED,
        )


def test_expired_but_unresolved_closes_waiting_operationally():
    entry = AnalysisBufferEntry(
        buffer_id="buf-9",
        original_request=make_original_request(),
        status=AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED,
        expiration_reason="Context window expired without sufficient data.",
    )

    assert entry.can_close_waiting_state() is True
    assert entry.sufficient_for_analysis is False


def test_original_and_sanitized_requests_are_separated():
    original = make_original_request()

    sanitized = AnalysisBufferSanitizedRequest(
        sanitized_request_id="san-1",
        original_request_id=original.original_request_id,
        sanitized_question="Sanitized external-safe question",
        removed_private_context=True,
        external_exposure_allowed=True,
    )

    entry = AnalysisBufferEntry(
        buffer_id="buf-10",
        original_request=original,
        sanitized_request=sanitized,
    )

    assert entry.original_request.original_question == "Private internal question"
    assert entry.sanitized_request is not None
    assert entry.sanitized_request.sanitized_question == (
        "Sanitized external-safe question"
    )
    assert entry.sanitized_request.removed_private_context is True


def test_cleaned_result_is_not_verified_truth_by_default():
    result = AnalysisBufferCleanedResult(
        result_id="res-2",
        result_type=AnalysisBufferResultType.CLEANED_EXTERNAL_RESULT,
        original_request_id="orig-1",
    )

    assert result.result_is_verified_truth is False
    assert result.result_is_sufficient_for_analysis is False


def test_analysis_buffer_invariants_present():
    invariant_names = {
        invariant.name
        for invariant in ANALYSIS_BUFFER_INVARIANTS
    }

    assert "analysis_buffer_is_not_memory" in invariant_names
    assert "analysis_buffer_is_not_truth_authority" in invariant_names
    assert "result_arrival_is_not_sufficiency" in invariant_names
    assert "external_result_is_not_ray_truth" in invariant_names
    assert "expiration_is_not_fake_completion" in invariant_names
    assert "no_data_requires_acquisition_or_clarification" in invariant_names
    assert "original_request_stays_private" in invariant_names