from __future__ import annotations

from dataclasses import dataclass

from runtime.shared_action.schemas import ActionStatus


TERMINAL_STATUSES: set[ActionStatus] = {
    ActionStatus.completed,
    ActionStatus.canceled,
    ActionStatus.expired,
    ActionStatus.forbidden_by_human,
    ActionStatus.duplicate_detected,
    ActionStatus.archived,
}


ALLOWED_TRANSITIONS: dict[ActionStatus, set[ActionStatus]] = {
    ActionStatus.candidate: {
        ActionStatus.proposed,
        ActionStatus.awaiting_human,
        ActionStatus.duplicate_detected,
        ActionStatus.archived,
        ActionStatus.expired,
    },
    ActionStatus.proposed: {
        ActionStatus.awaiting_human_confirmation,
        ActionStatus.awaiting_governance,
        ActionStatus.accepted,
        ActionStatus.awaiting_human,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },
    ActionStatus.accepted: {
        ActionStatus.assigned,
        ActionStatus.awaiting_human,
        ActionStatus.awaiting_governance,
        ActionStatus.blocked,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },
    ActionStatus.assigned: {
        ActionStatus.in_progress,
        ActionStatus.awaiting_human,
        ActionStatus.awaiting_governance,
        ActionStatus.blocked,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },
    ActionStatus.in_progress: {
        ActionStatus.completed,
        ActionStatus.awaiting_human,
        ActionStatus.awaiting_governance,
        ActionStatus.blocked,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },
    ActionStatus.awaiting_human: {
        ActionStatus.proposed,
        ActionStatus.accepted,
        ActionStatus.assigned,
        ActionStatus.blocked,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },
    ActionStatus.awaiting_human_confirmation: {
        ActionStatus.accepted,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },
    ActionStatus.awaiting_governance: {
        ActionStatus.accepted,
        ActionStatus.assigned,
        ActionStatus.blocked,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },

    # Important:
    # blocked must not go directly to in_progress.
    # Recovery must pass through assigned / awaiting_* first.
    ActionStatus.blocked: {
        ActionStatus.assigned,
        ActionStatus.awaiting_human,
        ActionStatus.awaiting_governance,
        ActionStatus.canceled,
        ActionStatus.expired,
        ActionStatus.forbidden_by_human,
    },

    ActionStatus.completed: set(),
    ActionStatus.canceled: set(),
    ActionStatus.expired: set(),
    ActionStatus.forbidden_by_human: set(),
    ActionStatus.duplicate_detected: set(),
    ActionStatus.archived: set(),
}


@dataclass(frozen=True)
class TransitionCheck:
    allowed: bool
    reason: str | None = None


def can_transition(
    current_status: ActionStatus,
    target_status: ActionStatus,
) -> TransitionCheck:
    """
    Check whether a lifecycle transition is allowed.

    Проверяет, разрешён ли переход статуса.

    Critical rules:
    - terminal states do not reactivate automatically.
    - forbidden_by_human is terminal forever for this action_id.
    - new human permission requires a new action_id.
    - proposed cannot become assigned directly.
    - blocked cannot become in_progress directly.
    """

    if current_status == target_status:
        return TransitionCheck(
            allowed=True,
            reason="status unchanged",
        )

    if current_status in TERMINAL_STATUSES:
        return TransitionCheck(
            allowed=False,
            reason=(
                f"terminal status {current_status.value} cannot transition; "
                "create a new action_id if new human permission exists"
            ),
        )

    allowed_targets = ALLOWED_TRANSITIONS.get(current_status, set())

    if target_status not in allowed_targets:
        return TransitionCheck(
            allowed=False,
            reason=(
                f"transition {current_status.value} → {target_status.value} "
                "is not allowed"
            ),
        )

    return TransitionCheck(allowed=True)


def assert_transition_allowed(
    current_status: ActionStatus,
    target_status: ActionStatus,
) -> None:
    """
    Raise ValueError if transition is not allowed.

    Поднимает ValueError, если переход запрещён.
    """

    result = can_transition(
        current_status=current_status,
        target_status=target_status,
    )

    if not result.allowed:
        raise ValueError(result.reason)