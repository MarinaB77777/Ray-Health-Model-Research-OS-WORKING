import pytest
from pydantic import ValidationError

from runtime.coordinator.bridge import RuntimeCoordinatorBridge
from runtime.coordinator.contracts import (
    CoordinatorBlockReason,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorSignalType,
    CoordinatorStatus,
)
from runtime.coordinator.lifecycle import CoordinatorLifecycleError


def make_record(
    *,
    coordinator_id: str = "coord-1",
    action_id: str = "action-1",
    status: CoordinatorStatus = CoordinatorStatus.CREATED,
) -> CoordinatorRecord:
    return CoordinatorRecord(
        coordinator_id=coordinator_id,
        action_id=action_id,
        status=status,
    )


def make_signal() -> CoordinatorSignal:
    return CoordinatorSignal(
        signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
        action_id="action-1",
        reason="missing acquisition",
    )


def test_create_coordinator_is_explicit_only():
    bridge = RuntimeCoordinatorBridge()

    output = bridge.create_coordinator(make_record())

    assert output.coordinator_id == "coord-1"
    assert output.status == CoordinatorStatus.CREATED


def test_get_output_does_not_implicitly_create_record():
    bridge = RuntimeCoordinatorBridge()

    assert bridge.get_output("missing") is None


def test_list_outputs_by_action_id_does_not_aggregate_readiness():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(
        make_record(coordinator_id="coord-1", action_id="action-1")
    )
    bridge.create_coordinator(
        make_record(coordinator_id="coord-2", action_id="action-1")
    )

    outputs = bridge.list_outputs_by_action_id("action-1")

    assert len(outputs) == 2
    assert all(output.action_id == "action-1" for output in outputs)
    assert all(output.ready_for_next_route is False for output in outputs)


def test_append_signal_transports_only_and_does_not_auto_transition():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(make_record())

    output = bridge.append_signal(
        coordinator_id="coord-1",
        signal=make_signal(),
    )

    assert output.status == CoordinatorStatus.CREATED
    assert len(output.signals) == 1


def test_append_signal_uses_action_match_validation():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(make_record())

    invalid_signal = CoordinatorSignal(
        signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
        action_id="wrong-action",
        reason="wrong action",
    )

    with pytest.raises(ValueError):
        bridge.append_signal(
            coordinator_id="coord-1",
            signal=invalid_signal,
        )


def test_update_status_uses_lifecycle_validation():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(
        make_record(status=CoordinatorStatus.READY_FOR_ROUTING)
    )

    with pytest.raises(CoordinatorLifecycleError):
        bridge.update_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.WAITING_ACQUISITION,
        )


def test_bridge_does_not_auto_clean_semantic_flags():
    bridge = RuntimeCoordinatorBridge()

    record = CoordinatorRecord(
        coordinator_id="coord-1",
        action_id="action-1",
        status=CoordinatorStatus.WAITING_ANALYSIS,
        requires_analysis=True,
    )

    bridge.create_coordinator(record)

    with pytest.raises(ValidationError):
        bridge.update_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.READY_FOR_ROUTING,
        )


def test_update_flags_uses_contract_validation():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(
        make_record(status=CoordinatorStatus.READY_FOR_ROUTING)
    )

    with pytest.raises(ValidationError):
        bridge.update_flags(
            coordinator_id="coord-1",
            requires_analysis=True,
        )


def test_delete_coordinator_is_technical_cleanup_only_returns_bool():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(make_record())

    assert bridge.delete_coordinator("coord-1") is True
    assert bridge.delete_coordinator("coord-1") is False


def test_get_output_after_delete_returns_none():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(make_record())
    bridge.delete_coordinator("coord-1")

    assert bridge.get_output("coord-1") is None


def test_bridge_returns_ready_for_routing_mechanically():
    bridge = RuntimeCoordinatorBridge()

    bridge.create_coordinator(
        make_record(status=CoordinatorStatus.WAITING_ANALYSIS)
    )

    output = bridge.update_status(
        coordinator_id="coord-1",
        next_status=CoordinatorStatus.READY_FOR_ROUTING,
    )

    assert output.status == CoordinatorStatus.READY_FOR_ROUTING
    assert output.ready_for_next_route is True


def test_blocked_to_ready_for_routing_is_not_allowed():
    bridge = RuntimeCoordinatorBridge()

    record = CoordinatorRecord(
        coordinator_id="coord-1",
        action_id="action-1",
        status=CoordinatorStatus.BLOCKED,
        block_reason=CoordinatorBlockReason.MISSING_REQUIRED_CONTEXT,
    )

    bridge.create_coordinator(record)

    with pytest.raises(CoordinatorLifecycleError):
        bridge.update_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.READY_FOR_ROUTING,
        )