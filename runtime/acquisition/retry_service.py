# runtime/acquisition/retry_service.py

from __future__ import annotations

from runtime.acquisition.retry_policy import (
    RetryPolicy,
    RetryPolicyDecision,
    RetryPolicyInput,
    RetryTrigger,
)


class RetryService:
    """
    Retry Service.

    This service centralizes bounded retry guidance calls.

    It is NOT:
    - retry executor;
    - acquisition executor;
    - planner;
    - Runtime authority;
    - Governance;
    - cancellation authority;
    - acquisition transport.

    retry_service ≠ executor
    retry_service ≠ planner
    retry_service ≠ Runtime authority
    """

    def __init__(
        self,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.retry_policy = retry_policy or RetryPolicy()

    def decide(
        self,
        policy_input: RetryPolicyInput,
    ) -> RetryPolicyDecision:
        return self.retry_policy.decide(policy_input)

    def handle_no_response(
        self,
        attempt_count: int = 0,
        max_attempts: int = 2,
        source_available: bool = True,
        channel_available: bool = True,
    ) -> RetryPolicyDecision:
        return self.retry_policy.decide(
            RetryPolicyInput(
                trigger=RetryTrigger.NO_RESPONSE,
                attempt_count=attempt_count,
                max_attempts=max_attempts,
                source_available=source_available,
                channel_available=channel_available,
            )
        )

    def handle_insufficient_data(
        self,
        attempt_count: int = 0,
        max_attempts: int = 2,
        human_clarification_possible: bool = True,
        alternative_source_available: bool = False,
    ) -> RetryPolicyDecision:
        return self.retry_policy.decide(
            RetryPolicyInput(
                trigger=RetryTrigger.INSUFFICIENT_DATA,
                attempt_count=attempt_count,
                max_attempts=max_attempts,
                human_clarification_possible=human_clarification_possible,
                alternative_source_available=alternative_source_available,
            )
        )

    def handle_source_failure(
        self,
        attempt_count: int = 0,
        max_attempts: int = 2,
        alternative_source_available: bool = False,
    ) -> RetryPolicyDecision:
        return self.retry_policy.decide(
            RetryPolicyInput(
                trigger=RetryTrigger.SOURCE_FAILED,
                attempt_count=attempt_count,
                max_attempts=max_attempts,
                alternative_source_available=alternative_source_available,
            )
        )

    def handle_retry_blocked(
        self,
    ) -> RetryPolicyDecision:
        return self.retry_policy.decide(
            RetryPolicyInput(
                trigger=RetryTrigger.NO_RESPONSE,
                attempt_count=0,
                max_attempts=0,
                policy_allows_retry=False,
            )
        )