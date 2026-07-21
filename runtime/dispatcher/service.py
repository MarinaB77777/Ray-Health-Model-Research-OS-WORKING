from typing import Optional
from datetime import datetime

from runtime.dispatcher.contracts import (
    RuntimeDispatchDecision,
    RuntimeDispatchReason,
    RuntimeDispatchStatus,
    dispatch_decision_from_queue_item,
)

from runtime.queue.contracts import (
    RuntimeQueueItem,
)

from runtime.queue.service import RuntimeQueueService


class RuntimeDispatcherService:
    """
    Bounded Runtime Dispatcher Service.

    Dispatcher Service is NOT:
    - planner;
    - governance;
    - executor;
    - Analyst;
    - truth authority.

    Dispatcher Service only:
    - selects processable queue items;
    - produces bounded dispatch decisions;
    - coordinates operational handoff preparation.
    """

    def __init__(
        self,
        queue_service: Optional[RuntimeQueueService] = None,
    ) -> None:
        self.queue_service = queue_service or RuntimeQueueService()

    def list_ready_items(
        self,
        now: Optional[datetime] = None,
    ) -> list[RuntimeQueueItem]:

        return self.queue_service.list_ready(now)

    def dispatch_queue_item(
        self,
        item: RuntimeQueueItem,
        now: Optional[datetime] = None,
    ) -> RuntimeDispatchDecision:
        """
        Dispatch decision does NOT:
        - execute actions;
        - grant permissions;
        - prove success;
        - prove correctness of world interpretation.
        """

        return dispatch_decision_from_queue_item(
            item=item,
            now=now,
        )

    def select_next_dispatch(
        self,
        now: Optional[datetime] = None,
    ) -> RuntimeDispatchDecision:
        """
        Selecting next dispatch does NOT:
        - invent work;
        - bypass queue boundaries;
        - bypass governance;
        - create hidden orchestration authority.
        """

        ready_items = self.list_ready_items(now)

        if not ready_items:
            return RuntimeDispatchDecision(
                dispatch_status=RuntimeDispatchStatus.NO_READY_ITEMS,
                dispatch_reason=(
                    RuntimeDispatchReason.NO_AVAILABLE_READY_ITEMS
                ),
                explanation=(
                    "No processable queue items available for dispatch."
                ),
                routing_trace=[
                    "dispatcher_checked_ready_queue",
                ],
             )

        selected_item = ready_items[0]

        decision = self.dispatch_queue_item(
            item=selected_item,
            now=now,
        )

        decision.routing_trace.append(
            "dispatcher_selected_ready_item"
        )

        return decision