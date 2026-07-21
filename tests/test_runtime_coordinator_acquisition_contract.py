# tests/test_runtime_coordinator_acquisition_contract.py

from runtime.coordinator.acquisition_contract import (
    coordinator_requires_acquisition,
)
from runtime.coordinator.contracts import (
    CoordinatorOutput,
    CoordinatorStatus,
)


def test_coordinator_output_acquisition_needed_is_not_completion_authority():
    output = CoordinatorOutput(
        coordinator_id="coord_contract_1",
        action_id="action_contract_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )

    assert output.ready_for_next_route is False

    assert output.status == CoordinatorStatus.CREATED

    # acquisition-needed contract boundaries
    assert output.status != "completed"
    assert output.status != "answered"
    assert output.status != "executed"


def test_coordinator_requires_acquisition_when_requests_exist():
    output = CoordinatorOutput(
        coordinator_id="coord_contract_2",
        action_id="action_contract_2",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )

    assert coordinator_requires_acquisition(
        output,
        has_acquisition_requests=True,
    ) is True


def test_not_ready_without_acquisition_requests_is_not_acquisition_needed():
    output = CoordinatorOutput(
        coordinator_id="coord_contract_3",
        action_id="action_contract_3",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )

    assert coordinator_requires_acquisition(
        output,
        has_acquisition_requests=False,
    ) is False


def test_ready_for_next_route_is_not_acquisition_needed():
    output = CoordinatorOutput(
        coordinator_id="coord_contract_4",
        action_id="action_contract_4",
        status=CoordinatorStatus.READY_FOR_ROUTING,
        ready_for_next_route=True,
        warnings=[],
    )

    assert coordinator_requires_acquisition(
        output,
        has_acquisition_requests=True,
    ) is False