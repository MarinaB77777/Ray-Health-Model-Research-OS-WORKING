import pytest
from pydantic import ValidationError

from runtime.acquisition.contracts import AcquisitionRequest
from runtime.acquisition.runtime_request_builder import (
    RuntimeAcquisitionRequestBuilder,
)
from runtime.contracts.runtime_acquisition_request import (
    RuntimeAcquisitionRequest,
    RuntimeAcquisitionRequestStatus,
    RuntimeAcquisitionRequestType,
)
from runtime.coordinator.contracts import (
    CoordinatorOutput,
    CoordinatorStatus,
)


def make_coordinator_output(
    *,
    action_id: str = "action-1",
    coordinator_id: str = "coord-1",
    ready_for_next_route: bool = False,
) -> CoordinatorOutput:
    return CoordinatorOutput(
        coordinator_id=coordinator_id,
        action_id=action_id,
        status=(
            CoordinatorStatus.READY_FOR_ROUTING
            if ready_for_next_route
            else CoordinatorStatus.CREATED
        ),
        ready_for_next_route=ready_for_next_route,
    )


def test_builder_creates_runtime_acquisition_request():
    output = make_coordinator_output()

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert isinstance(request, RuntimeAcquisitionRequest)
    assert not isinstance(request, AcquisitionRequest)


def test_builder_uses_action_id_from_coordinator_output():
    output = make_coordinator_output(action_id="action-from-output")

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert request.action_id == "action-from-output"


def test_builder_keeps_coordinator_reference_only():
    output = make_coordinator_output(
        action_id="action-1",
        coordinator_id="coord-123",
    )

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert request.coordinator_id == "coord-123"
    assert request.coordination_group_id is None


def test_builder_sets_prepared_status_but_does_not_send():
    output = make_coordinator_output()

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert request.status == RuntimeAcquisitionRequestStatus.PREPARED


def test_builder_creates_dialogue_question_type():
    output = make_coordinator_output()

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert (
        request.requested_acquisition_type
        == RuntimeAcquisitionRequestType.DIALOGUE_QUESTION
    )


def test_builder_sets_required_fields_from_variable_code():
    output = make_coordinator_output()

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert request.required_fields == ["d0"]


def test_builder_rejects_empty_variable_code():
    output = make_coordinator_output()

    with pytest.raises(ValueError):
        RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
            coordinator_output=output,
            variable_code="",
            reason="Need missing field",
        )


def test_builder_rejects_empty_reason():
    output = make_coordinator_output()

    with pytest.raises(ValueError):
        RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
            coordinator_output=output,
            variable_code="d0",
            reason="",
        )


def test_builder_does_not_require_ready_for_next_route():
    output = make_coordinator_output(
        ready_for_next_route=False,
    )

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert request.action_id == output.action_id


def test_builder_metadata_is_runtime_builder_only():
    output = make_coordinator_output()

    request = RuntimeAcquisitionRequestBuilder.build_dialogue_question_request(
        coordinator_output=output,
        variable_code="d0",
        reason="Need missing field",
    )

    assert request.metadata["variable_code"] == "d0"
    assert request.metadata["source"] == "runtime_builder"