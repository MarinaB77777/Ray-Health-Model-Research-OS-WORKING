# runtime/acquisition/retry_bridge.py

from __future__ import annotations

from runtime.acquisition.retry_policy import RetryPolicyDecision
from runtime.acquisition.retry_service import RetryService
from runtime.analysis_buffer.contracts import (
    AnalysisBufferEntry,
    AnalysisBufferStatus,
)


class RetryBridge:
    """
    Analysis Buffer ↔ Retry Service bridge.

    This bridge maps acquisition/buffer problem states
    to bounded retry guidance.

    It is NOT:
    - executor;
    - planner;
    - buffer mutator;
    - cancellation authority;
    - acquisition transport;
    - Runtime authority;
    - Governance;
    - Analyst.

    retry_bridge ≠ executor
    retry_bridge ≠ planner
    retry_bridge ≠ buffer mutator

    It returns guidance only.

    RESULT_RECEIVED ≠ no response.
    EXPIRED_BUT_UNRESOLVED ≠ cancellation authority.
    """

    def __init__(
        self,
        retry_service: RetryService | None = None,
    ) -> None:
        self.retry_service = retry_service or RetryService()

    def handle_buffer_state(
        self,
        buffer_entry: AnalysisBufferEntry,
        attempt_count: int = 0,
        max_attempts: int = 2,
    ) -> RetryPolicyDecision:
        if buffer_entry.status == AnalysisBufferStatus.NEEDS_MORE_DATA:
            return self.retry_service.handle_insufficient_data(
                attempt_count=attempt_count,
                max_attempts=max_attempts,
                human_clarification_possible=True,
            )

        if buffer_entry.status == AnalysisBufferStatus.WAITING_FOR_RESULT:
            return self.retry_service.handle_no_response(
                attempt_count=attempt_count,
                max_attempts=max_attempts,
            )

        if buffer_entry.status == (
            AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED
        ):
            return self.retry_service.handle_no_response(
                attempt_count=max_attempts,
                max_attempts=max_attempts,
            )

        if buffer_entry.status in {
            AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE,
            AnalysisBufferStatus.CANCELLED_BY_HUMAN,
            AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS,
            AnalysisBufferStatus.RESULT_RECEIVED,
        }:
            return self.retry_service.handle_retry_blocked()

        return self.retry_service.handle_retry_blocked()