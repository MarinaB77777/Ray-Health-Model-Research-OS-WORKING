from __future__ import annotations

from typing import Optional
from uuid import uuid4

from runtime.dispatcher.service import RuntimeDispatcherService
from runtime.queue.contracts import RuntimeQueueStatus
from runtime.queue.service import RuntimeQueueService

from runtime.coordinator.contracts import (
    RuntimeCoordinationResult,
    RuntimeCoordinationStatus,
    coordination_result_from_dispatch,
)


class RuntimeCoordinatorService:
    """
    Runtime-level bounded coordinator service.

    RuntimeCoordinatorService coordinates:
    queue -> dispatcher -> RuntimeCoordinationResult

    RuntimeCoordinatorService is NOT:
    - CoordinatorRecord storage lifecycle service;
    - planner;
    - Governance;
    - executor;
    - Analyst;
    - Analyzer;
    - truth authority.

    RuntimeCoordinationResult ≠ execution success.
    RuntimeCoordinationResult ≠ action completion.
    RuntimeCoordinationResult ≠ Runtime truth.

    It may apply explicit RuntimeCoordinationResult.next_queue_status
    to the queue only as bounded operational queue transition.
    """

    def __init__(
        self,
        queue_service: Optional[RuntimeQueueService] = None,
        dispatcher_service: Optional[RuntimeDispatcherService] = None,
    ) -> None:
        self.queue_service = queue_service or RuntimeQueueService()

        self.dispatcher_service = (
            dispatcher_service
            or RuntimeDispatcherService(queue_service=self.queue_service)
        )

    def coordinate_next(
        self,
        coordination_id: Optional[str] = None,
    ) -> RuntimeCoordinationResult:
        """
        Coordinate next available operational dispatch.

        This does NOT:
        - invent work;
        - execute actions;
        - grant permissions;
        - prove real-world success;
        - perform planning;
        - perform Analyst reasoning;
        - perform Governance.
        """

        coordination_id = coordination_id or f"coord-{uuid4()}"

        dispatch_decision = self.dispatcher_service.select_next_dispatch()

        result = coordination_result_from_dispatch(
            coordination_id=coordination_id,
            dispatch_decision=dispatch_decision,
        )

        if (
            result.status == RuntimeCoordinationStatus.HANDOFF_PREPARED
            and result.next_queue_status == RuntimeQueueStatus.IN_PROGRESS
            and dispatch_decision.queue_id is not None
        ):
            self.queue_service.mark_in_progress(
                queue_id=dispatch_decision.queue_id,
                explanation=(
                    "Queue item marked in progress after bounded "
                    "coordination handoff preparation. "
                    "This does not mean execution or success."
                ),
            )

            result.routing_trace.append(
                "coordinator_applied_explicit_queue_status_update"
            )

        return result