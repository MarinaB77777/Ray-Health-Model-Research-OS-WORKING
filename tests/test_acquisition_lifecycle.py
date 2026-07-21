import pytest

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionSourceClass,
    AcquisitionStatus,
)
from runtime.acquisition.lifecycle import AcquisitionLifecycle
from runtime.acquisition.registry import AcquisitionRegistry


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Internal question",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_created_can_move_to_waiting():
    lifecycle = AcquisitionLifecycle()

    assert lifecycle.can_transition(
        AcquisitionStatus.CREATED,
        AcquisitionStatus.WAITING,
    )


def test_waiting_can_move_to_result_received():
    lifecycle = AcquisitionLifecycle()

    assert lifecycle.can_transition(
        AcquisitionStatus.WAITING,
        AcquisitionStatus.RESULT_RECEIVED,
    )


def test_invalid_backward_transition_is_blocked():
    lifecycle = AcquisitionLifecycle()

    with pytest.raises(ValueError):
        lifecycle.validate_transition(
            AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
            AcquisitionStatus.WAITING,
        )


def test_closed_cannot_move_to_filtered():
    lifecycle = AcquisitionLifecycle()

    with pytest.raises(ValueError):
        lifecycle.validate_transition(
            AcquisitionStatus.CLOSED,
            AcquisitionStatus.FILTERED,
        )


def test_terminal_statuses_are_terminal():
    lifecycle = AcquisitionLifecycle()

    for status in {
        AcquisitionStatus.BLOCKED,
        AcquisitionStatus.FAILED,
        AcquisitionStatus.UNRESOLVED,
        AcquisitionStatus.CLOSED,
    }:
        assert lifecycle.is_terminal(status)


def test_registry_allows_same_status_update():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    updated = registry.update_status(
        "req-1",
        AcquisitionStatus.CREATED,
    )

    assert updated.status == AcquisitionStatus.CREATED


def test_registry_blocks_invalid_transition():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    registry.update_status("req-1", AcquisitionStatus.WAITING)
    registry.update_status("req-1", AcquisitionStatus.RESULT_RECEIVED)
    registry.update_status("req-1", AcquisitionStatus.FILTERED)
    registry.update_status(
        "req-1",
        AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
    )

    with pytest.raises(ValueError):
        registry.update_status("req-1", AcquisitionStatus.WAITING)


def test_registry_allows_valid_lifecycle_path_to_closed():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    registry.update_status("req-1", AcquisitionStatus.WAITING)
    registry.update_status("req-1", AcquisitionStatus.RESULT_RECEIVED)
    registry.update_status("req-1", AcquisitionStatus.FILTERED)
    registry.update_status(
        "req-1",
        AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
    )
    updated = registry.update_status("req-1", AcquisitionStatus.CLOSED)

    assert updated.status == AcquisitionStatus.CLOSED