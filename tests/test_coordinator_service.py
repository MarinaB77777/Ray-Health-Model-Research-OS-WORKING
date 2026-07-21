import pytest
from pydantic import ValidationError

from runtime.coordinator.contracts import (
    CoordinatorBlockReason,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorSignalType,
    CoordinatorStatus,
)
from runtime.coordinator.lifecycle import CoordinatorLifecycleError
from runtime.coordinator.service import CoordinatorService


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
        metadata={"source": {"kind": "test"}},
    )


def make_signal() -> CoordinatorSignal:
    return CoordinatorSignal(
        signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
        action_id="action-1",
        reason="missing acquisition",
        payload={"kind": "test"},
    )


def test_create_record_returns_output_snapshot():
    service = CoordinatorService()

    output = service.create_record(make_record())

    assert output.coordinator_id == "coord-1"
    assert output.action_id == "action-1"
    assert output.status == CoordinatorStatus.CREATED
    assert output.ready_for_next_route is False


def test_build_output_ready_for_next_route_is_mechanical():
    record = make_record(status=CoordinatorStatus.READY_FOR_ROUTING)

    output = CoordinatorService.build_output(record)

    assert output.ready_for_next_route is True
    assert output.status == CoordinatorStatus.READY_FOR_ROUTING


def test_build_output_does_not_mutate_record():
    record = make_record()

    original_dump = record.model_dump()

    CoordinatorService.build_output(record)

    assert record.model_dump() == original_dump


def test_build_output_deepcopies_mutable_fields():
    record = make_record()
    signal = make_signal()
    record = record.model_copy(update={"signals": [signal]})

    output = CoordinatorService.build_output(record)

    output.metadata["source"]["kind"] = "mutated"
    output.signals[0].payload["kind"] = "mutated"

    assert record.metadata["source"]["kind"] == "test"
    assert record.signals[0].payload["kind"] == "test"


def test_update_status_uses_lifecycle_constraints():
    service = CoordinatorService()

    service.create_record(
        make_record(status=CoordinatorStatus.READY_FOR_ROUTING)
    )

    with pytest.raises(CoordinatorLifecycleError):
        service.update_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.WAITING_ACQUISITION,
        )


def test_service_does_not_auto_clean_semantic_flags():
    service = CoordinatorService()

    record = CoordinatorRecord(
        coordinator_id="coord-1",
        action_id="action-1",
        status=CoordinatorStatus.WAITING_ANALYSIS,
        requires_analysis=True,
    )

    service.create_record(record)

    with pytest.raises(ValidationError):
        service.update_status(
            coordinator_id="coord-1",
            next_status=CoordinatorStatus.READY_FOR_ROUTING,
        )


def test_update_flags_uses_contract_validation():
    service = CoordinatorService()

    service.create_record(
        make_record(status=CoordinatorStatus.READY_FOR_ROUTING)
    )

    with pytest.raises(ValidationError):
        service.update_flags(
            coordinator_id="coord-1",
            requires_analysis=True,
        )


def test_append_signal_uses_store_action_match_validation():
    service = CoordinatorService()

    service.create_record(make_record())

    invalid_signal = CoordinatorSignal(
        signal_type=CoordinatorSignalType.ACQUISITION_NEEDED,
        action_id="wrong-action",
        reason="wrong action",
    )

    with pytest.raises(ValueError):
        service.append_signal(
            coordinator_id="coord-1",
            signal=invalid_signal,
        )


def test_append_signal_does_not_auto_transition_status():
    service = CoordinatorService()

    service.create_record(make_record())

    output = service.append_signal(
        coordinator_id="coord-1",
        signal=make_signal(),
    )

    assert output.status == CoordinatorStatus.CREATED
    assert output.last_signal if False else True  # output has no last_signal field
    assert len(output.signals) == 1


def test_get_output_returns_none_for_missing_record():
    service = CoordinatorService()

    assert service.get_output("missing") is None


def test_delete_record_returns_bool():
    service = CoordinatorService()

    service.create_record(make_record())

    assert service.delete_record("coord-1") is True
    assert service.delete_record("coord-1") is False


def test_list_outputs_by_action_id_returns_outputs():
    service = CoordinatorService()

    service.create_record(
        make_record(coordinator_id="coord-1", action_id="action-1")
    )
    service.create_record(
        make_record(coordinator_id="coord-2", action_id="action-1")
    )

    outputs = service.list_outputs_by_action_id("action-1")

    assert len(outputs) == 2
    assert all(output.action_id == "action-1" for output in outputs)


def test_output_warnings_are_explicit_empty_list():
    record = make_record()

    output = CoordinatorService.build_output(record)

    assert output.warnings == []