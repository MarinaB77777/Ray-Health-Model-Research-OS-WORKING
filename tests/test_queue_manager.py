# tests/test_queue_manager.py

from datetime import datetime, timedelta, timezone

from runtime.queue_manager import RuntimeQueueManager
from runtime.schemas import (
    GovernanceDecisionStatus,
    GovernanceTargetAudience,
    GovernanceVerdictSnapshot,
    GovernanceVisibilityLevel,
    RuntimeActionClass,
    RuntimeActionRecord,
    RuntimeRiskLevel,
    RuntimeStatus,
)


def make_action(
    action_id: str,
    risk_level: RuntimeRiskLevel = RuntimeRiskLevel.LOW,
    deadline_at: str | None = None,
    expires_at: str | None = None,
    status: RuntimeStatus = RuntimeStatus.NOT_STARTED,
    verdict: GovernanceVerdictSnapshot | None = None,
) -> RuntimeActionRecord:
    return RuntimeActionRecord(
        action_id=action_id,
        action_class=RuntimeActionClass.OPERATIONAL,
        risk_level=risk_level,
        created_by_type="test",
        runtime_status=status,
        deadline_at=deadline_at,
        expires_at=expires_at,
        governance_verdict=verdict,
    )


def make_verdict(
    decision_status: GovernanceDecisionStatus = GovernanceDecisionStatus.ALLOWED,
    confirmation_required: bool = False,
) -> GovernanceVerdictSnapshot:
    return GovernanceVerdictSnapshot(
        governance_decision_status=decision_status,
        governance_visibility_level=GovernanceVisibilityLevel.INTERNAL_ONLY,
        governance_target_audience=GovernanceTargetAudience.INTERNAL_RAY,
        governance_confirmation_required=confirmation_required,
    )


def test_not_started_action_becomes_queued():
    manager = RuntimeQueueManager()
    action = make_action("q1")

    prepared = manager.prepare_for_queue(action)

    assert prepared.runtime_status == RuntimeStatus.QUEUED


def test_expired_action_becomes_expired():
    manager = RuntimeQueueManager()

    expired_time = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    ).isoformat()

    action = make_action(
        "q2",
        expires_at=expired_time,
    )

    prepared = manager.prepare_for_queue(action)

    assert prepared.runtime_status == RuntimeStatus.EXPIRED


def test_confirmation_required_becomes_awaiting_human():
    manager = RuntimeQueueManager()

    action = make_action(
        "q3",
        verdict=make_verdict(
            decision_status=GovernanceDecisionStatus.RESTRICTED,
            confirmation_required=True,
        ),
    )

    prepared = manager.prepare_for_queue(action)

    assert prepared.runtime_status == RuntimeStatus.AWAITING_HUMAN


def test_not_enough_data_becomes_needs_reanalysis():
    manager = RuntimeQueueManager()

    action = make_action(
        "q4",
        verdict=make_verdict(
            decision_status=GovernanceDecisionStatus.NOT_ENOUGH_DATA,
        ),
    )

    prepared = manager.prepare_for_queue(action)

    assert prepared.runtime_status == RuntimeStatus.NEEDS_REANALYSIS


def test_sort_queue_prioritizes_risk_then_deadline():
    manager = RuntimeQueueManager()

    now = datetime.now(timezone.utc)

    low_early = make_action(
        "low_early",
        risk_level=RuntimeRiskLevel.LOW,
        deadline_at=(now + timedelta(hours=1)).isoformat(),
        status=RuntimeStatus.QUEUED,
    )

    high_late = make_action(
        "high_late",
        risk_level=RuntimeRiskLevel.HIGH,
        deadline_at=(now + timedelta(hours=5)).isoformat(),
        status=RuntimeStatus.QUEUED,
    )

    high_early = make_action(
        "high_early",
        risk_level=RuntimeRiskLevel.HIGH,
        deadline_at=(now + timedelta(hours=2)).isoformat(),
        status=RuntimeStatus.QUEUED,
    )

    sorted_actions = manager.sort_queue(
        [low_early, high_late, high_early]
    )

    assert [a.action_id for a in sorted_actions] == [
        "high_early",
        "high_late",
        "low_early",
    ]