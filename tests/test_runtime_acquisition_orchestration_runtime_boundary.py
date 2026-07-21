# tests/test_runtime_acquisition_orchestration_runtime_boundary.py
from datetime import timedelta
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
        coordinator_id="coord_runtime_boundary_1",
        action_id="action_runtime_boundary_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )


def test_waiting_acquisition_state_does_not_complete_runtime_task():
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

    state = service._states[result.orchestration_id]

    assert result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert state.status == RuntimeAcquisitionOrchestrationStatus.WAITING

    assert result.unresolved is False
    assert state.unresolved is False

    assert result.invariants["waiting_is_not_answered"] is True
    assert result.invariants["waiting_is_not_acquired"] is True
    assert result.invariants["acquisition_request_is_not_acquisition_result"] is True

    assert result.invariants["prepared_is_not_executed"] is True
    assert result.invariants["automatic_routing_is_not_automatic_authority"] is True

class FailingBridge:
    def create_from_runtime_request(self, runtime_request):
        raise RuntimeError("bridge transport failure")


def test_blocked_acquisition_state_does_not_cancel_runtime_task():
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

    state = service._states[result.orchestration_id]

    assert result.status == RuntimeAcquisitionOrchestrationStatus.BLOCKED
    assert state.status == RuntimeAcquisitionOrchestrationStatus.BLOCKED

    assert result.unresolved is True
    assert state.unresolved is True

    assert result.blocked_reason == "bridge_error"
    assert "bridge transport failure" in result.last_error

    assert result.invariants["blocked_is_not_cancelled"] is True
    assert result.invariants["blocked_is_not_expired"] is True
    assert result.invariants["unresolved_is_not_solved"] is True

    assert (
        result.invariants["automatic_routing_is_not_automatic_authority"]
        is True
    )

def test_expired_acquisition_state_does_not_delete_or_cancel_runtime_task():
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

    state = service._states[result.orchestration_id]
    expired_candidate = service._revalidate_state(
        state.model_copy(
            update={
                "created_at": service._now() - timedelta(minutes=60),
                "expires_at": service._now() - timedelta(minutes=1),
            }
        )
    )
    service._states[result.orchestration_id] = expired_candidate

    expired_ids = service.cleanup_expired()

    assert result.orchestration_id in expired_ids
    assert result.orchestration_id in service._states

    expired_state = service._states[result.orchestration_id]

    assert expired_state.status == RuntimeAcquisitionOrchestrationStatus.EXPIRED
    assert expired_state.unresolved is True

    assert result.invariants["expired_is_not_deleted"] is True
    assert result.invariants["cleanup_is_not_resolved"] is True
    assert result.invariants["cleanup_is_not_cancelled"] is True
    assert result.invariants["cleanup_is_not_memory_deletion"] is True

def test_external_runtime_state_mutation_does_not_mutate_internal_state():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=_make_coordinator_output(),
        variable_code="k30",
        reason="mutation protection test",
    )

    unresolved = service.list_unresolved()

    unresolved[0].retry_count = 999
    unresolved[0].status = (
        RuntimeAcquisitionOrchestrationStatus.UNRESOLVED
    )

    internal_state = service._states[result.orchestration_id]

    assert internal_state.retry_count == 0
    assert (
        internal_state.status
        == RuntimeAcquisitionOrchestrationStatus.WAITING
    )