from governance.service import GovernanceService
from runtime.governance_client import GovernanceClient
from runtime.schemas import GovernanceDecisionStatus


def test_current_governance_service_requires_explicit_action_and_context():
    client = GovernanceClient(governance_service=GovernanceService())

    verdict = client.get_verdict({"some": "arbitrary runtime payload"})

    assert verdict.governance_decision_status == GovernanceDecisionStatus.NOT_ENOUGH_DATA
    assert "GOVERNANCE_CONTEXT_REQUIRED" in verdict.reason_codes


def test_current_governance_service_accepts_explicit_action_and_context():
    client = GovernanceClient(governance_service=GovernanceService())

    verdict = client.get_verdict(
        {
            "governance_action": {
                "action_id": "runtime-governed-1",
                "action_type": "internal_review",
            },
            "governance_context": {
                "trust_level": "basic_trust",
            },
        }
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.ALLOWED
    assert verdict.authority_scope_id == "runtime-governed-1"


def test_governance_bridge_blocks_heart_write_even_when_generic_memory_write_allowed():
    client = GovernanceClient(governance_service=GovernanceService())

    verdict = client.get_verdict(
        {
            "governance_action": {
                "action_id": "runtime-heart-write",
                "action_type": "write_memory",
                "requires_memory_write": True,
                "memory_class": "heart_of_ray",
            },
            "governance_context": {
                "trust_level": "deep_trust",
                "memory_write_allowed": True,
            },
        }
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert "HEART_IS_NOT_MEMORY" in verdict.reason_codes
    assert verdict.authority_scope_id == "runtime-heart-write"


def test_missing_governance_service_fails_closed():
    verdict = GovernanceClient().get_verdict({})

    assert verdict.governance_decision_status == GovernanceDecisionStatus.NOT_ENOUGH_DATA
    assert "GOVERNANCE_SERVICE_MISSING" in verdict.reason_codes
