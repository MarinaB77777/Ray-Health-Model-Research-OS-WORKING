# runtime/acquisition/retry_policy.py

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class RetryTrigger(str, Enum):
    NO_RESPONSE = "no_response"
    INSUFFICIENT_DATA = "insufficient_data"
    SOURCE_FAILED = "source_failed"
    SOURCE_TIMEOUT = "source_timeout"
    LOW_SOURCE_QUALITY = "low_source_quality"
    CHANNEL_FAILURE_SUSPECTED = "channel_failure_suspected"
    UNCLEAR_REQUEST = "unclear_request"


class RetryNextStep(str, Enum):
    RETRY_SAME_SOURCE = "retry_same_source"
    RETRY_LATER = "retry_later"
    ASK_HUMAN_CLARIFICATION = "ask_human_clarification"
    SWITCH_SOURCE = "switch_source"
    REFORMULATE_REQUEST = "reformulate_request"
    CHECK_CHANNEL_OR_SOURCE_FAILURE = "check_channel_or_source_failure"
    MARK_UNRESOLVED = "mark_unresolved"
    BLOCKED_BY_POLICY = "blocked_by_policy"


class RetryReasonCode(str, Enum):
    RETRY_IS_NOT_EXECUTION = "retry_is_not_execution"
    RETRY_IS_NOT_PRESSURE = "retry_is_not_pressure"
    RETRY_IS_NOT_FAKE_COMPLETION = "retry_is_not_fake_completion"
    NO_RESPONSE_IS_NOT_TASK_SOLVED = "no_response_is_not_task_solved"
    NO_RESPONSE_IS_NOT_CANCEL_PERMISSION = (
        "no_response_is_not_cancel_permission"
    )
    TOO_MANY_ATTEMPTS = "too_many_attempts"
    SOURCE_FAILURE_SHOULD_BE_CHECKED = "source_failure_should_be_checked"
    REQUEST_SHOULD_BE_REFORMULATED = "request_should_be_reformulated"
    HUMAN_CLARIFICATION_NEEDED = "human_clarification_needed"
    SOURCE_SWITCH_RECOMMENDED = "source_switch_recommended"
    UNRESOLVED_STATE_RECOMMENDED = "unresolved_state_recommended"
    POLICY_BLOCKS_RETRY = "policy_blocks_retry"


class RetryPolicyInput(BaseModel):
    trigger: RetryTrigger

    attempt_count: int = 0
    max_attempts: int = 2

    source_available: bool = True
    channel_available: bool = True

    request_clear: bool = True
    alternative_source_available: bool = False

    policy_allows_retry: bool = True
    human_clarification_possible: bool = True

    @model_validator(mode="after")
    def validate_retry_counts(self) -> "RetryPolicyInput":
        if self.attempt_count < 0:
            raise ValueError("attempt_count must be >= 0")

        if self.max_attempts < 0:
            raise ValueError("max_attempts must be >= 0")

        if self.attempt_count > self.max_attempts:
            raise ValueError("attempt_count must not exceed max_attempts")

        return self


class RetryPolicyDecision(BaseModel):
    next_step: RetryNextStep
    reason_codes: list[RetryReasonCode] = Field(default_factory=list)

    should_execute_retry: bool = False
    requires_human: bool = False
    requires_governance: bool = False

    notes: list[str] = Field(default_factory=list)


