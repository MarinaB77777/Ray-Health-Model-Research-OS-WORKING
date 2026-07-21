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


def make_record(**overrides) -> SharedActionRecord:
    data = {
        "action_id": "action-1",
        "action_type": ActionType.ray_support_task,
        "source": ActionSource.runtime,
        "status": ActionStatus.candidate,
    }
    data.update(overrides)
    return SharedActionRecord(**data)


def test_candidate_record_is_valid():
    record = make_record()

    assert record.action_id == "action-1"
    assert record.status == ActionStatus.candidate
    assert record.owner_type == OwnerType.unassigned


def test_assigned_requires_owner():
    with pytest.raises(ValidationError):
        make_record(status=ActionStatus.assigned)


def test_in_progress_requires_owner():
    with pytest.raises(ValidationError):
        make_record(status=ActionStatus.in_progress)


def test_assigned_with_owner_is_valid():
    record = make_record(
        status=ActionStatus.assigned,
        owner_type=OwnerType.domain_ray,
        owner_id="career-ray",
    )

    assert record.status == ActionStatus.assigned
    assert record.owner_id == "career-ray"


def test_blocked_requires_block_reason():
    with pytest.raises(ValidationError):
        make_record(status=ActionStatus.blocked)


def test_block_reason_only_allowed_when_blocked():
    with pytest.raises(ValidationError):
        make_record(
            status=ActionStatus.accepted,
            block_reason=BlockReason.dependency,
        )


def test_forbidden_status_requires_forbidden_flag():
    with pytest.raises(ValidationError):
        make_record(status=ActionStatus.forbidden_by_human)


def test_forbidden_flag_requires_forbidden_status():
    with pytest.raises(ValidationError):
        make_record(
            status=ActionStatus.accepted,
            forbidden_by_human=True,
        )


def test_relevance_score_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        make_record(relevance_score=1.5)

    with pytest.raises(ValidationError):
        make_record(relevance_score=-0.1)


def test_relevance_score_valid_range():
    record = make_record(relevance_score=0.8)

    assert record.relevance_score == 0.8