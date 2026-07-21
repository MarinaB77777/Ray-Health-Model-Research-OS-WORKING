# tests/test_runtime_acquisition_orchestration_integration.py

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
        coordinator_id="coord_1",
        action_id="action_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )


def test_orchestration_integrates_builder_and_bridge_for_dialogue_question():
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
    assert result.runtime_request_id
    assert result.acquisition_request_id
    assert result.unresolved is False

    assert result.invariants["waiting_is_not_answered"] is True
    assert result.invariants["waiting_is_not_acquired"] is True
    assert (
        result.invariants["acquisition_request_is_not_acquisition_result"]
        is True
    )
    assert (
        result.invariants["automatic_routing_is_not_automatic_authority"]
        is True
    )


def test_orchestration_state_remains_temporary_runtime_state():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=_make_coordinator_output(),
        variable_code="k24",
        reason="missing safety marker",
    )

    state = service._states[result.orchestration_id]

    assert state.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert state.acquisition_request_id == result.acquisition_request_id

    assert result.invariants["orchestration_state_is_not_long_term_truth"]
    assert result.invariants["inbound_result_is_not_verified_truth"]
    assert result.invariants["prepared_is_not_externally_exposed"]


