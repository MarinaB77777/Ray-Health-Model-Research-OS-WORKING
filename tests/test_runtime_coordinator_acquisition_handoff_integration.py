# tests/test_runtime_coordinator_acquisition_handoff_integration.py

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationService,
    RuntimeAcquisitionOrchestrationStatus,
)
from runtime.acquisition.runtime_bridge import AcquisitionRuntimeBridge
from runtime.acquisition.runtime_request_builder import (
    RuntimeAcquisitionRequestBuilder,
)
from runtime.coordinator.acquisition_contract import (
    coordinator_requires_acquisition,
)
from runtime.coordinator.contracts import (
    CoordinatorOutput,
    CoordinatorStatus,
)


def _make_coordinator_output() -> CoordinatorOutput:
    return CoordinatorOutput(
        coordinator_id="coord_handoff_integration_1",
        action_id="action_handoff_integration_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )


def test_coordinator_acquisition_contract_can_drive_orchestration_handoff():
    coordinator_output = _make_coordinator_output()

    requires_acquisition = coordinator_requires_acquisition(
        coordinator_output,
        has_acquisition_requests=True,
    )

    assert requires_acquisition is True

    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=coordinator_output,
        variable_code="k31",
        reason="missing acquisition contract marker",
    )

    assert result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert result.acquisition_request_id
    assert result.unresolved is False

    assert result.invariants["waiting_is_not_answered"] is True
    assert (
        result.invariants["automatic_routing_is_not_automatic_authority"]
        is True
    )

def test_no_acquisition_contract_does_not_drive_orchestration_handoff():
    coordinator_output = _make_coordinator_output()

    requires_acquisition = coordinator_requires_acquisition(
        coordinator_output,
        has_acquisition_requests=False,
    )

    assert requires_acquisition is False

    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    assert service._states == {}

def test_acquisition_handoff_retry_visibility_does_not_grant_retry_authority():
    coordinator_output = _make_coordinator_output()

    requires_acquisition = coordinator_requires_acquisition(
        coordinator_output,
        has_acquisition_requests=True,
    )

    assert requires_acquisition is True

    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = service.orchestrate_dialogue_question(
        coordinator_output=coordinator_output,
        variable_code="k32",
        reason="retry visibility integration",
    )

    retry_result = service.mark_retry_attempt(
        result.orchestration_id,
        last_error="integration retry visibility",
        max_retry_count=2,
    )

    assert retry_result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert retry_result.unresolved is False

    assert (
        service._states[result.orchestration_id].retry_count
        == 1
    )

    assert (
        retry_result.invariants[
            "retry_visibility_is_not_retry_authority"
        ]
        is True
    )

    assert (
        retry_result.invariants[
            "retry_tracking_is_not_retry_execution"
        ]
        is True
    )

    assert (
        retry_result.invariants[
            "retry_execution_is_not_escalation_authority"
        ]
        is True
    )