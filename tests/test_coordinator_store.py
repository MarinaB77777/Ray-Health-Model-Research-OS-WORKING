from copy import deepcopy

import pytest
from pydantic import ValidationError

from runtime.coordinator.contracts import (
    CoordinationGroup,
    CoordinatorBlockReason,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorSignalType,
    CoordinatorStatus,
)
from runtime.coordinator.lifecycle import CoordinatorLifecycleError
from runtime.coordinator.store import CoordinatorStore


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


def test_add_record_returns_copy():
    store = CoordinatorStore()

    original = make_record()

    stored = store.add_record(original)

    assert stored is not original
    assert stored == original


def test_get_record_returns_copy():
    store = CoordinatorStore()

    store.add_record(make_record())

    record1 = store.get_record("coord-1")
    record2 = store.get_record("coord-1")

    assert record1 is not record2
    assert record1 == record2


def test_external_mutation_does_not_modify_store():
    store = CoordinatorStore()

    store.add_record(make_record())

    record = store.get_record("coord-1")

    assert record is not None

    mutated = record.model_copy(
        update={
            "status": CoordinatorStatus.BLOCKED,
            "block_reason": CoordinatorBlockReason.MISSING_REQUIRED_CONTEXT,
        }
    )

    assert mutated.status == CoordinatorStatus.BLOCKED

    original = store.get_record("coord-1")

    assert original is not None
    assert original.status == CoordinatorStatus.CREATED


def test_update_record_status_valid_transition():
    store = CoordinatorStore()

    store.add_record(make_record())

    updated = store.update_record_status(
        coordinator_id="coord-1",
        next_status=CoordinatorStatus.WAITING_ACQUISITION,
    )

    assert updated.status == CoordinatorStatus.WAITING_ACQUISITION


def test_update_record_status_invalid_transition_raises():
    store = CoordinatorStore()

    store.add_record(
        make_record(
            status=CoordinatorStatus.READY_FOR_ROUTING,
        )
    )

    with pytest.raises(CoordinatorLifecycleError):
        store.update_record_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.WAITING_ACQUISITION,
        )


def test_append_signal_requires_matching_action_id():
    store = CoordinatorStore()

    store.add_record(make_record())

    invalid_signal = CoordinatorSignal(
        signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
        action_id="wrong-action",
        reason="invalid",
    )

    with pytest.raises(ValueError):
        store.append_signal(
            coordinator_id="coord-1",
            signal=invalid_signal,
        )


def test_append_signal_updates_last_signal():
    store = CoordinatorStore()

    store.add_record(make_record())

    updated = store.append_signal(
        coordinator_id="coord-1",
        signal=make_signal(),
    )

    assert updated.last_signal == CoordinatorSignalType.ACQUISITION_NEEDED
    assert len(updated.signals) == 1


def test_update_record_flags_revalidates_record():
    store = CoordinatorStore()

    store.add_record(
        make_record(
            status=CoordinatorStatus.READY_FOR_ROUTING,
        )
    )

    with pytest.raises(ValidationError):
        store.update_record_flags(
            coordinator_id="coord-1",
            requires_analysis=True,
        )


def test_update_record_status_does_not_auto_clean_semantic_flags():
    store = CoordinatorStore()

    record = CoordinatorRecord(
        coordinator_id="coord-1",
        action_id="action-1",
        status=CoordinatorStatus.WAITING_ANALYSIS,
        requires_analysis=True,
    )

    store.add_record(record)

    with pytest.raises(ValidationError):
        store.update_record_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.READY_FOR_ROUTING,
        )


def test_delete_record_returns_true_when_deleted():
    store = CoordinatorStore()

    store.add_record(make_record())

    assert store.delete_record("coord-1") is True


def test_delete_record_returns_false_when_missing():
    store = CoordinatorStore()

    assert store.delete_record("missing") is False


def test_add_group_returns_copy():
    store = CoordinatorStore()

    group = CoordinationGroup(
        coordination_group_id="group-1",
        action_id="action-1",
    )

    stored = store.add_group(group)

    assert stored is not group
    assert stored == group


def test_get_group_returns_copy():
    store = CoordinatorStore()

    group = CoordinationGroup(
        coordination_group_id="group-1",
        action_id="action-1",
    )

    store.add_group(group)

    group1 = store.get_group("group-1")
    group2 = store.get_group("group-1")

    assert group1 is not group2
    assert group1 == group2


def test_update_group_status_valid_transition():
    store = CoordinatorStore()

    group = CoordinationGroup(
        coordination_group_id="group-1",
        action_id="action-1",
        operation_ids=["op-1"],
    )

    store.add_group(group)

    updated = store.update_group_status(
        coordination_group_id="group-1",
        next_status=CoordinatorStatus.WAITING_ACQUISITION,
    )

    assert updated.status == CoordinatorStatus.WAITING_ACQUISITION


def test_update_group_status_invalid_transition_raises():
    store = CoordinatorStore()

    group = CoordinationGroup(
        coordination_group_id="group-1",
        action_id="action-1",
        operation_ids=["op-1"],
        status=CoordinatorStatus.READY_FOR_ROUTING,
    )

    store.add_group(group)

    with pytest.raises(CoordinatorLifecycleError):
        store.update_group_status(
            coordination_group_id="group-1",
            next_status=CoordinatorStatus.WAITING_ANALYSIS,
        )


def test_delete_group_returns_true_when_deleted():
    store = CoordinatorStore()

    group = CoordinationGroup(
        coordination_group_id="group-1",
        action_id="action-1",
    )

    store.add_group(group)

    assert store.delete_group("group-1") is True


def test_delete_group_returns_false_when_missing():
    store = CoordinatorStore()

    assert store.delete_group("missing") is False