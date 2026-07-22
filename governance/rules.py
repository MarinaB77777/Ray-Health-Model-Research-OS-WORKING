# governance/rules.py

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from .schemas import (
    ProposedAction,
    GovernanceContext,
    GovernanceVerdict,
    GovernanceDecisionStatus,
    GovernanceVisibilityLevel,
    GovernanceTargetAudience,
    TrustLevel,
    ReversibilityLevel,
    ExternalTargetType,
    EmergencyType,
    DomainImportanceLevel,
    GovernancePolicyTemporalStatus,
    GovernanceSanitizerStatus,
    HarmSeverity,
)

from .reason_codes import ReasonCodes as R


DECISION_PRIORITY = {
    GovernanceDecisionStatus.BLOCKED: 4,
    GovernanceDecisionStatus.NOT_ENOUGH_DATA: 3,
    GovernanceDecisionStatus.RESTRICTED: 2,
    GovernanceDecisionStatus.ALLOWED: 1,
}

VISIBILITY_PRIORITY = {
    GovernanceVisibilityLevel.INTERNAL_ONLY: 0,
    GovernanceVisibilityLevel.TRUSTED_HUMAN: 1,
    GovernanceVisibilityLevel.HUMAN_SAFE: 2,
    GovernanceVisibilityLevel.PUBLIC_FILTERED: 3,
    GovernanceVisibilityLevel.EXTERNAL_MINIMAL: 4,
}

HARM_PRIORITY = {
    HarmSeverity.NONE: 0,
    HarmSeverity.MINIMAL: 1,
    HarmSeverity.MODERATE: 2,
    HarmSeverity.SERIOUS: 3,
    HarmSeverity.CRITICAL: 4,
}


@dataclass
class GovernanceFinding:

    decision_status: GovernanceDecisionStatus

    reason_codes: list[str]

    visibility_level: GovernanceVisibilityLevel = (
        GovernanceVisibilityLevel.INTERNAL_ONLY
    )

    target_audience: GovernanceTargetAudience = (
        GovernanceTargetAudience.INTERNAL_RAY
    )

    confirmation_required: bool = False

    allowed_action_scopes: list[str] = field(default_factory=list)
    blocked_action_scopes: list[str] = field(default_factory=list)

    allowed_external_targets: list[str] = field(default_factory=list)
    blocked_external_targets: list[str] = field(default_factory=list)

    allowed_memory_targets: list[str] = field(default_factory=list)
    blocked_memory_targets: list[str] = field(default_factory=list)

    restrictions: list[str] = field(default_factory=list)

    policy_source: str = ""
    policy_version: str = ""

    rule_hit: str = ""


def detect_scope_conflicts(
    allowed: set[str],
    blocked: set[str],
    conflict_name: str,
) -> list[str]:

    conflicts = allowed.intersection(blocked)

    return [
        f"{conflict_name}:{item}"
        for item in conflicts
    ]


