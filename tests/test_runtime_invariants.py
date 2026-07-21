from copy import deepcopy

from runtime.communication_router import CommunicationRouter
from runtime.executor import RuntimeExecutor
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


def make_verdict(
    decision_status=GovernanceDecisionStatus.ALLOWED,
    visibility=GovernanceVisibilityLevel.HUMAN_SAFE,
    target=GovernanceTargetAudience.PRIMARY_HUMAN,
    confirmation_required=False,
):
    return GovernanceVerdictSnapshot(
        governance_decision_status=decision_status,
        governance_visibility_level=visibility,
        governance_target_audience=target,
        governance_confirmation_required=confirmation_required,
        restrictions=[],
        reason_codes=[],
    )


def make_action(verdict):
    return RuntimeActionRecord(
        action_id="runtime_inv_1",
        action_class=RuntimeActionClass.COMMUNICATION,
        risk_level=RuntimeRiskLevel.LOW,
        created_by_type="test",
        runtime_status=RuntimeStatus.QUEUED,
        payload={
            "internal": {
                "secret": "raw_internal_data"
            },
            "human_safe": {
                "message": "safe_for_human"
            },
            "public": {
                "message": "public_safe"
            },
        },
        governance_verdict=verdict,
    )


# =====================================================
# Runtime MUST NOT mutate GovernanceVerdict
# =====================================================

def test_runtime_does_not_mutate_governance_verdict():

    verdict = make_verdict()

    original = deepcopy(verdict.model_dump())

    action = make_action(verdict)

    executor = RuntimeExecutor()

    executor.execute(action)

    after = verdict.model_dump()

    assert original == after


# =====================================================
# Blocked actions MUST NEVER execute
# =====================================================

def test_blocked_action_never_executes():

    verdict = make_verdict(
        decision_status=GovernanceDecisionStatus.BLOCKED
    )

    action = make_action(verdict)

    executor = RuntimeExecutor()

    result = executor.execute(action)

    assert result.success is False
    assert result.blocked is True
    assert result.status == RuntimeStatus.BLOCKED_BY_GOVERNANCE

    event_types = [
        event.event_type.value
        for event in result.events
    ]

    assert "execution_started" not in event_types
    assert "execution_completed" not in event_types


# =====================================================
# Runtime MUST NEVER bypass confirmation
# =====================================================

def test_runtime_never_bypasses_confirmation():

    verdict = make_verdict(
        decision_status=GovernanceDecisionStatus.RESTRICTED,
        confirmation_required=True,
    )

    action = make_action(verdict)

    executor = RuntimeExecutor()

    result = executor.execute(action)

    assert result.awaiting_human is True
    assert result.status == RuntimeStatus.AWAITING_HUMAN

    event_types = [
        event.event_type.value
        for event in result.events
    ]

    assert "execution_started" not in event_types


# =====================================================
# Runtime MUST NEVER expose internal payload externally
# =====================================================

def test_external_delivery_never_receives_internal_payload():

    verdict = make_verdict(
        visibility=GovernanceVisibilityLevel.PUBLIC_FILTERED,
        target=GovernanceTargetAudience.EXTERNAL_AI,
    )

    action = make_action(verdict)

    router = CommunicationRouter()

    delivery = router.build_delivery_plan(action)

    payload = delivery.payload

    assert "internal" not in payload

    assert payload == {
        "visibility": "public_filtered",
        "payload": {
            "message": "public_safe"
        },
    }


# =====================================================
# Terminal statuses MUST NOT re-enter execution
# =====================================================

def test_terminal_status_must_not_reenter_execution():

    verdict = make_verdict()

    action = make_action(verdict)

    action.runtime_status = RuntimeStatus.COMPLETED

    executor = RuntimeExecutor()

    try:
        executor.execute(action)

    except ValueError:
        assert True

    else:
        assert False