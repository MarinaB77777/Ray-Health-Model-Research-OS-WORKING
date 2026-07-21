# runtime/acquisition/lifecycle.py

from __future__ import annotations

from runtime.acquisition.contracts import AcquisitionStatus


TERMINAL_STATUSES = {
    AcquisitionStatus.BLOCKED,
    AcquisitionStatus.FAILED,
    AcquisitionStatus.UNRESOLVED,
    AcquisitionStatus.CLOSED,
}


ALLOWED_TRANSITIONS: dict[
    AcquisitionStatus,
    set[AcquisitionStatus],
] = {
    AcquisitionStatus.CREATED: {
        AcquisitionStatus.WAITING,
        AcquisitionStatus.BLOCKED,
        AcquisitionStatus.FAILED,
    },
    AcquisitionStatus.WAITING: {
        AcquisitionStatus.RESULT_RECEIVED,
        AcquisitionStatus.NEEDS_MORE_DATA,
        AcquisitionStatus.FAILED,
        AcquisitionStatus.UNRESOLVED,
        AcquisitionStatus.BLOCKED,
    },
    AcquisitionStatus.RESULT_RECEIVED: {
        AcquisitionStatus.FILTERED,
        AcquisitionStatus.BLOCKED,
        AcquisitionStatus.FAILED,
    },
    AcquisitionStatus.FILTERED: {
        AcquisitionStatus.NEEDS_MORE_DATA,
        AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
        AcquisitionStatus.BLOCKED,
    },
    AcquisitionStatus.NEEDS_MORE_DATA: {
        AcquisitionStatus.WAITING,
        AcquisitionStatus.UNRESOLVED,
        AcquisitionStatus.BLOCKED,
    },
    AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS: {
        AcquisitionStatus.CLOSED,
    },
    AcquisitionStatus.SUFFICIENT_FOR_FORECAST: {
        AcquisitionStatus.CLOSED,
    },
    AcquisitionStatus.BLOCKED: set(),
    AcquisitionStatus.FAILED: set(),
    AcquisitionStatus.UNRESOLVED: set(),
    AcquisitionStatus.CLOSED: set(),
}


class AcquisitionLifecycle:
    """
    Acquisition lifecycle transition validator.

    It is NOT:
    - Runtime;
    - Governance;
    - planner;
    - executor;
    - Analyst;
    - truth authority;
    - cancellation authority.

    It only answers:
    can acquisition status move from A to B?

    UNRESOLVED means acquisition lifecycle unresolved.
    It does NOT mean the human task is solved.
    """

    def can_transition(
        self,
        current_status: AcquisitionStatus,
        next_status: AcquisitionStatus,
    ) -> bool:
        return next_status in ALLOWED_TRANSITIONS.get(
            current_status,
            set(),
    )
    def validate_transition(
        self,
        current_status: AcquisitionStatus,
        next_status: AcquisitionStatus,
    ) -> None:
        if not self.can_transition(
            current_status=current_status,
            next_status=next_status,
        ):
            raise ValueError(
                "Invalid acquisition lifecycle transition: "
                f"{current_status.value} -> {next_status.value}"
            )

    def is_terminal(
        self,
        status: AcquisitionStatus,
    ) -> bool:
        return status in TERMINAL_STATUSES