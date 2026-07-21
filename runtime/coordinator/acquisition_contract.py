# runtime/coordinator/acquisition_contract.py

from runtime.coordinator.contracts import CoordinatorOutput


def coordinator_requires_acquisition(
    coordinator_output: CoordinatorOutput,
    *,
    has_acquisition_requests: bool,
) -> bool:
    """
    Returns whether CoordinatorOutput explicitly requires acquisition routing.

    This is a routing/readiness helper only.

    Does NOT:
    - complete Runtime task;
    - mark acquisition answered;
    - grant execution authority;
    - infer truth;
    - infer human approval;
    - infer acquisition need from generic not-ready state;
    - infer acquisition success;
    - infer acquisition freshness;
    - grant orchestration authority.

    acquisition needed ≠ completed
    acquisition needed ≠ answered
    acquisition needed ≠ execution authority
    not ready ≠ acquisition needed
    missing contract ≠ no acquisition
    helper output ≠ orchestration authority
    """

    return (
        coordinator_output.ready_for_next_route is False
        and has_acquisition_requests
    )