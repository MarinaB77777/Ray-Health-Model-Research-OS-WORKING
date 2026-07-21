import pytest

from runtime.coordinator.contracts import CoordinatorStatus
from runtime.coordinator.lifecycle import (
    CoordinatorLifecycleError,
    can_transition,
    is_terminal,
    validate_transition,
)


def test_created_can_transition_to_allowed_statuses():
    assert can_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.WAITING_ACQUISITION,
    )
    assert can_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.WAITING_ANALYSIS,
    )
    assert can_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.WAITING_HUMAN,
    )
    assert can_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.BLOCKED,
    )
    assert can_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.READY_FOR_ROUTING,
    )
    assert can_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    )


def test_waiting_human_cannot_transition_directly_to_ready_for_routing():
    assert not can_transition(
        CoordinatorStatus.WAITING_HUMAN,
        CoordinatorStatus.READY_FOR_ROUTING,
    )

    with pytest.raises(CoordinatorLifecycleError):
        validate_transition(
            CoordinatorStatus.WAITING_HUMAN,
            CoordinatorStatus.READY_FOR_ROUTING,
        )


def test_blocked_cannot_transition_directly_to_ready_for_routing():
    assert not can_transition(
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.READY_FOR_ROUTING,
    )

    with pytest.raises(CoordinatorLifecycleError):
        validate_transition(
            CoordinatorStatus.BLOCKED,
            CoordinatorStatus.READY_FOR_ROUTING,
        )


def test_blocked_can_transition_to_waiting_states_or_expired():
    assert can_transition(
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.WAITING_ACQUISITION,
    )
    assert can_transition(
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.WAITING_ANALYSIS,
    )
    assert can_transition(
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.WAITING_HUMAN,
    )
    assert can_transition(
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    )


def test_ready_for_routing_is_terminal():
    assert is_terminal(CoordinatorStatus.READY_FOR_ROUTING)

    for next_status in CoordinatorStatus:
        assert not can_transition(
            CoordinatorStatus.READY_FOR_ROUTING,
            next_status,
        )


def test_expired_unresolved_is_terminal():
    assert is_terminal(CoordinatorStatus.EXPIRED_UNRESOLVED)

    for next_status in CoordinatorStatus:
        assert not can_transition(
            CoordinatorStatus.EXPIRED_UNRESOLVED,
            next_status,
        )


def test_non_terminal_statuses_are_not_terminal():
    assert not is_terminal(CoordinatorStatus.CREATED)
    assert not is_terminal(CoordinatorStatus.WAITING_ACQUISITION)
    assert not is_terminal(CoordinatorStatus.WAITING_ANALYSIS)
    assert not is_terminal(CoordinatorStatus.WAITING_HUMAN)
    assert not is_terminal(CoordinatorStatus.BLOCKED)


def test_validate_transition_allows_valid_transition():
    validate_transition(
        CoordinatorStatus.CREATED,
        CoordinatorStatus.WAITING_ACQUISITION,
    )


def test_validate_transition_rejects_invalid_transition():
    with pytest.raises(CoordinatorLifecycleError):
        validate_transition(
            CoordinatorStatus.WAITING_ANALYSIS,
            CoordinatorStatus.WAITING_ACQUISITION,
        )