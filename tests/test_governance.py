from governance.schemas import (
    ProposedAction,
    GovernanceContext,
    GovernanceDecisionStatus,
    GovernanceVisibilityLevel,
    GovernanceTargetAudience,
    TrustLevel,
    ReversibilityLevel,
    ExternalTargetType,
    EmergencyType,
    SensitiveDomainRule,
)

from governance.rules import governance_check
from governance.service import GovernanceService

from governance.visibility import (
    apply_visibility_scope,
    VisibilityFilterError,
)


# =====================================================
# HUMAN PROHIBITION
# =====================================================

def test_human_prohibition_blocks_everything():

    action = ProposedAction(
        action_id="a1",
        action_type="send_message",
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        human_prohibition_active=True,
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_decision_status
        == GovernanceDecisionStatus.BLOCKED
    )

    assert (
        "full_action"
        in verdict.governance_blocked_action_scopes
    )


# =====================================================
# UNKNOWN DOMAIN
# =====================================================

def test_unknown_domain_returns_not_enough_data():

    action = ProposedAction(
        action_id="a2",
        action_type="modify_schedule",
        affected_sensitive_domains=[
            "career_reputation"
        ],
    )

    context = GovernanceContext(
        trust_level=TrustLevel.EXPANDED,
        sensitive_domain_config={},
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_decision_status
        == GovernanceDecisionStatus.NOT_ENOUGH_DATA
    )


# =====================================================
# PROTECTED DOMAIN
# =====================================================

def test_protected_domain_requires_confirmation():

    action = ProposedAction(
        action_id="a3",
        action_type="send_external_message",
        affected_sensitive_domains=[
            "privacy_of_personal_data"
        ],
    )

    context = GovernanceContext(

        trust_level=TrustLevel.DEEP,

        sensitive_domain_config={

            "privacy_of_personal_data":

                SensitiveDomainRule(
                    domain_id=(
                        "privacy_of_personal_data"
                    ),
                    protected=True,
                )
        },
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_confirmation_required
        is True
    )


# =====================================================
# IRREVERSIBLE ACTION
# =====================================================

def test_irreversible_action_requires_confirmation():

    action = ProposedAction(
        action_id="a4",
        action_type="delete_memory",
        reversibility_level=(
            ReversibilityLevel.IRREVERSIBLE
        ),
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_confirmation_required
        is True
    )


# =====================================================
# INNER CORE / PROTECTED MEMORY
# =====================================================

def test_inner_core_write_is_blocked():

    action = ProposedAction(
        action_id="a5",
        action_type="write_memory",
        requires_memory_write=True,
        memory_target="inner_core",
    )

    context = GovernanceContext(
        trust_level=TrustLevel.DEEP,
        memory_write_allowed=True,
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_decision_status
        == GovernanceDecisionStatus.BLOCKED
    )


def test_governance_service_blocks_heart_of_ray_as_memory():
    verdict = GovernanceService().check(
        ProposedAction(
            action_id="heart-ray-write",
            action_type="write_memory",
            requires_memory_write=True,
            memory_class="heart_of_ray",
        ),
        GovernanceContext(
            trust_level=TrustLevel.DEEP,
            memory_write_allowed=True,
        ),
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert "HEART_IS_NOT_MEMORY" in verdict.governance_reason_codes
    assert "heart_of_ray" in verdict.governance_blocked_memory_targets


def test_governance_service_blocks_heart_of_human_as_memory():
    verdict = GovernanceService().check(
        ProposedAction(
            action_id="heart-human-write",
            action_type="write_memory",
            requires_memory_write=True,
            memory_class="heart_of_human",
        ),
        GovernanceContext(
            trust_level=TrustLevel.DEEP,
            memory_write_allowed=True,
        ),
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert "HEART_IS_NOT_MEMORY" in verdict.governance_reason_codes


def test_governance_service_blocks_raw_self_health_authority_write():
    verdict = GovernanceService().check(
        ProposedAction(
            action_id="raw-self-health-write",
            action_type="write_memory",
            requires_memory_write=True,
            memory_class="ray_self_health_authority_raw",
        ),
        GovernanceContext(
            trust_level=TrustLevel.DEEP,
            memory_write_allowed=True,
        ),
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert "PROTECTED_MEMORY_WRITE_FORBIDDEN" in verdict.governance_reason_codes


def test_self_health_memory_requires_specialized_pathway():
    verdict = GovernanceService().check(
        ProposedAction(
            action_id="self-health-memory-write",
            action_type="write_memory",
            requires_memory_write=True,
            memory_class="ray_self_health_memory",
        ),
        GovernanceContext(
            trust_level=TrustLevel.DEEP,
            memory_write_allowed=True,
        ),
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED
    assert (
        "SELF_HEALTH_SPECIALIZED_PATH_REQUIRED"
        in verdict.governance_reason_codes
    )


def test_specialized_self_health_memory_path_reaches_normal_governance():
    verdict = GovernanceService().check(
        ProposedAction(
            action_id="self-health-specialized-write",
            action_type="write_memory",
            requires_memory_write=True,
            memory_class="ray_self_health_memory",
            specialized_memory_pathway=True,
        ),
        GovernanceContext(
            trust_level=TrustLevel.DEEP,
            memory_write_allowed=True,
        ),
    )

    assert verdict.governance_decision_status == GovernanceDecisionStatus.ALLOWED


# =====================================================
# PUBLIC FILTER REQUIRED
# =====================================================

def test_external_ai_requires_public_filter():

    action = ProposedAction(
        action_id="a6",
        action_type="send_external_ai_request",

        requires_external_communication=True,

        external_target_type=(
            ExternalTargetType.EXTERNAL_AI
        ),

        affected_sensitive_domains=[
            "privacy_of_personal_data"
        ],
    )

    context = GovernanceContext(

        trust_level=TrustLevel.DEEP,

        sensitive_domain_config={

            "privacy_of_personal_data":

                SensitiveDomainRule(
                    domain_id=(
                        "privacy_of_personal_data"
                    ),

                    external_ai_allowed=False,
                )
        },
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_visibility_level
        == GovernanceVisibilityLevel.PUBLIC_FILTERED
    )

    assert (
        verdict.governance_sanitizer_required
        is True
    )


# =====================================================
# FACTUAL EMERGENCY
# =====================================================

def test_factual_emergency_is_restricted():

    action = ProposedAction(
        action_id="a7",
        action_type="contact_emergency_contact",

        requires_external_communication=True,

        external_target_type=(
            ExternalTargetType.EMERGENCY_CONTACT
        ),
    )

    context = GovernanceContext(

        trust_level=TrustLevel.BASIC,

        emergency_type=(
            EmergencyType.FACTUAL
        ),

        factual_emergency_policy_allowed=True,
    )

    verdict = governance_check(
        action=action,
        context=context,
    )

    assert (
        verdict.governance_decision_status
        == GovernanceDecisionStatus.RESTRICTED
    )


# =====================================================
# VISIBILITY FILTER
# =====================================================

def test_visibility_filter_requires_public_payload():

    verdict = governance_check(

        action=ProposedAction(
            action_id="a8",
            action_type="external_message",
        ),

        context=GovernanceContext(
            trust_level=TrustLevel.DEEP,
        ),
    )

    verdict.governance_visibility_level = (
        GovernanceVisibilityLevel.PUBLIC_FILTERED
    )

    payload = {
        "internal": "secret"
    }

    try:

        apply_visibility_scope(
            payload=payload,
            verdict=verdict,
        )

    except VisibilityFilterError:

        assert True

    else:

        assert False