def evaluate_policy_temporal_status(
    policy_versions_by_source: dict[str, set[str]],
    context: GovernanceContext,
) -> tuple[GovernancePolicyTemporalStatus, list[str], list[str]]:
    if not policy_versions_by_source:
        return GovernancePolicyTemporalStatus.NOT_APPLICABLE, [], []
    evaluated_at = context.evaluation_time or datetime.now(UTC)
    if evaluated_at.tzinfo is None:
        return (
            GovernancePolicyTemporalStatus.MISSING,
            ["evaluation_time:timezone_required"],
            [R.NOT_ENOUGH_GOVERNANCE_DATA],
        )
    statuses = []
    details = []
    reasons = []
    for source, expected_versions in sorted(policy_versions_by_source.items()):
        validity = context.policy_temporal_validity.get(source)
        if validity is None:
            statuses.append(GovernancePolicyTemporalStatus.MISSING)
            details.append(f"{source}:validity_missing")
            reasons.extend([R.POLICY_SOURCE_UNKNOWN, R.NOT_ENOUGH_GOVERNANCE_DATA])
            continue
        if validity.valid_from.tzinfo is None or (
            validity.valid_until is not None and validity.valid_until.tzinfo is None
        ):
            statuses.append(GovernancePolicyTemporalStatus.MISSING)
            details.append(f"{source}:timezone_required")
            reasons.append(R.NOT_ENOUGH_GOVERNANCE_DATA)
            continue
        if validity.policy_version not in expected_versions:
            statuses.append(GovernancePolicyTemporalStatus.VERSION_MISMATCH)
            details.append(f"{source}:version_mismatch:{validity.policy_version}")
            reasons.append(R.POLICY_VERSION_MISSING)
            continue
        if evaluated_at < validity.valid_from:
            statuses.append(GovernancePolicyTemporalStatus.NOT_YET_VALID)
            details.append(f"{source}:not_yet_valid")
            reasons.append(R.POLICY_NOT_REVALIDATED)
            continue
        if validity.valid_until is not None and evaluated_at > validity.valid_until:
            statuses.append(GovernancePolicyTemporalStatus.EXPIRED)
            details.append(f"{source}:expired")
            reasons.append(R.POLICY_EXPIRED)
            continue
        if validity.revalidation_due_at is not None and (
            evaluated_at > validity.revalidation_due_at
        ):
            statuses.append(GovernancePolicyTemporalStatus.REVALIDATION_OVERDUE)
            details.append(f"{source}:revalidation_overdue")
            reasons.append(R.POLICY_NOT_REVALIDATED)
            continue
        statuses.append(GovernancePolicyTemporalStatus.VALID)
        details.append(f"{source}:valid:{validity.policy_version}")
    priority = {
        GovernancePolicyTemporalStatus.MISSING: 6,
        GovernancePolicyTemporalStatus.VERSION_MISMATCH: 5,
        GovernancePolicyTemporalStatus.EXPIRED: 4,
        GovernancePolicyTemporalStatus.REVALIDATION_OVERDUE: 3,
        GovernancePolicyTemporalStatus.NOT_YET_VALID: 2,
        GovernancePolicyTemporalStatus.VALID: 1,
    }
    final = max(statuses, key=lambda item: priority[item])
    return final, details, sorted(set(reasons))