class RetryPolicy:
    """
    Bounded acquisition retry policy.

    This module provides decision/guidance only.

    It is NOT:
    - retry executor;
    - acquisition executor;
    - planner;
    - Runtime authority;
    - Analyst;
    - Governance;
    - truth authority;
    - cancellation authority.

    retry ≠ pressure
    retry ≠ infinite loop
    retry ≠ fake completion
    no response ≠ task solved
    no response ≠ permission to cancel
    """

    def decide(
        self,
        policy_input: RetryPolicyInput,
    ) -> RetryPolicyDecision:
        if not policy_input.policy_allows_retry:
            return RetryPolicyDecision(
                next_step=RetryNextStep.BLOCKED_BY_POLICY,
                reason_codes=[
                    RetryReasonCode.POLICY_BLOCKS_RETRY,
                    RetryReasonCode.RETRY_IS_NOT_EXECUTION,
                ],
                requires_governance=True,
            )

        if policy_input.attempt_count >= policy_input.max_attempts:
            return RetryPolicyDecision(
                next_step=RetryNextStep.MARK_UNRESOLVED,
                reason_codes=[
                    RetryReasonCode.TOO_MANY_ATTEMPTS,
                    RetryReasonCode.UNRESOLVED_STATE_RECOMMENDED,
                    RetryReasonCode.RETRY_IS_NOT_FAKE_COMPLETION,
                ],
            )

        if not policy_input.source_available or not policy_input.channel_available:
            return RetryPolicyDecision(
                next_step=RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE,
                reason_codes=[
                    RetryReasonCode.SOURCE_FAILURE_SHOULD_BE_CHECKED,
                    RetryReasonCode.NO_RESPONSE_IS_NOT_TASK_SOLVED,
                ],
            )

        if not policy_input.request_clear:
            if policy_input.human_clarification_possible:
                return RetryPolicyDecision(
                    next_step=RetryNextStep.ASK_HUMAN_CLARIFICATION,
                    reason_codes=[
                        RetryReasonCode.HUMAN_CLARIFICATION_NEEDED,
                        RetryReasonCode.REQUEST_SHOULD_BE_REFORMULATED,
                    ],
                    requires_human=True,
                )

            return RetryPolicyDecision(
                next_step=RetryNextStep.REFORMULATE_REQUEST,
                reason_codes=[
                    RetryReasonCode.REQUEST_SHOULD_BE_REFORMULATED,
                    RetryReasonCode.RETRY_IS_NOT_PRESSURE,
                ],
            )

        if policy_input.trigger in {
            RetryTrigger.LOW_SOURCE_QUALITY,
            RetryTrigger.SOURCE_FAILED,
        }:
            if policy_input.alternative_source_available:
                return RetryPolicyDecision(
                    next_step=RetryNextStep.SWITCH_SOURCE,
                    reason_codes=[
                        RetryReasonCode.SOURCE_SWITCH_RECOMMENDED,
                    ],
                )

            return RetryPolicyDecision(
                next_step=RetryNextStep.RETRY_LATER,
                reason_codes=[
                    RetryReasonCode.SOURCE_FAILURE_SHOULD_BE_CHECKED,
                    RetryReasonCode.RETRY_IS_NOT_PRESSURE,
                ],
            )

        if policy_input.trigger in {
            RetryTrigger.NO_RESPONSE,
            RetryTrigger.SOURCE_TIMEOUT,
            RetryTrigger.CHANNEL_FAILURE_SUSPECTED,
        }:
            return RetryPolicyDecision(
                next_step=RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE,
                reason_codes=[
                    RetryReasonCode.NO_RESPONSE_IS_NOT_TASK_SOLVED,
                    RetryReasonCode.NO_RESPONSE_IS_NOT_CANCEL_PERMISSION,
                    RetryReasonCode.SOURCE_FAILURE_SHOULD_BE_CHECKED,
                ],
            )

        if policy_input.trigger == RetryTrigger.INSUFFICIENT_DATA:
            if policy_input.human_clarification_possible:
                return RetryPolicyDecision(
                    next_step=RetryNextStep.ASK_HUMAN_CLARIFICATION,
                    reason_codes=[
                        RetryReasonCode.HUMAN_CLARIFICATION_NEEDED,
                    ],
                    requires_human=True,
                )

            if policy_input.alternative_source_available:
                return RetryPolicyDecision(
                    next_step=RetryNextStep.SWITCH_SOURCE,
                    reason_codes=[
                        RetryReasonCode.SOURCE_SWITCH_RECOMMENDED,
                    ],
                )

            return RetryPolicyDecision(
                next_step=RetryNextStep.MARK_UNRESOLVED,
                reason_codes=[
                    RetryReasonCode.UNRESOLVED_STATE_RECOMMENDED,
                ],
            )

        return RetryPolicyDecision(
            next_step=RetryNextStep.MARK_UNRESOLVED,
            reason_codes=[
                RetryReasonCode.UNRESOLVED_STATE_RECOMMENDED,
            ],
        )