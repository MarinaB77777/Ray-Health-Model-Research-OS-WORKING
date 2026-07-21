import pytest
from pydantic import ValidationError

from runtime.coordinator.contracts import (
    CoordinationGroup,
    CoordinatorBlockReason,
    CoordinatorOutput,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorSignalType,
    CoordinatorStatus,
    FORBIDDEN_COORDINATOR_MEANING_STATUSES,
)


def test_coordinator_statuses_do_not_use_forbidden_meaning_statuses():
    status_values = {status.value for status in CoordinatorStatus}

    assert status_values.isdisjoint(
        FORBIDDEN_COORDINATOR_MEANING_STATUSES
    )


def test_coordinator_record_requires_non_empty_coordinator_id():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="",
            action_id="action-1",
        )


def test_coordinator_record_requires_non_empty_action_id():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="",
        )


def test_coordinator_signal_requires_non_empty_action_id():
    with pytest.raises(ValidationError):
        CoordinatorSignal(
            signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
            action_id="",
            reason="needed",
        )


def test_coordinator_signal_cannot_be_operationally_empty():
    with pytest.raises(ValidationError):
        CoordinatorSignal(
            signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
            action_id="action-1",
        )


def test_blocked_record_requires_block_reason():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.BLOCKED,
        )


def test_expired_unresolved_record_requires_unresolved_true():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.EXPIRED_UNRESOLVED,
            unresolved=False,
        )


def test_ready_for_routing_record_cannot_be_unresolved():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            unresolved=True,
        )


def test_ready_for_routing_record_cannot_require_human_input():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            requires_human_input=True,
            last_signal=CoordinatorSignalType.HUMAN_INPUT_NEEDED,
        )


def test_ready_for_routing_record_cannot_require_governance():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            requires_governance=True,
        )


def test_ready_for_routing_record_cannot_require_analysis():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            requires_analysis=True,
        )


def test_ready_for_routing_record_cannot_have_block_reason():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            block_reason=CoordinatorBlockReason.MISSING_REQUIRED_CONTEXT,
        )


def test_requires_human_input_requires_reason():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            requires_human_input=True,
        )


def test_requires_runtime_action_requires_explanation():
    with pytest.raises(ValidationError):
        CoordinatorRecord(
            coordinator_id="coord-1",
            action_id="action-1",
            requires_runtime_action=True,
        )


def test_coordinator_output_ready_for_next_route_requires_ready_status():
    with pytest.raises(ValidationError):
        CoordinatorOutput(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.WAITING_ACQUISITION,
            ready_for_next_route=True,
        )


def test_coordinator_output_ready_for_next_route_cannot_be_unresolved():
    with pytest.raises(ValidationError):
        CoordinatorOutput(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            ready_for_next_route=True,
            unresolved=True,
        )


def test_coordinator_output_ready_for_next_route_cannot_require_human_input():
    with pytest.raises(ValidationError):
        CoordinatorOutput(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            ready_for_next_route=True,
            requires_human_input=True,
        )


def test_coordinator_output_ready_for_next_route_cannot_require_governance():
    with pytest.raises(ValidationError):
        CoordinatorOutput(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            ready_for_next_route=True,
            requires_governance=True,
        )


def test_coordinator_output_ready_for_next_route_cannot_require_analysis():
    with pytest.raises(ValidationError):
        CoordinatorOutput(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            ready_for_next_route=True,
            requires_analysis=True,
        )


def test_coordinator_output_ready_for_next_route_cannot_have_block_reason():
    with pytest.raises(ValidationError):
        CoordinatorOutput(
            coordinator_id="coord-1",
            action_id="action-1",
            status=CoordinatorStatus.READY_FOR_ROUTING,
            ready_for_next_route=True,
            block_reason=CoordinatorBlockReason.MISSING_REQUIRED_CONTEXT,
        )


def test_coordination_group_requires_non_empty_group_id():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="",
            action_id="action-1",
        )


def test_coordination_group_requires_non_empty_action_id():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="group-1",
            action_id="",
        )


def test_coordination_group_cannot_be_empty_when_not_created():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="group-1",
            action_id="action-1",
            status=CoordinatorStatus.WAITING_ACQUISITION,
        )


def test_blocked_coordination_group_requires_block_reason():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="group-1",
            action_id="action-1",
            operation_ids=["op-1"],
            status=CoordinatorStatus.BLOCKED,
        )


def test_expired_coordination_group_requires_unresolved_true():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="group-1",
            action_id="action-1",
            operation_ids=["op-1"],
            status=CoordinatorStatus.EXPIRED_UNRESOLVED,
            unresolved=False,
        )


def test_ready_for_routing_group_cannot_be_unresolved():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="group-1",
            action_id="action-1",
            operation_ids=["op-1"],
            status=CoordinatorStatus.READY_FOR_ROUTING,
            unresolved=True,
        )


def test_ready_for_routing_group_cannot_have_block_reason():
    with pytest.raises(ValidationError):
        CoordinationGroup(
            coordination_group_id="group-1",
            action_id="action-1",
            operation_ids=["op-1"],
            status=CoordinatorStatus.READY_FOR_ROUTING,
            block_reason=CoordinatorBlockReason.MISSING_REQUIRED_CONTEXT,
        )