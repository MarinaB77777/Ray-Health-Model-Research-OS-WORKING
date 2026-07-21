import pytest
from pydantic import ValidationError

from runtime.shared_action.schemas import (
    ActionSource,
    ActionStatus,
    ActionType,
    BlockReason,
    OwnerType,
    SharedActionRecord,
)
from runtime.shared_action.updates import (
    StatusUpdateRequest,
    apply_status_update,
)


def make_record(**overrides) -> SharedActionRecord:
    data = {
        "action_id": "action-1",
        "action_type": ActionType.ray_support_task,
        "source": ActionSource.runtime,
        "status": ActionStatus.candidate,
    }
    data.update(overrides)
    return SharedActionRecord(**data)


def test_apply_candidate_to_proposed():
    record = make_record()

    updated = apply_status_update(
        record,
        StatusUpdateRequest(target_status=ActionStatus.proposed),
    )

    assert updated.status == ActionStatus.proposed
    assert updated.updated_at >= record.updated_at


def test_invalid_transition_raises():
    record = make_record(status=ActionStatus.proposed)

    with pytest.raises(ValueError):
        apply_status_update(
            record,
            StatusUpdateRequest(target_status=ActionStatus.assigned),
        )


def test_transition_to_blocked_requires_block_reason():
    record = make_record(status=ActionStatus.accepted)

    with pytest.raises(ValueError):
        apply_status_update(
            record,
            StatusUpdateRequest(target_status=ActionStatus.blocked),
        )


def test_transition_to_blocked_with_reason():
    record = make_record(status=ActionStatus.accepted)

    updated = apply_status_update(
        record,
        StatusUpdateRequest(
            target_status=ActionStatus.blocked,
            block_reason=BlockReason.dependency,
        ),
    )

    assert updated.status == ActionStatus.blocked
    assert updated.block_reason == BlockReason.dependency


def test_unblocked_status_clears_block_reason():
    record = make_record(
        status=ActionStatus.blocked,
        block_reason=BlockReason.dependency,
    )

    updated = apply_status_update(
        record,
        StatusUpdateRequest(
            target_status=ActionStatus.assigned,
            owner_type=OwnerType.domain_ray,
            owner_id="work-ray",
        ),
    )

    assert updated.status == ActionStatus.assigned
    assert updated.block_reason is None


def test_assigned_requires_owner_through_schema_validation():
    record = make_record(status=ActionStatus.accepted)

    with pytest.raises(ValidationError):
        apply_status_update(
            record,
            StatusUpdateRequest(target_status=ActionStatus.assigned),
        )


def test_assigned_with_owner_is_valid():
    record = make_record(status=ActionStatus.accepted)

    updated = apply_status_update(
        record,
        StatusUpdateRequest(
            target_status=ActionStatus.assigned,
            owner_type=OwnerType.domain_ray,
            owner_id="academic-ray",
        ),
    )

    assert updated.status == ActionStatus.assigned
    assert updated.owner_type == OwnerType.domain_ray
    assert updated.owner_id == "academic-ray"


def test_in_progress_requires_existing_or_new_owner():
    record = make_record(
        status=ActionStatus.assigned,
        owner_type=OwnerType.domain_ray,
        owner_id="academic-ray",
    )

    updated = apply_status_update(
        record,
        StatusUpdateRequest(target_status=ActionStatus.in_progress),
    )

    assert updated.status == ActionStatus.in_progress
    assert updated.owner_id == "academic-ray"


def test_forbidden_by_human_sets_hard_flag():
    record = make_record(status=ActionStatus.proposed)

    updated = apply_status_update(
        record,
        StatusUpdateRequest(target_status=ActionStatus.forbidden_by_human),
    )

    assert updated.status == ActionStatus.forbidden_by_human
    assert updated.forbidden_by_human is True


def test_forbidden_by_human_cannot_reactivate():
    record = make_record(
        status=ActionStatus.forbidden_by_human,
        forbidden_by_human=True,
    )

    with pytest.raises(ValueError):
        apply_status_update(
            record,
            StatusUpdateRequest(target_status=ActionStatus.proposed),
        )