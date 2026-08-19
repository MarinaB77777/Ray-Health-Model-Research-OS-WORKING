# runtime/tests/test_runtime_service.py

from datetime import datetime, timedelta, timezone

from runtime.schemas import (
    GovernanceDecisionStatus,
    GovernanceTargetAudience,
    GovernanceVerdictSnapshot,
    GovernanceVisibilityLevel,
    RuntimeActionClass,
    RuntimeActionRecord,
    RuntimeCompletionScope,
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


def allowed_verdict(**kwargs) -> GovernanceVerdictSnapshot:
    data = {
        "governance_decision_status": GovernanceDecisionStatus.ALLOWED,
        "governance_visibility_level": GovernanceVisibilityLevel.HUMAN_SAFE,
        "governance_target_audience": GovernanceTargetAudience.PRIMARY_HUMAN,
        "governance_confirmation_required": False,
    }
    data.update(kwargs)
    return GovernanceVerdictSnapshot(**data)


def test_runtime_completes_only_runtime_step_without_claiming_world_effect():
    service = RuntimeService()
    result = service.process_action(make_action(allowed_verdict()))

    assert result.success is True
    assert result.status == RuntimeStatus.COMPLETED
    assert result.completion_scope == RuntimeCompletionScope.RUNTIME_STEP
    assert result.external_effect_verified is False
    assert result.verification_evidence == {}


def test_runtime_rejects_expired_governance_verdict():
    issued = datetime.now(timezone.utc) - timedelta(minutes=10)
    verdict = allowed_verdict(
        issued_at=issued,
        valid_until=issued + timedelta(minutes=1),
    )

    result = RuntimeService().process_action(make_action(verdict))

    assert result.success is False
    assert result.reanalysis_requested is True
    assert result.status == RuntimeStatus.NEEDS_REANALYSIS
    assert result.error_code == "GOVERNANCE_VERDICT_EXPIRED"


def test_runtime_rejects_revoked_governance_verdict():
    verdict = allowed_verdict(
        revoked=True,
        revocation_reason="Human revoked the operational permission.",
    )

    result = RuntimeService().process_action(make_action(verdict))

    assert result.success is False
    assert result.reanalysis_requested is True
    assert result.status == RuntimeStatus.NEEDS_REANALYSIS
    assert result.error_code == "GOVERNANCE_VERDICT_REVOKED"


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
    action = make_action(allowed_verdict())
    action.human_prohibition_active = True

    result = RuntimeService().process_action(action)

    assert result.success is False
    assert result.blocked is True
    assert result.status == RuntimeStatus.BLOCKED_BY_HUMAN
