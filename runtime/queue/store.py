from typing import Optional
from datetime import datetime

from runtime.queue.contracts import (
    RuntimeQueueItem,
    RuntimeQueueStatus,
    RuntimeQueueBlockReason,
    utc_now,
)


class RuntimeQueueStore:
    """
    Bounded in-memory Runtime Queue Store.

    Queue Store is NOT:
    - planner;
    - governance;
    - execution engine;
    - truth authority;
    - memory system.

    It stores operational queue items only.
    """

    def __init__(self) -> None:
        self._items: dict[str, RuntimeQueueItem] = {}

    def add_item(
        self,
        item: RuntimeQueueItem,
    ) -> RuntimeQueueItem:

        self._items[item.queue_id] = item
        return item

    def get_item(
        self,
        queue_id: str,
    ) -> Optional[RuntimeQueueItem]:

        return self._items.get(queue_id)

    def update_status(
        self,
        queue_id: str,
        status: RuntimeQueueStatus,
        block_reason: Optional[RuntimeQueueBlockReason] = None,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        item = self.get_item(queue_id)

        if item is None:
            return None

        update_data = item.model_dump()

        update_data["status"] = status
        update_data["block_reason"] = block_reason
        update_data["updated_at"] = utc_now()

        if explanation is not None:
            update_data["explanation"] = explanation

        updated_item = RuntimeQueueItem.model_validate(update_data)

        self._items[queue_id] = updated_item

        return updated_item

    def mark_blocked(
        self,
        queue_id: str,
        block_reason: RuntimeQueueBlockReason,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.BLOCKED,
            block_reason=block_reason,
            explanation=explanation,
        )

    def mark_waiting_governance(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.WAITING_GOVERNANCE,
            block_reason=RuntimeQueueBlockReason.GOVERNANCE_REQUIRED,
            explanation=explanation,
        )

    def mark_waiting_human_confirmation(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.WAITING_HUMAN_CONFIRMATION,
            block_reason=RuntimeQueueBlockReason.HUMAN_CONFIRMATION_REQUIRED,
            explanation=explanation,
        )

    def mark_waiting_clarification(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.WAITING_CLARIFICATION,
            block_reason=RuntimeQueueBlockReason.CLARIFICATION_REQUIRED,
            explanation=explanation,
        )

    def mark_waiting_dependency(
        self,
        queue_id: str,
        dependency_ref: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        item = self.get_item(queue_id)

        if item is None:
            return None

        update_data = item.model_dump()

        update_data["status"] = RuntimeQueueStatus.WAITING_DEPENDENCY
        update_data["block_reason"] = RuntimeQueueBlockReason.DEPENDENCY_WAIT
        update_data["waiting_for"] = dependency_ref
        update_data["updated_at"] = utc_now()

        if explanation is not None:
            update_data["explanation"] = explanation

        updated_item = RuntimeQueueItem.model_validate(update_data)

        self._items[queue_id] = updated_item

        return updated_item

    def mark_ready(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.READY,
            block_reason=None,
            explanation=explanation,
        )

    def mark_in_progress(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.IN_PROGRESS,
            block_reason=None,
            explanation=explanation,
        )

    def mark_completed(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.COMPLETED,
            block_reason=None,
            explanation=explanation,
        )

    def mark_cancelled(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.CANCELLED,
            block_reason=RuntimeQueueBlockReason.CANCELLED_BY_HUMAN,
            explanation=explanation,
        )

    def mark_expired(
        self,
        queue_id: str,
        explanation: Optional[str] = None,
    ) -> Optional[RuntimeQueueItem]:

        return self.update_status(
            queue_id=queue_id,
            status=RuntimeQueueStatus.EXPIRED,
            block_reason=RuntimeQueueBlockReason.EXPIRED,
            explanation=explanation,
        )

    def list_all(self) -> list[RuntimeQueueItem]:
        return list(self._items.values())

    def list_pending(self) -> list[RuntimeQueueItem]:
        return [
            item
            for item in self._items.values()
            if item.status == RuntimeQueueStatus.PENDING
        ]

    def list_ready(
        self,
        now: Optional[datetime] = None,
    ) -> list[RuntimeQueueItem]:

        now = now or utc_now()

        return [
            item
            for item in self._items.values()
            if item.can_be_processed(now)
        ]

    def list_waiting(self) -> list[RuntimeQueueItem]:
        return [
            item
            for item in self._items.values()
            if item.is_waiting()
        ]

    def list_blocked(self) -> list[RuntimeQueueItem]:
        return [
            item
            for item in self._items.values()
            if item.is_blocked()
        ]

    def list_terminal(self) -> list[RuntimeQueueItem]:
        return [
            item
            for item in self._items.values()
            if item.is_terminal()
        ]

    def expire_due_items(
        self,
        now: Optional[datetime] = None,
    ) -> list[str]:

        now = now or utc_now()

        expired_ids: list[str] = []

        for item in list(self._items.values()):

            if item.is_terminal() or item.is_blocked():
                continue

            if item.expires_at is None:
                continue

            if now < item.expires_at:
                continue

            self.mark_expired(
                queue_id=item.queue_id,
                explanation="Queue item expired by time boundary.",
            )

            expired_ids.append(item.queue_id)

        return expired_ids

    def remove_item(
        self,
        queue_id: str,
    ) -> bool:

        if queue_id not in self._items:
            return False

        del self._items[queue_id]
        return True