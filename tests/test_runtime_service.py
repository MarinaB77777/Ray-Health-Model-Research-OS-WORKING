# runtime/tests/test_runtime_service.py

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
from runtime.service import RuntimeService


def make_action(verdict: GovernanceVerdictSnapshot) -> RuntimeActionRecord:
    return RuntimeActionRecord(
        action_id="action_test_1",
        action_class=RuntimeActionClass.COMMUNICATION,
        risk_level=RuntimeRiskLevel.LOW,
        created_by_type="human",
        created_by_id="primary_human",
        domain_owner="work",
        payload={
            "internal": {"secret": "internal only"},
            "human_safe": {"message": "Human-safe message"},
            "public": {"message": "Public message"},
        },
        governance_verdict=verdict,
    )


def test_runtime_executes_allowed_action():
    verdict = GovernanceVerdictSnapshot(
        governance_decision_status=GovernanceDecisionStatus.ALLOWED,
        governance_visibility_level=GovernanceVisibilityLevel.HUMAN_SAFE,
        governance_target_audience=GovernanceTargetAudience.PRIMARY_HUMAN,
        governance_confirmation_required=False,
    )

    service = RuntimeService()
    result = service.process_action(make_action(verdict))

    assert result.success is True
    assert result.status == RuntimeStatus.COMPLETED


def test_runtime_blocks_governance_blocked_action():
    verdict = GovernanceVerdictSnapshot(
        governance_decision_status=GovernanceDecisionStatus.BLOCKED,
        governance_visibility_level=GovernanceVisibilityLevel.INTERNAL_ONLY,
        governance_target_audience=GovernanceTargetAudience.INTERNAL_RAY,
        governance_confirmation_required=False,
        reason_codes=["TEST_BLOCK"],
    )

    service = RuntimeService()
    result = service.process_action(make_action(verdict))

    assert result.success is False
    assert result.blocked is True
    assert result.status == RuntimeStatus.BLOCKED_BY_GOVERNANCE


def test_runtime_waits_when_confirmation_required():
    verdict = GovernanceVerdictSnapshot(
        governance_decision_status=GovernanceDecisionStatus.RESTRICTED,
        governance_visibility_level=GovernanceVisibilityLevel.HUMAN_SAFE,
        governance_target_audience=GovernanceTargetAudience.PRIMARY_HUMAN,
        governance_confirmation_required=True,
    )

    service = RuntimeService()
    result = service.process_action(make_action(verdict))

    assert result.success is False
    assert result.awaiting_human is True
    assert result.status == RuntimeStatus.AWAITING_HUMAN


def test_runtime_requests_reanalysis_on_not_enough_data():
    verdict = GovernanceVerdictSnapshot(
        governance_decision_status=GovernanceDecisionStatus.NOT_ENOUGH_DATA,
        governance_visibility_level=GovernanceVisibilityLevel.INTERNAL_ONLY,
        governance_target_audience=GovernanceTargetAudience.INTERNAL_RAY,
        governance_confirmation_required=True,
        reason_codes=["NOT_ENOUGH_DATA"],
    )

    service = RuntimeService()
    result = service.process_action(make_action(verdict))

    assert result.success is False
    assert result.reanalysis_requested is True
    assert result.status == RuntimeStatus.NEEDS_REANALYSIS


def test_human_prohibition_blocks_runtime():
    verdict = GovernanceVerdictSnapshot(
        governance_decision_status=GovernanceDecisionStatus.ALLOWED,
        governance_visibility_level=GovernanceVisibilityLevel.HUMAN_SAFE,
        governance_target_audience=GovernanceTargetAudience.PRIMARY_HUMAN,
        governance_confirmation_required=False,
    )

    action = make_action(verdict)
    action.human_prohibition_active = True

    service = RuntimeService()
    result = service.process_action(action)

    assert result.success is False
    assert result.blocked is True
    assert result.status == RuntimeStatus.BLOCKED_BY_HUMAN