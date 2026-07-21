from __future__ import annotations

from runtime.coordinator.contracts import CoordinatorStatus


ALLOWED_COORDINATOR_TRANSITIONS: dict[
    CoordinatorStatus,
    set[CoordinatorStatus],
] = {
    CoordinatorStatus.CREATED: {
        CoordinatorStatus.WAITING_ACQUISITION,
        CoordinatorStatus.WAITING_ANALYSIS,
        CoordinatorStatus.WAITING_HUMAN,
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.READY_FOR_ROUTING,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    },
    CoordinatorStatus.WAITING_ACQUISITION: {
        CoordinatorStatus.WAITING_ANALYSIS,
        CoordinatorStatus.WAITING_HUMAN,
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.READY_FOR_ROUTING,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    },
    CoordinatorStatus.WAITING_ANALYSIS: {
        CoordinatorStatus.WAITING_HUMAN,
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.READY_FOR_ROUTING,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    },
    CoordinatorStatus.WAITING_HUMAN: {
        CoordinatorStatus.WAITING_ACQUISITION,
        CoordinatorStatus.WAITING_ANALYSIS,
        CoordinatorStatus.BLOCKED,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    },
    CoordinatorStatus.BLOCKED: {
        CoordinatorStatus.WAITING_ACQUISITION,
        CoordinatorStatus.WAITING_ANALYSIS,
        CoordinatorStatus.WAITING_HUMAN,
        CoordinatorStatus.EXPIRED_UNRESOLVED,
    },
    CoordinatorStatus.READY_FOR_ROUTING: set(),
    CoordinatorStatus.EXPIRED_UNRESOLVED: set(),
}


TERMINAL_COORDINATOR_STATUSES: set[CoordinatorStatus] = {
    CoordinatorStatus.READY_FOR_ROUTING,
    CoordinatorStatus.EXPIRED_UNRESOLVED,
}


class CoordinatorLifecycleError(ValueError):
    pass


def can_transition(
    current_status: CoordinatorStatus,
    next_status: CoordinatorStatus,
) -> bool:
    """
    Return whether a Coordinator status transition is allowed.

    Operational lifecycle validation only.
    No truth, retry, execution, permission, or completion authority.
    """

    return next_status in ALLOWED_COORDINATOR_TRANSITIONS.get(
        current_status,
        set(),
    )


def validate_transition(
    current_status: CoordinatorStatus,
    next_status: CoordinatorStatus,
) -> None:
    """
    Validate Coordinator lifecycle transition.

    READY_FOR_ROUTING is a terminal handoff boundary.
    EXPIRED_UNRESOLVED is a terminal unresolved boundary.
    """

    if not can_transition(current_status, next_status):
        raise CoordinatorLifecycleError(
            f"Invalid Coordinator lifecycle transition: "
            f"{current_status.value} -> {next_status.value}"
        )


def is_terminal(
    status: CoordinatorStatus,
) -> bool:
    return status in TERMINAL_COORDINATOR_STATUSES