from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from runtime.shared_action.schemas import (
    ActionCompletionScope,
    ActionStatus,
    BlockReason,
    OwnerType,
    SharedActionRecord,
    utc_now,
)
from runtime.shared_action.statuses import assert_transition_allowed


@dataclass(frozen=True)
class StatusUpdateRequest:
    """Request for lifecycle status update."""

    target_status: ActionStatus
    block_reason: Optional[BlockReason] = None
    owner_type: Optional[OwnerType] = None
    owner_id: Optional[str] = None
    completion_scope: Optional[ActionCompletionScope] = None
    external_effect_verified: bool = False
    completion_evidence: dict[str, Any] = field(default_factory=dict)


def apply_status_update(
    record: SharedActionRecord,
    request: StatusUpdateRequest,
) -> SharedActionRecord:
    """Apply an operational lifecycle transition.

    `completed` is a coordination state, not automatic proof of real-world
    completion. The caller must state what was completed.
    """

    assert_transition_allowed(
        current_status=record.status,
        target_status=request.target_status,
    )

    update_data = {
        "status": request.target_status,
        "updated_at": utc_now(),
    }

    if request.target_status == ActionStatus.blocked:
        if request.block_reason is None:
            raise ValueError("transition to blocked requires block_reason")
        update_data["block_reason"] = request.block_reason
    else:
        update_data["block_reason"] = None

    if request.target_status == ActionStatus.forbidden_by_human:
        update_data["forbidden_by_human"] = True

    if request.owner_type is not None:
        update_data["owner_type"] = request.owner_type
    if request.owner_id is not None:
        update_data["owner_id"] = request.owner_id

    if request.target_status == ActionStatus.completed:
        if request.completion_scope is None:
            raise ValueError("transition to completed requires completion_scope")
        update_data["completion_scope"] = request.completion_scope
        update_data["external_effect_verified"] = request.external_effect_verified
        update_data["completion_evidence"] = dict(request.completion_evidence)
    else:
        if (
            request.completion_scope is not None
            or request.external_effect_verified
            or request.completion_evidence
        ):
            raise ValueError(
                "completion fields are only valid when target_status=completed"
            )
        update_data["completion_scope"] = None
        update_data["external_effect_verified"] = False
        update_data["completion_evidence"] = {}

    updated = record.model_copy(update=update_data)
    return SharedActionRecord(**updated.model_dump())