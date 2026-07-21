from __future__ import annotations

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationResult,
    RuntimeAcquisitionOrchestrationService,
)
from runtime.coordinator.acquisition_contract import (
    coordinator_requires_acquisition,
)
from runtime.coordinator.contracts import CoordinatorOutput


def handoff_acquisition_to_orchestration(
    *,
    coordinator_output: CoordinatorOutput,
    orchestration_service: RuntimeAcquisitionOrchestrationService,
    has_acquisition_requests: bool,
    variable_code: str,
    reason: str,
) -> RuntimeAcquisitionOrchestrationResult | None:
    """
    Bounded Coordinator → Runtime orchestration handoff helper.

    Does NOT:
    - complete Runtime task;
    - grant execution authority;
    - infer acquisition success;
    - infer acquisition freshness;
    - infer acquisition answer;
    - infer lifecycle completion;
    - execute retry;
    - plan retry;
    - escalate;
    - infer human approval;
    - validate truth;
    - mutate Coordinator state;
    - auto-create orchestration state;
    - aggregate coordination outputs.

    helper handoff ≠ orchestration authority
    orchestration handoff ≠ execution authority
    handoff helper ≠ retry planner
    handoff helper ≠ acquisition freshness validator
    WAITING ≠ answered
    """

    requires_acquisition = coordinator_requires_acquisition(
        coordinator_output,
        has_acquisition_requests=has_acquisition_requests,
    )

    if not requires_acquisition:
        return None

    return orchestration_service.orchestrate_dialogue_question(
        coordinator_output=coordinator_output,
        variable_code=variable_code,
        reason=reason,
    )