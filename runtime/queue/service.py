from typing import Optional
from datetime import datetime

from runtime.queue.contracts import (
    RuntimeQueueItem,
    RuntimeQueueStatus,
    RuntimeQueueBlockReason,
)

from runtime.queue.store import RuntimeQueueStore


class RuntimeQueueService:
    """
    Bounded Runtime Queue Service.

    Queue Service is NOT:
    - planner;
    - governance;
    - execution engine;
    - Analyst;
    - truth authority.

    It provides a safe operational interface over RuntimeQueueStore.
    """

    def __init__(
        self,
        store: Optional[RuntimeQueueStore] = None,
    ) -> None:
        self.store = store or RuntimeQueueStore()

    def enqueue(
        self,
        item: RuntimeQueueItem,
    ) -> RuntimeQueueItem:
        """
        Enqueue means accepted into operational queue.

        It does NOT mean:
        - approved;
        - verified;
        - executable;
        - completed.
        """
        return self.store.add_item(item)

    def get_item(
        self,
        queue_id: str,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.get_item(queue_id)

    def list_pending(
        self,
    ) -> list[RuntimeQueueItem]:
        return self.store.list_pending()

    def list_ready(
        self,
        now: Optional[datetime] = None,
    ) -> list[RuntimeQueueItem]:
        return self.store.list_ready(now)

    def list_waiting(self) -> list[RuntimeQueueItem]:
        return self.store.list_waiting()

    def list_blocked(self) -> list[RuntimeQueueItem]:
        return self.store.list_blocked()

    def list_terminal(self) -> list[RuntimeQueueItem]:
        return self.store.list_terminal()

    def mark_ready(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_ready(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_blocked(
        self,
        queue_id: str,
        block_reason: RuntimeQueueBlockReason,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_blocked(
            queue_id=queue_id,
            block_reason=block_reason,
            explanation=explanation,
        )

    def mark_waiting_governance(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_waiting_governance(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_waiting_human_confirmation(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_waiting_human_confirmation(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_waiting_clarification(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_waiting_clarification(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_waiting_dependency(
        self,
        queue_id: str,
        dependency_ref: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_waiting_dependency(
            queue_id=queue_id,
            dependency_ref=dependency_ref,
            explanation=explanation,
        )

    def mark_in_progress(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        """
        In progress means Runtime queue handling started.

        It does NOT mean real-world execution succeeded.
        """
        return self.store.mark_in_progress(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_completed(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        """
        Completed means queue handling completed.

        It does NOT prove:
        - external action succeeded;
        - user outcome was achieved;
        - real-world state changed.
        """
        return self.store.mark_completed(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_cancelled(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_cancelled(
            queue_id=queue_id,
            explanation=explanation,
        )

    def mark_expired(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:
        return self.store.mark_expired(
            queue_id=queue_id,
            explanation=explanation,
        )

    def expire_due_items(
        self,
        now: Optional[datetime] = None,
    ) -> list[str]:
        """
        Expiration marks queue items operationally expired.
        
        It does NOT:
        - physically delete queue items;
        - erase operational history;
        - prove failure severity.
        """
        return self.store.expire_due_items(now)

    def remove_item(
        self,
        queue_id: str,
    ) -> bool:
        return self.store.remove_item(queue_id)