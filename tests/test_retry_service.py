from runtime.acquisition.retry_policy import (
    RetryNextStep,
    RetryPolicyInput,
    RetryReasonCode,
    RetryTrigger,
)

from runtime.acquisition.retry_service import RetryService


def test_retry_service_decide_delegates_to_policy():
    service = RetryService()

    decision = service.decide(
        RetryPolicyInput(
            trigger=RetryTrigger.NO_RESPONSE,
        )
    )

    assert decision.next_step == RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE
    assert decision.should_execute_retry is False


def test_handle_no_response_checks_channel_or_source_failure():
    service = RetryService()

    decision = service.handle_no_response()

    assert decision.next_step == RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE
    assert RetryReasonCode.NO_RESPONSE_IS_NOT_TASK_SOLVED in decision.reason_codes
    assert decision.should_execute_retry is False


def test_handle_no_response_with_unavailable_source_checks_failure():
    service = RetryService()

    decision = service.handle_no_response(
        source_available=False,
    )

    assert decision.next_step == RetryNextStep.CHECK_CHANNEL_OR_SOURCE_FAILURE
    assert RetryReasonCode.SOURCE_FAILURE_SHOULD_BE_CHECKED in decision.reason_codes


def test_handle_insufficient_data_asks_human_when_possible():
    service = RetryService()

    decision = service.handle_insufficient_data(
        human_clarification_possible=True,
    )

    assert decision.next_step == RetryNextStep.ASK_HUMAN_CLARIFICATION
    assert decision.requires_human is True


def test_handle_insufficient_data_switches_source_when_human_not_possible():
    service = RetryService()

    decision = service.handle_insufficient_data(
        human_clarification_possible=False,
        alternative_source_available=True,
    )

    assert decision.next_step == RetryNextStep.SWITCH_SOURCE
    assert RetryReasonCode.SOURCE_SWITCH_RECOMMENDED in decision.reason_codes


def test_handle_source_failure_switches_source_when_available():
    service = RetryService()

    decision = service.handle_source_failure(
        alternative_source_available=True,
    )

    assert decision.next_step == RetryNextStep.SWITCH_SOURCE


def test_handle_source_failure_retries_later_without_alternative():
    service = RetryService()

    decision = service.handle_source_failure(
        alternative_source_available=False,
    )

    assert decision.next_step == RetryNextStep.RETRY_LATER
    assert decision.should_execute_retry is False