def build_verdict(
    action: ProposedAction,
    findings: list[GovernanceFinding],
    context: GovernanceContext,
) -> GovernanceVerdict:

    if not findings:
        return GovernanceVerdict(
            action_id=action.action_id,

            governance_decision_status=(
                GovernanceDecisionStatus.ALLOWED
            ),

            governance_visibility_level=(
                GovernanceVisibilityLevel.INTERNAL_ONLY
            ),

            governance_target_audience=(
                GovernanceTargetAudience.INTERNAL_RAY
            ),

            governance_reason_codes=[
                R.ACTION_ALLOWED_BY_POLICY
            ],

            governance_allowed_action_scopes=[
                "full_action"
            ],

            governance_trace_id=str(uuid4()),
            governance_sanitizer_status=(
                GovernanceSanitizerStatus.NOT_REQUIRED
            ),
            governance_policy_temporal_status=(
                GovernancePolicyTemporalStatus.NOT_APPLICABLE
            ),
        )

    final_decision_status = max(
        findings,
        key=lambda f: DECISION_PRIORITY[f.decision_status]
    ).decision_status

    visibility_level = max(
        (finding.visibility_level for finding in findings),
        key=lambda item: VISIBILITY_PRIORITY[item],
    )

    target_audience = GovernanceTargetAudience.INTERNAL_RAY
    for finding in findings:
        if finding.target_audience != GovernanceTargetAudience.INTERNAL_RAY:
            target_audience = finding.target_audience

    reason_codes = set()
    restrictions = set()

    allowed_action_scopes = set()
    blocked_action_scopes = set()

    allowed_external_targets = set()
    blocked_external_targets = set()

    allowed_memory_targets = set()
    blocked_memory_targets = set()

    policy_sources = set()
    policy_versions = set()
    policy_versions_by_source: dict[str, set[str]] = {}

    rule_hits = set()

    confirmation_required = False

    for finding in findings:

        reason_codes.update(finding.reason_codes)

        restrictions.update(finding.restrictions)

        allowed_action_scopes.update(
            finding.allowed_action_scopes
        )

        blocked_action_scopes.update(
            finding.blocked_action_scopes
        )

        allowed_external_targets.update(
            finding.allowed_external_targets
        )

        blocked_external_targets.update(
            finding.blocked_external_targets
        )

        allowed_memory_targets.update(
            finding.allowed_memory_targets
        )

        blocked_memory_targets.update(
            finding.blocked_memory_targets
        )

        if finding.policy_source:
            policy_sources.add(finding.policy_source)
            policy_versions_by_source.setdefault(
                finding.policy_source,
                set(),
            )

        if finding.policy_version:
            policy_versions.add(finding.policy_version)
            if finding.policy_source:
                policy_versions_by_source[finding.policy_source].add(
                    finding.policy_version
                )

        if finding.rule_hit:
            rule_hits.add(finding.rule_hit)

        confirmation_required = (
            confirmation_required
            or finding.confirmation_required
        )

    scope_conflicts = []

    scope_conflicts.extend(
        detect_scope_conflicts(
            allowed_action_scopes,
            blocked_action_scopes,
            "action_scope_conflict",
        )
    )

    scope_conflicts.extend(
        detect_scope_conflicts(
            allowed_external_targets,
            blocked_external_targets,
            "external_target_conflict",
        )
    )

    scope_conflicts.extend(
        detect_scope_conflicts(
            allowed_memory_targets,
            blocked_memory_targets,
            "memory_target_conflict",
        )
    )

    if scope_conflicts:
        reason_codes.add(
            R.GOVERNANCE_SCOPE_CONFLICT_DETECTED
        )

        final_decision_status = GovernanceDecisionStatus.BLOCKED
        restrictions.add("unresolved_governance_scope_conflict")
        allowed_action_scopes.clear()
        allowed_external_targets.clear()
        allowed_memory_targets.clear()
        blocked_action_scopes.add("full_action")

    temporal_status, temporal_details, temporal_reasons = (
        evaluate_policy_temporal_status(
            policy_versions_by_source,
            context,
        )
    )
    temporal_enforcement_required = (
        context.temporal_policy_enforcement
        or action.requires_external_communication
        or action.external_target_type != ExternalTargetType.NONE
        or action.requires_autonomy
    )
    if temporal_enforcement_required and temporal_status not in {
        GovernancePolicyTemporalStatus.VALID,
        GovernancePolicyTemporalStatus.NOT_APPLICABLE,
    }:
        reason_codes.update(temporal_reasons)
        if final_decision_status != GovernanceDecisionStatus.BLOCKED:
            final_decision_status = GovernanceDecisionStatus.NOT_ENOUGH_DATA
        restrictions.add("policy_temporal_validation_failed")
        allowed_action_scopes.clear()
        allowed_external_targets.clear()
        allowed_memory_targets.clear()
        blocked_action_scopes.add("full_action")

    return GovernanceVerdict(
        action_id=action.action_id,

        governance_decision_status=(
            final_decision_status
        ),

        governance_visibility_level=(
            visibility_level
        ),

        governance_target_audience=(
            target_audience
        ),

        governance_confirmation_required=(
            confirmation_required
        ),

        governance_reason_codes=(
            sorted(reason_codes)
        ),

        governance_allowed_action_scopes=(
            sorted(allowed_action_scopes)
        ),

        governance_blocked_action_scopes=(
            sorted(blocked_action_scopes)
        ),

        governance_allowed_external_targets=(
            sorted(allowed_external_targets)
        ),

        governance_blocked_external_targets=(
            sorted(blocked_external_targets)
        ),

        governance_allowed_memory_targets=(
            sorted(allowed_memory_targets)
        ),

        governance_blocked_memory_targets=(
            sorted(blocked_memory_targets)
        ),

        governance_restrictions=(
            sorted(restrictions)
        ),

        governance_policy_sources=(
            sorted(policy_sources)
        ),

        governance_policy_versions=(
            sorted(policy_versions)
        ),

        governance_trace_id=str(uuid4()),

        governance_rule_hits=(
            sorted(rule_hits)
        ),

        governance_sanitizer_required=(
            visibility_level in {
                GovernanceVisibilityLevel.PUBLIC_FILTERED,
                GovernanceVisibilityLevel.EXTERNAL_MINIMAL,
            }
        ),

        governance_sanitizer_status=(
            GovernanceSanitizerStatus.REQUIRED_PENDING
            if visibility_level in {
                GovernanceVisibilityLevel.PUBLIC_FILTERED,
                GovernanceVisibilityLevel.EXTERNAL_MINIMAL,
            }
            else GovernanceSanitizerStatus.NOT_REQUIRED
        ),

        governance_policy_temporal_status=(
            temporal_status
        ),

        governance_policy_temporal_details=temporal_details,

        governance_scope_conflicts=(
            sorted(scope_conflicts)
        ),
    )
