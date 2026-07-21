from runtime.acquisition.retry_bridge import RetryBridge
from runtime.acquisition.retry_policy import RetryNextStep
from runtime.analysis_buffer.contracts import (
    AnalysisBufferEntry,
    AnalysisBufferOriginalRequest,
    AnalysisBufferStatus,
)


def make_buffer_entry(
    status: AnalysisBufferStatus,
) -> AnalysisBufferEntry:
    kwargs = {}

    if status == AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE:
        kwargs["governance_block_reason"] = "blocked"

    if status == AnalysisBufferStatus.CANCELLED_BY_HUMAN:
        kwargs["cancellation_reason"] = "cancelled"

    if status == AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED:
        kwargs["expiration_reason"] = "expired"

    if status == AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS:
        kwargs["sufficient_for_analysis"] = True
        # Must be above NOT_READY for contract validation.
        from runtime.analysis_buffer.contracts import AnalysisReadinessLevel

        kwargs["readiness_level"] = (
            AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY
        )

    return AnalysisBufferEntry(
        buffer_id="buffer-1",
        status=status,
        original_request=AnalysisBufferOriginalRequest(
            original_request_id="orig-1",
            original_question="Private question",
        ),
        **kwargs,
    )


def test_waiting_for_result_checks_channel_or_source_failure():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.WAITING_FOR_RESULT)
    )

    assert decision.next_step == RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE
    assert decision.should_execute_retry is False


def test_needs_more_data_asks_human_clarification():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.NEEDS_MORE_DATA)
    )

    assert decision.next_step == RetryNextStep.ASK_HUMAN_CLARIFICATION
    assert decision.requires_human is True


def test_expired_unresolved_marks_unresolved_not_cancelled():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED)
    )

    assert decision.next_step == RetryNextStep.MARK_UNRESOLVED
    assert decision.should_execute_retry is False


def test_result_received_blocks_retry_guidance():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.RESULT_RECEIVED)
    )

    assert decision.next_step == RetryNextStep.BLOCKED_BY_POLICY
    assert decision.requires_governance is True
    assert decision.should_execute_retry is False


def test_sufficient_for_analysis_blocks_retry_guidance():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS)
    )

    assert decision.next_step == RetryNextStep.BLOCKED_BY_POLICY
    assert decision.requires_governance is True


def test_blocked_by_governance_blocks_retry_guidance():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE)
    )

    assert decision.next_step == RetryNextStep.BLOCKED_BY_POLICY
    assert decision.requires_governance is True


def test_cancelled_by_human_blocks_retry_guidance():
    bridge = RetryBridge()

    decision = bridge.handle_buffer_state(
        make_buffer_entry(AnalysisBufferStatus.CANCELLED_BY_HUMAN)
    )

    assert decision.next_step == RetryNextStep.BLOCKED_BY_POLICY
    assert decision.requires_governance is True


def test_retry_bridge_does_not_mutate_buffer():
    bridge = RetryBridge()
    buffer_entry = make_buffer_entry(
        AnalysisBufferStatus.WAITING_FOR_RESULT
    )

    original_status = buffer_entry.status
    original_readiness = buffer_entry.readiness_level
    original_results = list(buffer_entry.cleaned_results)

    bridge.handle_buffer_state(buffer_entry)

    assert buffer_entry.status == original_status
    assert buffer_entry.readiness_level == original_readiness
    assert buffer_entry.cleaned_results == original_results