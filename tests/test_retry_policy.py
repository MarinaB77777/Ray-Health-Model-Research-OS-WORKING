import pytest

from runtime.acquisition.retry_policy import (
    RetryNextStep,
    RetryPolicy,
    RetryPolicyInput,
    RetryReasonCode,
    RetryTrigger,
)


def test_no_response_checks_channel_or_source_failure():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
        )
    )

    assert decision.next_step == RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE
    assert RetryReasonCode.NO_RESPONSE_IS_NOT_TASK_SOLVED in decision.reason_codes
    assert RetryReasonCode.NO_RESPONSE_IS_NOT_CANCEL_PERMISSION in decision.reason_codes
    assert decision.should_execute_retry is False


def test_insufficient_data_asks_human_when_possible():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.INSUFFICIENT_DATA,
            human_clarification_possible=True,
        )
    )

    assert decision.next_step == RetryNextStep.ASK_HUMAN_CLARIFICATION
    assert decision.requires_human is True
    assert RetryReasonCode.HUMAN_CLARIFICATION_NEEDED in decision.reason_codes


def test_too_many_attempts_marks_unresolved():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
            attempt_count=2,
            max_attempts=2,
        )
    )

    assert decision.next_step == RetryNextStep.MARK_UNRESOLVED
    assert RetryReasonCode.TOO_MANY_ATTEMPTS in decision.reason_codes
    assert RetryReasonCode.RETRY_IS_NOT_FAKE_COMPLETION in decision.reason_codes


def test_policy_blocked_requires_governance():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
            policy_allows_retry=False,
        )
    )

    assert decision.next_step == RetryNextStep.BLOCKED_BY_POLICY
    assert decision.requires_governance is True
    assert RetryReasonCode.POLICY_BLOCKS_RETRY in decision.reason_codes


def test_unclear_request_asks_human_when_possible():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.UNCLEAR_REQUEST,
            request_clear=False,
            human_clarification_possible=True,
        )
    )

    assert decision.next_step == RetryNextStep.ASK_HUMAN_CLARIFICATION
    assert decision.requires_human is True


def test_unclear_request_reformulates_when_human_not_possible():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.UNCLEAR_REQUEST,
            request_clear=False,
            human_clarification_possible=False,
        )
    )

    assert decision.next_step == RetryNextStep.REFORMULATE_REQUEST
    assert RetryReasonCode.REQUEST_SHOULD_BE_REFORMULATED in decision.reason_codes


def test_low_source_quality_switches_source_when_available():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.LOW_SOURCE_QUALITY,
            alternative_source_available=True,
        )
    )

    assert decision.next_step == RetryNextStep.SWITCH_SOURCE
    assert RetryReasonCode.SOURCE_SWITCH_RECOMMENDED in decision.reason_codes


def test_source_failed_retries_later_when_no_alternative():
    policy = RetryPolicy()

    decision = policy.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.SOURCE_FAILED,
            alternative_source_available=False,
        )
    )

    assert decision.next_step == RetryNextStep.RETRY_LATER
    assert RetryReasonCode.RETRY_IS_NOT_PRESSURE in decision.reason_codes


def test_negative_attempt_count_is_invalid():
    with pytest.raises(ValueError):
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
            attempt_count=-1,
        )


def test_negative_max_attempts_is_invalid():
    with pytest.raises(ValueError):
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
            max_attempts=-1,
        )


def test_attempt_count_must_not_exceed_max_attempts():
    with pytest.raises(ValueError):
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
            attempt_count=3,
            max_attempts=2,
        )