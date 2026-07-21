# tests/test_runtime_acquisition_run_output_bridge.py

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationService,
    RuntimeAcquisitionOrchestrationStatus,
)
from runtime.acquisition.runtime_bridge import AcquisitionRuntimeBridge
from runtime.acquisition.runtime_request_builder import (
    RuntimeAcquisitionRequestBuilder,
)
from runtime.acquisition.run_output_bridge import (
    orchestrate_run_output_acquisition_requests,
)
from runtime.coordinator.contracts import CoordinatorOutput, CoordinatorStatus


def _make_coordinator_output() -> CoordinatorOutput:
    return CoordinatorOutput(
        coordinator_id="coord_run_output_bridge_1",
        action_id="action_run_output_bridge_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )


def _make_service() -> RuntimeAcquisitionOrchestrationService:
    return RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )


def test_run_output_pending_dialogue_requests_are_orchestrated():
    run_result = {
        "data_acquisition_requests": [
            {
                "status": "pending",
                "acquisition_route": "dialogue_question",
                "variable_code": "d0",
                "reason_code": "MISSING_FIELD",
            },
            {
                "status": "pending",
                "acquisition_route": "dialogue_question",
                "variable_code": "d8",
                "reason_code": "MISSING_FIELD",
            },
        ]
    }

    results = orchestrate_run_output_acquisition_requests(
        run_result=run_result,
        coordinator_output=_make_coordinator_output(),
        orchestration_service=_make_service(),
    )

    assert len(results) == 2
    assert all(
        result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
        for result in results
    )
    assert all(result.unresolved is False for result in results)
    assert all(
        result.invariants["waiting_is_not_answered"] is True
        for result in results
    )


def test_run_output_bridge_ignores_non_pending_requests():
    run_result = {
        "data_acquisition_requests": [
            {
                "status": "completed",
                "acquisition_route": "dialogue_question",
                "variable_code": "d0",
                "reason_code": "MISSING_FIELD",
            }
        ]
    }

    results = orchestrate_run_output_acquisition_requests(
        run_result=run_result,
        coordinator_output=_make_coordinator_output(),
        orchestration_service=_make_service(),
    )

    assert results == []


def test_run_output_bridge_ignores_non_dialogue_routes():
    run_result = {
        "data_acquisition_requests": [
            {
                "status": "pending",
                "acquisition_route": "sensor_request",
                "variable_code": "k_sensor",
                "reason_code": "SENSOR_REQUIRED",
            }
        ]
    }

    results = orchestrate_run_output_acquisition_requests(
        run_result=run_result,
        coordinator_output=_make_coordinator_output(),
        orchestration_service=_make_service(),
    )

    assert results == []


def test_run_output_bridge_ignores_requests_without_variable_code():
    run_result = {
        "data_acquisition_requests": [
            {
                "status": "pending",
                "acquisition_route": "dialogue_question",
                "reason_code": "MISSING_FIELD",
            }
        ]
    }

    results = orchestrate_run_output_acquisition_requests(
        run_result=run_result,
        coordinator_output=_make_coordinator_output(),
        orchestration_service=_make_service(),
    )

    assert results == []