def collect_findings(
    action: ProposedAction,
    context: GovernanceContext,
) -> list[GovernanceFinding]:

    findings: list[GovernanceFinding] = []

    # ==========================================
    # HUMAN PROHIBITION
    # ==========================================

    if context.human_prohibition_active:

        findings.append(
            GovernanceFinding(

                decision_status=(
                    GovernanceDecisionStatus.BLOCKED
                ),

                reason_codes=[
                    R.HUMAN_PROHIBITION_ACTIVE
                ],

                blocked_action_scopes=[
                    "full_action"
                ],

                restrictions=[
                    "human_prohibition_hard_stop"
                ],

                policy_source="human_override",

                policy_version="human_override_v1",

                rule_hit="human_prohibition_active",
            )
        )

        return findings

    # ==========================================
    # EMERGENCY
    # ==========================================

    if context.emergency_type == EmergencyType.PROJECTED:

        findings.append(
            GovernanceFinding(

                decision_status=(
                    GovernanceDecisionStatus.RESTRICTED
                ),

                reason_codes=[
                    R.PROJECTED_EMERGENCY_NOT_AUTHORIZATION,
                    R.HUMAN_CONFIRMATION_REQUIRED,
                ],

                confirmation_required=True,

                restrictions=[
                    "projected_emergency_cannot_authorize"
                ],

                policy_source="emergency_policy",

                policy_version=(
                    context.emergency_policy_version
                    or "unknown"
                ),

                rule_hit="projected_emergency_requires_confirmation",
            )
        )

    if context.emergency_type == EmergencyType.FACTUAL:

        if context.factual_emergency_policy_allowed:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.FACTUAL_EMERGENCY_POLICY_ALLOWED,
                        R.EMERGENCY_SCOPE_RESTRICTED,
                    ],

                    allowed_action_scopes=[
                        "preapproved_emergency_scope"
                    ],

                    blocked_action_scopes=[
                        "outside_emergency_scope"
                    ],

                    restrictions=[
                        "emergency_policy_scope_only"
                    ],

                    policy_source="emergency_policy",

                    policy_version=(
                        context.emergency_policy_version
                        or "unknown"
                    ),

                    rule_hit="factual_emergency_scope",
                )
            )

        else:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.FACTUAL_EMERGENCY_POLICY_NOT_ALLOWED,
                        R.HUMAN_CONFIRMATION_REQUIRED,
                    ],

                    confirmation_required=True,

                    restrictions=[
                        "no_preapproved_emergency_policy"
                    ],

                    policy_source="emergency_policy",

                    policy_version=(
                        context.emergency_policy_version
                        or "unknown"
                    ),

                    rule_hit="factual_emergency_without_policy",
                )
            )

    # ==========================================
    # UNKNOWN SENSITIVE DOMAINS
    # ==========================================

    if action.unknown_sensitive_domains_present:

        findings.append(
            GovernanceFinding(

                decision_status=(
                    GovernanceDecisionStatus.NOT_ENOUGH_DATA
                ),

                reason_codes=[
                    R.SENSITIVE_DOMAIN_UNKNOWN,
                    R.NOT_ENOUGH_GOVERNANCE_DATA,
                ],

                confirmation_required=True,

                restrictions=[
                    "unknown_sensitive_domains"
                ],

                policy_source="sensitive_domain_policy",

                policy_version="unknown",

                rule_hit="unknown_sensitive_domains_present",
            )
        )

    # ==========================================
    # DOMAIN RULES
    # ==========================================

    for domain_id in action.affected_sensitive_domains:

        domain_rule = (
            context.sensitive_domain_config.get(
                domain_id
            )
        )

        if domain_rule is None:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.NOT_ENOUGH_DATA
                    ),

                    reason_codes=[
                        R.SENSITIVE_DOMAIN_UNKNOWN,
                        R.NOT_ENOUGH_GOVERNANCE_DATA,
                    ],

                    confirmation_required=True,

                    restrictions=[
                        f"missing_domain_config:{domain_id}"
                    ],

                    policy_source="sensitive_domain_policy",

                    policy_version="missing",

                    rule_hit=f"missing_domain_config:{domain_id}",
                )
            )

            continue

        if domain_rule.protected:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.SENSITIVE_DOMAIN_PROTECTED,
                        R.HUMAN_CONFIRMATION_REQUIRED,
                    ],

                    confirmation_required=True,

                    restrictions=[
                        f"protected_domain:{domain_id}"
                    ],

                    policy_source="sensitive_domain_policy",

                    policy_version=(
                        domain_rule.policy_version
                    ),

                    rule_hit=f"protected_domain:{domain_id}",
                )
            )

        if domain_rule.requires_confirmation:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.SENSITIVE_DOMAIN_REQUIRES_CONFIRMATION,
                        R.HUMAN_CONFIRMATION_REQUIRED,
                    ],

                    confirmation_required=True,

                    restrictions=[
                        f"domain_requires_confirmation:{domain_id}"
                    ],

                    policy_source="sensitive_domain_policy",

                    policy_version=(
                        domain_rule.policy_version
                    ),

                    rule_hit=f"domain_requires_confirmation:{domain_id}",
                )
            )

        if domain_rule.importance_level in {
            DomainImportanceLevel.HIGH,
            DomainImportanceLevel.CRITICAL,
        }:
            findings.append(
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.RESTRICTED,
                    reason_codes=[
                        R.SENSITIVE_DOMAIN_REQUIRES_CONFIRMATION,
                        R.HUMAN_CONFIRMATION_REQUIRED,
                    ],
                    confirmation_required=True,
                    restrictions=[f"high_importance_domain:{domain_id}"],
                    policy_source="sensitive_domain_policy",
                    policy_version=domain_rule.policy_version,
                    rule_hit=f"high_importance_domain:{domain_id}",
                )
            )

        harm_profile = domain_rule.acceptable_harm_profile
        if HARM_PRIORITY[action.projected_harm_severity] > HARM_PRIORITY[
            harm_profile.maximum_severity
        ]:
            findings.append(
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.BLOCKED,
                    reason_codes=[R.ACCEPTABLE_HARM_PROFILE_EXCEEDED],
                    blocked_action_scopes=["full_action"],
                    restrictions=[f"harm_threshold_exceeded:{domain_id}"],
                    policy_source="acceptable_harm_policy",
                    policy_version=domain_rule.policy_version,
                    rule_hit=f"harm_threshold_exceeded:{domain_id}",
                )
            )
        disallowed_impacts = set(action.projected_impact_categories) - set(
            harm_profile.permitted_impact_categories
        )
        if disallowed_impacts:
            findings.append(
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.BLOCKED,
                    reason_codes=[R.ACCEPTABLE_HARM_PROFILE_EXCEEDED],
                    blocked_action_scopes=["full_action"],
                    restrictions=[
                        f"impact_category_not_allowed:{domain_id}:{item}"
                        for item in sorted(disallowed_impacts)
                    ],
                    policy_source="acceptable_harm_policy",
                    policy_version=domain_rule.policy_version,
                    rule_hit=f"impact_category_not_allowed:{domain_id}",
                )
            )
        disallowed_overrides = set(action.requested_governance_overrides) - set(
            domain_rule.allowed_overrides
        )
        if disallowed_overrides:
            findings.append(
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.BLOCKED,
                    reason_codes=[R.GOVERNANCE_OVERRIDE_NOT_ALLOWED],
                    blocked_action_scopes=["full_action"],
                    restrictions=[
                        f"override_not_allowed:{domain_id}:{item}"
                        for item in sorted(disallowed_overrides)
                    ],
                    policy_source="sensitive_domain_policy",
                    policy_version=domain_rule.policy_version,
                    rule_hit=f"override_not_allowed:{domain_id}",
                )
            )

        # ==========================================
        # EXTERNAL TARGETS
        # ==========================================

        if (
            action.external_target_type
            == ExternalTargetType.EXTERNAL_AI
        ):

            if not domain_rule.external_ai_allowed:

                findings.append(
                    GovernanceFinding(

                        decision_status=(
                            GovernanceDecisionStatus.RESTRICTED
                        ),

                        reason_codes=[
                            R.EXTERNAL_AI_RESTRICTED,
                            R.PUBLIC_FILTER_REQUIRED,
                        ],

                        visibility_level=(
                            GovernanceVisibilityLevel.PUBLIC_FILTERED
                        ),

                        target_audience=(
                            GovernanceTargetAudience.EXTERNAL_AI
                        ),

                        blocked_external_targets=[
                            "external_ai_raw_internal"
                        ],

                        restrictions=[
                            "public_filter_required"
                        ],

                        policy_source="external_ai_policy",

                        policy_version=(
                            domain_rule.policy_version
                        ),

                        rule_hit=f"external_ai_restricted:{domain_id}",
                    )
                )

        if (
            action.external_target_type
            == ExternalTargetType.INTERNET
        ):

            if not domain_rule.internet_allowed:

                findings.append(
                    GovernanceFinding(

                        decision_status=(
                            GovernanceDecisionStatus.RESTRICTED
                        ),

                        reason_codes=[
                            R.INTERNET_ACCESS_RESTRICTED,
                            R.PUBLIC_FILTER_REQUIRED,
                        ],

                        visibility_level=(
                            GovernanceVisibilityLevel.PUBLIC_FILTERED
                        ),

                        target_audience=(
                            GovernanceTargetAudience.INTERNET
                        ),

                        blocked_external_targets=[
                            "internet_raw_internal"
                        ],

                        restrictions=[
                            "public_filter_required"
                        ],

                        policy_source="internet_policy",

                        policy_version=(
                            domain_rule.policy_version
                        ),

                        rule_hit=f"internet_restricted:{domain_id}",
                    )
                )
    # ==========================================
    # REVERSIBILITY
    # ==========================================

    if action.reversibility_level in {

        ReversibilityLevel.HARD_TO_REVERSE,

        ReversibilityLevel.IRREVERSIBLE,
    }:

        findings.append(
            GovernanceFinding(

                decision_status=(
                    GovernanceDecisionStatus.RESTRICTED
                ),

                reason_codes=[
                    R.LOW_REVERSIBILITY_ACTION,
                    R.IRREVERSIBLE_ACTION_REQUIRES_CONFIRMATION,
                    R.HUMAN_CONFIRMATION_REQUIRED,
                ],

                confirmation_required=True,

                restrictions=[
                    "low_reversibility_action"
                ],

                policy_source="reversibility_policy",

                policy_version="reversibility_policy_v1",

                rule_hit="irreversible_action_requires_confirmation",
            )
        )

    # ==========================================
    # AUTONOMY
    # ==========================================

    if action.requires_autonomy:

        if not context.delegated_autonomy_allowed:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.DELEGATED_AUTONOMY_NOT_ALLOWED,
                        R.HUMAN_CONFIRMATION_REQUIRED,
                    ],

                    confirmation_required=True,

                    restrictions=[
                        "delegated_autonomy_not_allowed"
                    ],

                    policy_source="autonomy_policy",

                    policy_version=(
                        context.autonomy_policy_version
                        or "unknown"
                    ),

                    rule_hit="delegated_autonomy_not_allowed",
                )
            )

        if context.trust_level == TrustLevel.BASIC:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.BASIC_TRUST_REQUIRES_CONFIRMATION
                    ],

                    confirmation_required=True,

                    restrictions=[
                        "basic_trust_requires_confirmation"
                    ],

                    policy_source="trust_policy",

                    policy_version="trust_policy_v1",

                    rule_hit="basic_trust_requires_confirmation",
                )
            )

    # ==========================================
    # MEMORY
    # ==========================================

    if action.requires_memory_write:

        if action.memory_target == "inner_core":

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.BLOCKED
                    ),

                    reason_codes=[
                        R.INNER_CORE_WRITE_FORBIDDEN
                    ],

                    blocked_memory_targets=[
                        "inner_core"
                    ],

                    restrictions=[
                        "inner_core_write_forbidden"
                    ],

                    policy_source="memory_policy",

                    policy_version="memory_policy_v1",

                    rule_hit="inner_core_write_forbidden",
                )
            )

        elif not context.memory_write_allowed:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.MEMORY_WRITE_NOT_ALLOWED
                    ],

                    blocked_memory_targets=[
                        action.memory_target or "unknown"
                    ],

                    restrictions=[
                        "memory_write_not_allowed"
                    ],

                    policy_source="memory_policy",

                    policy_version="memory_policy_v1",

                    rule_hit="memory_write_not_allowed",
                )
            )

    # ==========================================
    # EXTERNAL COMMUNICATION
    # ==========================================

    if action.requires_external_communication:

        if (
            action.external_target_type
            == ExternalTargetType.EXTERNAL_AI
            and context.external_communication_allowed
            and all(
                context.sensitive_domain_config.get(domain_id) is not None
                and context.sensitive_domain_config[domain_id].external_ai_allowed
                for domain_id in action.affected_sensitive_domains
            )
        ):
            findings.append(
                GovernanceFinding(
                    decision_status=GovernanceDecisionStatus.RESTRICTED,
                    reason_codes=[
                        R.PUBLIC_FILTER_REQUIRED,
                    ],
                    visibility_level=(
                        GovernanceVisibilityLevel.EXTERNAL_MINIMAL
                    ),
                    target_audience=(
                        GovernanceTargetAudience.EXTERNAL_AI
                    ),
                    allowed_external_targets=[
                        "external_ai_sanitized_request"
                    ],
                    blocked_external_targets=[
                        "external_ai_raw_internal"
                    ],
                    restrictions=[
                        "external_minimal_payload_only",
                        "external_response_is_not_internal_truth",
                        "external_response_memory_write_forbidden",
                    ],
                    policy_source="external_communication_policy",
                    policy_version=(
                        context.privacy_policy_version
                        or "unknown"
                    ),
                    rule_hit="external_ai_separate_outbound_channel",
                )
            )

        if not context.external_communication_allowed:

            findings.append(
                GovernanceFinding(

                    decision_status=(
                        GovernanceDecisionStatus.RESTRICTED
                    ),

                    reason_codes=[
                        R.EXTERNAL_COMMUNICATION_RESTRICTED,
                        R.PUBLIC_FILTER_REQUIRED,
                    ],

                    visibility_level=(
                        GovernanceVisibilityLevel.PUBLIC_FILTERED
                    ),

                    target_audience=(
                        GovernanceTargetAudience.EXTERNAL_PERSON
                    ),

                    blocked_external_targets=[
                        "raw_internal_external_communication"
                    ],

                    restrictions=[
                        "public_filter_required"
                    ],

                    policy_source="external_communication_policy",

                    policy_version=(
                        context.privacy_policy_version
                        or "unknown"
                    ),

                    rule_hit="external_communication_restricted",
                )
            )

    return findings


def governance_check(
    action: ProposedAction,
    context: GovernanceContext,
) -> GovernanceVerdict:

    findings = collect_findings(
        action=action,
        context=context,
    )

    return build_verdict(
        action=action,
        findings=findings,
        context=context,
    )
