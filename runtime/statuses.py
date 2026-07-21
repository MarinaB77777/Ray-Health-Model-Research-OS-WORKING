# runtime/statuses.py

from __future__ import annotations

from typing import Dict, Set

from runtime.schemas import RuntimeStatus


TERMINAL_STATUSES: Set[RuntimeStatus] = {
    RuntimeStatus.COMPLETED,
    RuntimeStatus.FAILED,
    RuntimeStatus.EXPIRED,
    RuntimeStatus.CANCELED,
    RuntimeStatus.BLOCKED_BY_GOVERNANCE,
    RuntimeStatus.BLOCKED_BY_HUMAN,
}


ALLOWED_TRANSITIONS: Dict[RuntimeStatus, Set[RuntimeStatus]] = {
    RuntimeStatus.NOT_STARTED: {
        RuntimeStatus.QUEUED,
        RuntimeStatus.AWAITING_HUMAN,
        RuntimeStatus.BLOCKED_BY_GOVERNANCE,
        RuntimeStatus.BLOCKED_BY_HUMAN,
        RuntimeStatus.NEEDS_REANALYSIS,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
    },

    RuntimeStatus.QUEUED: {
        RuntimeStatus.EXECUTING,
        RuntimeStatus.AWAITING_HUMAN,
        RuntimeStatus.PAUSED,
        RuntimeStatus.BLOCKED_BY_GOVERNANCE,
        RuntimeStatus.BLOCKED_BY_HUMAN,
        RuntimeStatus.NEEDS_REANALYSIS,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
    },

    RuntimeStatus.EXECUTING: {
        RuntimeStatus.COMPLETED,
        RuntimeStatus.FAILED,
        RuntimeStatus.AWAITING_HUMAN,
        RuntimeStatus.AWAITING_EXTERNAL,
        RuntimeStatus.RETRY_PENDING,
        RuntimeStatus.PAUSED,
        RuntimeStatus.NEEDS_REANALYSIS,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
    },

    RuntimeStatus.AWAITING_HUMAN: {
        RuntimeStatus.QUEUED,
        RuntimeStatus.EXECUTING,
        RuntimeStatus.NEEDS_REANALYSIS,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
        RuntimeStatus.BLOCKED_BY_HUMAN,
    },

    RuntimeStatus.AWAITING_EXTERNAL: {
        RuntimeStatus.QUEUED,
        RuntimeStatus.EXECUTING,
        RuntimeStatus.RETRY_PENDING,
        RuntimeStatus.FAILED,
        RuntimeStatus.NEEDS_REANALYSIS,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
    },

    RuntimeStatus.RETRY_PENDING: {
        RuntimeStatus.QUEUED,
        RuntimeStatus.EXECUTING,
        RuntimeStatus.FAILED,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
        RuntimeStatus.NEEDS_REANALYSIS,
    },

    RuntimeStatus.PAUSED: {
        RuntimeStatus.QUEUED,
        RuntimeStatus.EXECUTING,
        RuntimeStatus.AWAITING_HUMAN,
        RuntimeStatus.NEEDS_REANALYSIS,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
    },

    RuntimeStatus.NEEDS_REANALYSIS: {
        RuntimeStatus.QUEUED,
        RuntimeStatus.AWAITING_HUMAN,
        RuntimeStatus.BLOCKED_BY_GOVERNANCE,
        RuntimeStatus.EXPIRED,
        RuntimeStatus.CANCELED,
    },

    RuntimeStatus.COMPLETED: set(),
    RuntimeStatus.FAILED: set(),
    RuntimeStatus.EXPIRED: set(),
    RuntimeStatus.CANCELED: set(),
    RuntimeStatus.BLOCKED_BY_GOVERNANCE: set(),
    RuntimeStatus.BLOCKED_BY_HUMAN: set(),
}


def is_terminal_status(status: RuntimeStatus) -> bool:
    return status in TERMINAL_STATUSES


def can_transition(
    previous_status: RuntimeStatus,
    new_status: RuntimeStatus,
) -> bool:
    if previous_status == new_status:
        return True

    if previous_status in TERMINAL_STATUSES:
        return False

    return new_status in ALLOWED_TRANSITIONS.get(previous_status, set())


def require_valid_transition(
    previous_status: RuntimeStatus,
    new_status: RuntimeStatus,
) -> None:
    if not can_transition(previous_status, new_status):
        raise ValueError(
            f"Invalid runtime status transition: "
            f"{previous_status.value} -> {new_status.value}"
        )