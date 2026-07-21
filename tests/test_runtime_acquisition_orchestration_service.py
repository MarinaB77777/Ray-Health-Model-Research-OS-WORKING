# tests/test_runtime_acquisition_orchestration_service.py

from datetime import timedelta

import pytest

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationService,
    RuntimeAcquisitionOrchestrationState,
    RuntimeAcquisitionOrchestrationStatus,
)


class FakeRuntimeRequest:
    runtime_request_id = "runtime_1"


class FakeAcquisitionRequest:
    request_id = "acq_1"


class FakeRequestBuilder:
    def build_dialogue_question_request(
        self,
        coordinator_output,
        variable_code,
        reason,
    ):
        return FakeRuntimeRequest()


class FakeBridge:
    def create_from_runtime_request(self, runtime_request):
        return FakeAcquisitionRequest()


class FailingBridge:
    def create_from_runtime_request(self, runtime_request):
        raise RuntimeError("bridge failed")


def test_orchestrate_dialogue_question_success_goes_to_waiting():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    assert result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert result.acquisition_request_id == "acq_1"
    assert result.unresolved is False
    assert result.invariants["waiting_is_not_answered"] is True
    assert result.invariants["automatic_routing_is_not_automatic_authority"] is True


def test_bridge_error_goes_to_blocked_and_unresolved():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FailingBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    assert result.status == RuntimeAcquisitionOrchestrationStatus.BLOCKED
    assert result.unresolved is True
    assert result.blocked_reason == "bridge_error"
    assert "bridge failed" in result.last_error


def test_cleanup_expired_marks_open_state_expired_not_deleted():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    state = service._states[result.orchestration_id]
    expired_state = service._revalidate_state(
        state.model_copy(
            update={
                "created_at": service._now() - timedelta(minutes=60),
                "expires_at": service._now() - timedelta(minutes=1),
            }            
        )
    )
    service._states[result.orchestration_id] = expired_state

    expired_ids = service.cleanup_expired()

    assert result.orchestration_id in expired_ids
    assert result.orchestration_id in service._states
    assert (
        service._states[result.orchestration_id].status
        == RuntimeAcquisitionOrchestrationStatus.EXPIRED
    )
    assert service._states[result.orchestration_id].unresolved is True


def test_cleanup_expired_does_not_overwrite_blocked_state():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FailingBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    state = service._states[result.orchestration_id]
    expired_blocked_state = service._revalidate_state(
        state.model_copy(
            update={
                "created_at": service._now() - timedelta(minutes=60),
                "expires_at": service._now() - timedelta(minutes=1),
            }
        )
    )
    service._states[result.orchestration_id] = expired_blocked_state

    expired_ids = service.cleanup_expired()

    assert result.orchestration_id not in expired_ids
    assert (
        service._states[result.orchestration_id].status
        == RuntimeAcquisitionOrchestrationStatus.BLOCKED
    )


def test_list_unresolved_includes_waiting_blocked_and_expired():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    waiting_result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    state = service._states[waiting_result.orchestration_id]
    expired_state = service._revalidate_state(
        state.model_copy(
            update={
                "status": RuntimeAcquisitionOrchestrationStatus.EXPIRED,
                "unresolved": True,
            }
        )
    )
    service._states[waiting_result.orchestration_id] = expired_state

    unresolved = service.list_unresolved()

    assert len(unresolved) == 1
    assert unresolved[0].status == RuntimeAcquisitionOrchestrationStatus.EXPIRED


def test_list_unresolved_returns_deepcopy():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    unresolved = service.list_unresolved()
    unresolved[0].retry_count = 99

    assert service._states[result.orchestration_id].retry_count == 0


def test_invalid_ttl_is_rejected():
    with pytest.raises(ValueError, match="ttl_minutes must be > 0"):
        RuntimeAcquisitionOrchestrationService(
            request_builder=FakeRequestBuilder(),
            acquisition_bridge=FakeBridge(),
            ttl_minutes=0,
        )


