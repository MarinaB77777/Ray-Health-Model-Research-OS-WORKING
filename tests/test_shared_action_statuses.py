import pytest

from runtime.shared_action.schemas import ActionStatus
from runtime.shared_action.statuses import (
    assert_transition_allowed,
    can_transition,
)


def test_candidate_can_move_to_proposed():
    result = can_transition(
        ActionStatus.candidate,
        ActionStatus.proposed,
    )

    assert result.allowed is True


def test_candidate_cannot_move_to_completed():
    result = can_transition(
        ActionStatus.candidate,
        ActionStatus.completed,
    )

    assert result.allowed is False


def test_proposed_cannot_move_directly_to_assigned():
    result = can_transition(
        ActionStatus.proposed,
        ActionStatus.assigned,
    )

    assert result.allowed is False


def test_blocked_cannot_move_directly_to_in_progress():
    result = can_transition(
        ActionStatus.blocked,
        ActionStatus.in_progress,
    )

    assert result.allowed is False


def test_blocked_can_move_to_assigned():
    result = can_transition(
        ActionStatus.blocked,
        ActionStatus.assigned,
    )

    assert result.allowed is True


def test_forbidden_by_human_is_terminal():
    result = can_transition(
        ActionStatus.forbidden_by_human,
        ActionStatus.proposed,
    )

    assert result.allowed is False


def test_completed_is_terminal():
    result = can_transition(
        ActionStatus.completed,
        ActionStatus.in_progress,
    )

    assert result.allowed is False


def test_assert_transition_allowed_raises_on_invalid_transition():
    with pytest.raises(ValueError):
        assert_transition_allowed(
            ActionStatus.proposed,
            ActionStatus.assigned,
        )


def test_duplicate_detected_is_terminal():
    result = can_transition(
        ActionStatus.duplicate_detected,
        ActionStatus.proposed,
    )

    assert result.allowed is False


def test_archived_is_terminal():
    result = can_transition(
        ActionStatus.archived,
        ActionStatus.proposed,
    )

    assert result.allowed is False