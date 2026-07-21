from governance.schemas import (
    ProposedAction,
    GovernanceContext,
    GovernanceDecisionStatus,
    GovernanceVisibilityLevel,
    TrustLevel,
    ReversibilityLevel,
    ExternalTargetType,
    EmergencyType,
    SensitiveDomainRule,
)

from governance.rules import governance_check

from governance.visibility import (
    apply_visibility_scope,
    VisibilityFilterError,
)


def test_human_prohibition_overrides_all_other_findings():

    action = ProposedAction(
        action_id="inv_1",
        action_type="dangerous_external_action",
        requires_external_communication=True,
        external_target_type=ExternalTargetType.EXTERNAL_AI,
        requires_memory_write=True,
        memory_target="inner_core",
        requires_autonomy=True,
        reversibility_level=ReversibilityLevel.IRREVERSIBLE,
        unknown_sensitive_domains_present=True,
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        human_prohibition_active=True,
        delegated_autonomy_allowed=True,
        external_communication_allowed=True,
        memory_write_allowed=True,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert "full_action" in verdict.governance_blocked_action_scopes
    assert "human_prohibition_active" in verdict.governance_rule_hits


def test_unknown_is_never_allowed():

    action = ProposedAction(
        action_id="inv_2",
        action_type="act_with_unknown_domain",
        unknown_sensitive_domains_present=True,
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_decision_status != GovernanceDecisionStatus.ALLOWED
    assert verdict.governance_confirmation_required is True


def test_projected_emergency_does_not_authorize_action():

    action = ProposedAction(
        action_id="inv_3",
        action_type="projected_emergency_action",
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        emergency_type=EmergencyType.PROJECTED,
        factual_emergency_policy_allowed=True,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_decision_status != GovernanceDecisionStatus.ALLOWED
    assert verdict.governance_confirmation_required is True
    assert "projected_emergency_requires_confirmation" in verdict.governance_rule_hits


def test_factual_emergency_is_only_policy_scoped():

    action = ProposedAction(
        action_id="inv_4",
        action_type="factual_emergency_action",
    )

    context = GovernanceContext(
        trust_level=TrustLevel.BASIC,
        emergency_type=EmergencyType.FACTUAL,
        factual_emergency_policy_allowed=True,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_decision_status == GovernanceDecisionStatus.RESTRICTED
    assert "preapproved_emergency_scope" in verdict.governance_allowed_action_scopes
    assert "outside_emergency_scope" in verdict.governance_blocked_action_scopes


def test_inner_core_write_is_always_blocked():

    action = ProposedAction(
        action_id="inv_5",
        action_type="write_inner_core",
        requires_memory_write=True,
        memory_target="inner_core",
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        memory_write_allowed=True,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert "inner_core" in verdict.governance_blocked_memory_targets


def test_multiple_findings_are_aggregated():

    action = ProposedAction(
        action_id="inv_6",
        action_type="external_ai_irreversible_memory_action",
        requires_external_communication=True,
        external_target_type=ExternalTargetType.EXTERNAL_AI,
        requires_memory_write=True,
        memory_target="temporary_memory",
        reversibility_level=ReversibilityLevel.IRREVERSIBLE,
        affected_sensitive_domains=[
            "privacy_of_personal_data"
        ],
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        external_communication_allowed=False,
        memory_write_allowed=False,
        sensitive_domain_config={
            "privacy_of_personal_data": SensitiveDomainRule(
                domain_id="privacy_of_personal_data",
                protected=True,
                external_ai_allowed=False,
            )
        },
    )

    verdict = governance_check(action, context)

    assert verdict.governance_decision_status == GovernanceDecisionStatus.RESTRICTED
    assert verdict.governance_confirmation_required is True
    assert verdict.governance_visibility_level == GovernanceVisibilityLevel.PUBLIC_FILTERED

    assert "memory_write_not_allowed" in verdict.governance_rule_hits
    assert "external_communication_restricted" in verdict.governance_rule_hits
    assert "irreversible_action_requires_confirmation" in verdict.governance_rule_hits


def test_governance_trace_is_always_present():

    action = ProposedAction(
        action_id="inv_7",
        action_type="simple_action",
    )

    context = GovernanceContext(
        trust_level=TrustLevel.BASIC,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_trace_id
    assert verdict.governance_version


def test_public_visibility_requires_public_payload():

    action = ProposedAction(
        action_id="inv_8",
        action_type="external_ai_action",
        requires_external_communication=True,
        external_target_type=ExternalTargetType.EXTERNAL_AI,
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        external_communication_allowed=False,
    )

    verdict = governance_check(action, context)

    assert verdict.governance_visibility_level == GovernanceVisibilityLevel.PUBLIC_FILTERED

    payload = {
        "internal": {
            "secret": "raw internal data"
        }
    }

    try:
        apply_visibility_scope(payload, verdict)
    except VisibilityFilterError:
        assert True
    else:
        assert False


def test_public_visibility_allows_only_public_payload():

    action = ProposedAction(
        action_id="inv_9",
        action_type="external_ai_action",
        requires_external_communication=True,
        external_target_type=ExternalTargetType.EXTERNAL_AI,
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        external_communication_allowed=False,
    )

    verdict = governance_check(action, context)

    payload = {
        "internal": {
            "secret": "raw internal data"
        },
        "public": {
            "safe_summary": "public-safe content"
        },
    }

    filtered = apply_visibility_scope(payload, verdict)

    assert filtered == {
        "safe_summary": "public-safe content"
    }