def test_state_rejects_empty_ids():
    now = RuntimeAcquisitionOrchestrationService._now()

    with pytest.raises(ValueError, match="ids must not be empty"):
        RuntimeAcquisitionOrchestrationState(
            orchestration_id="",
            runtime_request_id="runtime_1",
            status=RuntimeAcquisitionOrchestrationStatus.CREATED,
            created_at=now,
            expires_at=now + timedelta(minutes=1),
        )


def test_state_rejects_negative_retry_count():
    now = RuntimeAcquisitionOrchestrationService._now()

    with pytest.raises(ValueError, match="retry_count must be >= 0"):
        RuntimeAcquisitionOrchestrationState(
            orchestration_id="orch_1",
            runtime_request_id="runtime_1",
            status=RuntimeAcquisitionOrchestrationStatus.CREATED,
            created_at=now,
            expires_at=now + timedelta(minutes=1),
            retry_count=-1,
        )


def test_state_rejects_invalid_expiration_window():
    now = RuntimeAcquisitionOrchestrationService._now()

    with pytest.raises(ValueError, match="expires_at must be after created_at"):
        RuntimeAcquisitionOrchestrationState(
            orchestration_id="orch_1",
            runtime_request_id="runtime_1",
            status=RuntimeAcquisitionOrchestrationStatus.CREATED,
            created_at=now,
            expires_at=now,
        )


def test_blocked_requires_reason_or_error():
    now = RuntimeAcquisitionOrchestrationService._now()

    with pytest.raises(
        ValueError,
        match="BLOCKED state requires blocked_reason or last_error",
    ):
        RuntimeAcquisitionOrchestrationState(
            orchestration_id="orch_1",
            runtime_request_id="runtime_1",
            status=RuntimeAcquisitionOrchestrationStatus.BLOCKED,
            created_at=now,
            expires_at=now + timedelta(minutes=1),
        )


def test_expired_requires_unresolved_true():
    now = RuntimeAcquisitionOrchestrationService._now()

    with pytest.raises(
        ValueError,
        match="UNRESOLVED/EXPIRED state requires unresolved=True",
    ):
        RuntimeAcquisitionOrchestrationState(
            orchestration_id="orch_1",
            runtime_request_id="runtime_1",
            status=RuntimeAcquisitionOrchestrationStatus.EXPIRED,
            created_at=now,
            expires_at=now + timedelta(minutes=1),
            unresolved=False,
        )

def test_mark_retry_attempt_increments_retry_count_without_execution():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    retry_result = service.mark_retry_attempt(
        result.orchestration_id,
        last_error="temporary failure",
        max_retry_count=2,
    )

    assert retry_result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert retry_result.unresolved is False
    assert service._states[result.orchestration_id].retry_count == 1
    assert service._states[result.orchestration_id].last_error == "temporary failure"
    assert retry_result.invariants["retry_visibility_is_not_retry_authority"] is True
    assert retry_result.invariants["retry_tracking_is_not_retry_execution"] is True


def test_mark_retry_attempt_marks_unresolved_at_limit():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    retry_result = service.mark_retry_attempt(
        result.orchestration_id,
        last_error="second failure",
        max_retry_count=1,
    )

    assert retry_result.status == RuntimeAcquisitionOrchestrationStatus.UNRESOLVED
    assert retry_result.unresolved is True
    assert service._states[result.orchestration_id].retry_count == 1
    assert service._states[result.orchestration_id].last_error == "second failure"


def test_mark_retry_attempt_rejects_negative_max_retry_count():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=None,
        variable_code="k1",
        reason="missing answer",
    )

    with pytest.raises(ValueError, match="max_retry_count must be >= 0"):
        service.mark_retry_attempt(
            result.orchestration_id,
            max_retry_count=-1,
        )


def test_mark_retry_attempt_rejects_unknown_orchestration_id():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=FakeRequestBuilder(),
        acquisition_bridge=FakeBridge(),
    )

    with pytest.raises(
        KeyError,
        match="RuntimeAcquisitionOrchestrationState not found",
    ):
        service.mark_retry_attempt("missing_orchestration_id")