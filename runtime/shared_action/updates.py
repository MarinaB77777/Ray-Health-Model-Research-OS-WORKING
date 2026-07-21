from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from runtime.shared_action.schemas import (
    ActionStatus,
    BlockReason,
    OwnerType,
    SharedActionRecord,
    utc_now,
)
from runtime.shared_action.statuses import assert_transition_allowed


@dataclass(frozen=True)
class StatusUpdateRequest:
    """
    Request for lifecycle status update.

    Запрос на изменение lifecycle-статуса.
    """

    target_status: ActionStatus

    block_reason: Optional[BlockReason] = None

    owner_type: Optional[OwnerType] = None
    owner_id: Optional[str] = None


def apply_status_update(
    record: SharedActionRecord,
    request: StatusUpdateRequest,
) -> SharedActionRecord:
    """
    Apply lifecycle transition to SharedActionRecord.

    Применяет lifecycle-переход к Shared Action record.

    Runtime owns operational transitions.
    Governance returns verdicts only.
    """

    assert_transition_allowed(
        current_status=record.status,
        target_status=request.target_status,
    )

    update_data = {
        "status": request.target_status,
        "updated_at": utc_now(),
    }

    # blocked requires block_reason
    if request.target_status == ActionStatus.blocked:
        if request.block_reason is None:
            raise ValueError(
                "transition to blocked requires block_reason"
            )

        update_data["block_reason"] = request.block_reason

    else:
        update_data["block_reason"] = None

    # forbidden_by_human is hard boundary
    if request.target_status == ActionStatus.forbidden_by_human:
        update_data["forbidden_by_human"] = True

    # optional ownership update
    if request.owner_type is not None:
        update_data["owner_type"] = request.owner_type

    if request.owner_id is not None:
        update_data["owner_id"] = request.owner_id

    updated = record.model_copy(update=update_data)

    # Force full validation after update
    return SharedActionRecord(**updated.model_dump())