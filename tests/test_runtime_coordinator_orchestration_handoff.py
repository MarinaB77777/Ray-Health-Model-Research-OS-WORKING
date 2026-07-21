# tests/test_runtime_coordinator_orchestration_handoff.py

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationService,
    RuntimeAcquisitionOrchestrationStatus,
)
from runtime.acquisition.runtime_bridge import AcquisitionRuntimeBridge
from runtime.acquisition.runtime_request_builder import (
    RuntimeAcquisitionRequestBuilder,
)
from runtime.coordinator.contracts import CoordinatorOutput, CoordinatorStatus


def _make_coordinator_output() -> CoordinatorOutput:
    return CoordinatorOutput(
        coordinator_id="coord_handoff_1",
        action_id="action_handoff_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )


def test_coordinator_handoff_to_orchestration_does_not_complete_runtime_task():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=_make_coordinator_output(),
        variable_code="k23",
        reason="missing critical marker",
    )

    assert result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert result.acquisition_request_id
    assert result.unresolved is False

    assert result.invariants["waiting_is_not_answered"] is True
    assert result.invariants["waiting_is_not_acquired"] is True
    assert result.invariants["acquisition_request_is_not_acquisition_result"] is True
    assert result.invariants["automatic_routing_is_not_automatic_authority"] is True
    assert result.invariants["prepared_is_not_executed"] is True

class FailingBridge:
    def create_from_runtime_request(self, runtime_request):
        raise RuntimeError("handoff transport failure")


def test_coordinator_handoff_failure_does_not_cancel_runtime_task():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=FailingBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=_make_coordinator_output(),
        variable_code="k24",
        reason="missing safety marker",
    )

    assert result.status == RuntimeAcquisitionOrchestrationStatus.BLOCKED
    assert result.unresolved is True

    assert result.blocked_reason == "bridge_error"
    assert "handoff transport failure" in result.last_error

    assert result.invariants["blocked_is_not_cancelled"] is True
    assert result.invariants["blocked_is_not_expired"] is True
    assert result.invariants["unresolved_is_not_solved"] is True

    assert (
        result.invariants["automatic_routing_is_not_automatic_authority"]
        is True
    )

def test_coordinator_handoff_retry_visibility_does_not_execute_or_escalate():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=_make_coordinator_output(),
        variable_code="k25",
        reason="missing follow-up marker",
    )

    retry_result = service.mark_retry_attempt(
        result.orchestration_id,
        last_error="handoff retry visibility only",
        max_retry_count=2,
    )

    assert retry_result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert retry_result.unresolved is False

    assert service._states[result.orchestration_id].retry_count == 1
    assert (
        service._states[result.orchestration_id].last_error
        == "handoff retry visibility only"
    )

    assert retry_result.invariants["retry_visibility_is_not_retry_authority"] is True
    assert retry_result.invariants["retry_tracking_is_not_retry_execution"] is True
    assert (
        retry_result.invariants["retry_execution_is_not_escalation_authority"]
        is True
    )