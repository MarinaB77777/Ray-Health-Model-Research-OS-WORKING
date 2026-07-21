# runtime/acquisition/run_output_bridge.py

from typing import Any, Dict, List

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationResult,
    RuntimeAcquisitionOrchestrationService,
)
from runtime.coordinator.contracts import CoordinatorOutput


def orchestrate_run_output_acquisition_requests(
    *,
    run_result: Dict[str, Any],
    coordinator_output: CoordinatorOutput,
    orchestration_service: RuntimeAcquisitionOrchestrationService,
) -> List[RuntimeAcquisitionOrchestrationResult]:
    """
    Bridges Core Engine /run data_acquisition_requests into Runtime acquisition orchestration.

    Does NOT:
    - answer acquisition;
    - verify truth;
    - execute action;
    - grant authority;
    - complete lifecycle;
    - infer human approval;
    - create memory.

    /run acquisition request ≠ acquisition answer
    orchestration result ≠ verified truth
    WAITING ≠ answered
    bridge ≠ authority
    """

    requests = run_result.get("data_acquisition_requests") or []

    results: List[RuntimeAcquisitionOrchestrationResult] = []

    for request in requests:
        if request.get("status") != "pending":
            continue

        if request.get("acquisition_route") != "dialogue_question":
            continue

        variable_code = request.get("variable_code") or request.get("target_data")
        reason_code = request.get("reason_code") or "DATA_ACQUISITION_REQUEST"

        if not variable_code:
            continue

        result = orchestration_service.orchestrate_dialogue_question(
            coordinator_output=coordinator_output,
            variable_code=variable_code,
            reason=reason_code,
        )

        results.append(result)

    return results
