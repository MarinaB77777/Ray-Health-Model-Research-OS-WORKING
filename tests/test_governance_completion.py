from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from governance.rules import GovernanceFinding, build_verdict, governance_check
from governance.schemas import (
    AcceptableHarmProfile,
    EmergencyType,
    ExternalTargetType,
    GovernanceContext,
    GovernanceDecisionStatus,
    GovernancePolicyTemporalStatus,
    GovernanceSanitizerStatus,
    GovernanceVisibilityLevel,
    HarmSeverity,
    PolicyTemporalValidity,
    ProposedAction,
    SensitiveDomainRule,
    TrustLevel,
)
from governance.visibility import apply_visibility_scope


NOW = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)


def validity(source: str, version: str, *, expired: bool = False):
    return PolicyTemporalValidity(
        policy_source=source,
        policy_version=version,
        valid_from=NOW - timedelta(days=30),
        valid_until=(NOW - timedelta(days=1)) if expired else (NOW + timedelta(days=30)),
        last_revalidated_at=NOW - timedelta(days=1),
        revalidation_due_at=NOW + timedelta(days=7),
    )


class GovernanceCompletionTests(unittest.TestCase):
    def test_internal_allowed_action_needs_no_sanitizer_or_temporal_policy(self) -> None:
        verdict = governance_check(
            ProposedAction(action_id="action-1", action_type="internal_review"),
            GovernanceContext(trust_level=TrustLevel.BASIC),
        )
        self.assertEqual(GovernanceDecisionStatus.ALLOWED, verdict.governance_decision_status)
        self.assertEqual(
            GovernanceSanitizerStatus.NOT_REQUIRED,
            verdict.governance_sanitizer_status,
        )
        self.assertEqual(
            GovernancePolicyTemporalStatus.NOT_APPLICABLE,
            verdict.governance_policy_temporal_status,
        )

    def test_external_ai_path_checks_policy_time_and_applies_sanitizer(self) -> None:
        domain_rule = SensitiveDomainRule(
            domain_id="health_model_research",
            requires_confirmation=True,
            external_ai_allowed=False,
            policy_version="domain-policy-1",
        )
        context = GovernanceContext(
            trust_level=TrustLevel.DEEP,
            external_communication_allowed=False,
            evaluation_time=NOW,
            temporal_policy_enforcement=True,
            sensitive_domain_config={"health_model_research": domain_rule},
            policy_temporal_validity={
                "sensitive_domain_policy": validity(
                    "sensitive_domain_policy", "domain-policy-1"
                ),
                "external_ai_policy": validity(
                    "external_ai_policy", "domain-policy-1"
                ),
                "external_communication_policy": validity(
                    "external_communication_policy", "privacy_policy_v1"
                ),
            },
        )
        action = ProposedAction(
            action_id="action-2",
            action_type="external_processing",
            requires_external_communication=True,
            external_target_type=ExternalTargetType.EXTERNAL_AI,
            affected_sensitive_domains=["health_model_research"],
        )
        verdict = governance_check(action, context)
        self.assertEqual(
            GovernancePolicyTemporalStatus.VALID,
            verdict.governance_policy_temporal_status,
        )
        self.assertEqual(
            GovernanceSanitizerStatus.REQUIRED_PENDING,
            verdict.governance_sanitizer_status,
        )
        filtered = apply_visibility_scope(
            {
                "public": {
                    "summary": "bounded public input",
                    "participant_id": "must-not-leave",
                    "nested": {"raw_answers": [1, 2], "unit": "score"},
                }
            },
            verdict,
        )
        self.assertEqual(
            {"summary": "bounded public input", "nested": {"unit": "score"}},
            filtered,
        )
        self.assertEqual(
            GovernanceSanitizerStatus.APPLIED,
            verdict.governance_sanitizer_status,
        )
        self.assertEqual(
            ["nested.raw_answers", "participant_id"],
            verdict.governance_sanitizer_removed_fields,
        )

    def test_external_action_with_missing_policy_validity_is_not_executable(self) -> None:
        verdict = governance_check(
            ProposedAction(
                action_id="action-3",
                action_type="external_message",
                requires_external_communication=True,
                external_target_type=ExternalTargetType.EXTERNAL_PERSON,
            ),
            GovernanceContext(
                trust_level=TrustLevel.DEEP,
                external_communication_allowed=False,
                evaluation_time=NOW,
            ),
        )
        self.assertEqual(
            GovernanceDecisionStatus.NOT_ENOUGH_DATA,
            verdict.governance_decision_status,
        )
        self.assertEqual(
            GovernancePolicyTemporalStatus.MISSING,
            verdict.governance_policy_temporal_status,
        )
        self.assertIn("full_action", verdict.governance_blocked_action_scopes)

    def test_allowed_external_ai_still_uses_external_minimal_separate_channel(self) -> None:
        context = GovernanceContext(
            trust_level=TrustLevel.BASIC,
            external_communication_allowed=True,
            evaluation_time=NOW,
            privacy_policy_version="external-policy-1",
            policy_temporal_validity={
                "external_communication_policy": validity(
                    "external_communication_policy",
                    "external-policy-1",
                )
            },
        )
        verdict = governance_check(
            ProposedAction(
                action_id="action-external-ai-allowed",
                action_type="external_ai_information_request",
                requires_external_communication=True,
                external_target_type=ExternalTargetType.EXTERNAL_AI,
            ),
            context,
        )
        self.assertEqual(
            GovernanceDecisionStatus.RESTRICTED,
            verdict.governance_decision_status,
        )
        self.assertEqual(
            GovernanceVisibilityLevel.EXTERNAL_MINIMAL,
            verdict.governance_visibility_level,
        )
        filtered = apply_visibility_scope(
            {
                "external_minimal": {
                    "question": "safe question",
                    "participant_id": "blocked",
                }
            },
            verdict,
        )
        self.assertEqual({"question": "safe question"}, filtered)

    def test_expired_external_policy_is_reported(self) -> None:
        verdict = governance_check(
            ProposedAction(
                action_id="action-4",
                action_type="external_message",
                requires_external_communication=True,
                external_target_type=ExternalTargetType.EXTERNAL_PERSON,
            ),
            GovernanceContext(
                trust_level=TrustLevel.DEEP,
                external_communication_allowed=False,
                evaluation_time=NOW,
                policy_temporal_validity={
                    "external_communication_policy": validity(
                        "external_communication_policy",
                        "privacy_policy_v1",
                        expired=True,
                    )
                },
            ),
        )
        self.assertEqual(
            GovernancePolicyTemporalStatus.EXPIRED,
            verdict.governance_policy_temporal_status,
        )

    def test_scope_conflict_is_blocking_not_merely_restricted(self) -> None:
        action = ProposedAction(action_id="action-5", action_type="conflicted")
        verdict = build_verdict(
            action,
            [
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.ALLOWED,
                    reason_codes=["ALLOW"],
                    allowed_action_scopes=["same_scope"],
                ),
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.RESTRICTED,
                    reason_codes=["BLOCK"],
                    blocked_action_scopes=["same_scope"],
                ),
            ],
            GovernanceContext(trust_level=TrustLevel.DEEP),
        )
        self.assertEqual(GovernanceDecisionStatus.BLOCKED, verdict.governance_decision_status)
        self.assertEqual([], verdict.governance_allowed_action_scopes)
        self.assertIn("full_action", verdict.governance_blocked_action_scopes)

    def test_projected_harm_above_domain_profile_is_blocked(self) -> None:
        rule = SensitiveDomainRule(
            domain_id="health_model_research",
            requires_confirmation=False,
            acceptable_harm_profile=AcceptableHarmProfile(
                maximum_severity=HarmSeverity.MINIMAL,
                permitted_impact_categories=["temporary_inconvenience"],
            ),
        )
        verdict = governance_check(
            ProposedAction(
                action_id="action-6",
                action_type="domain_action",
                affected_sensitive_domains=["health_model_research"],
                projected_harm_severity=HarmSeverity.SERIOUS,
                projected_impact_categories=["temporary_inconvenience"],
            ),
            GovernanceContext(
                trust_level=TrustLevel.DEEP,
                sensitive_domain_config={"health_model_research": rule},
            ),
        )
        self.assertEqual(GovernanceDecisionStatus.BLOCKED, verdict.governance_decision_status)

    def test_projected_emergency_branch_builds_a_valid_verdict(self) -> None:
        verdict = governance_check(
            ProposedAction(action_id="action-7", action_type="projected_emergency"),
            GovernanceContext(
                trust_level=TrustLevel.BASIC,
                emergency_type=EmergencyType.PROJECTED,
            ),
        )
        self.assertEqual(GovernanceDecisionStatus.RESTRICTED, verdict.governance_decision_status)
        self.assertTrue(verdict.governance_confirmation_required)


if __name__ == "__main__":
    unittest.main()
