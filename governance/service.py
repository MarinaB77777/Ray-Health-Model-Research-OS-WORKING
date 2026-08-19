from uuid import uuid4

from .reason_codes import ReasonCodes as R
from .schemas import (
    ProposedAction,
    GovernanceContext,
    GovernanceDecisionStatus,
    GovernanceTargetAudience,
    GovernanceVerdict,
    GovernanceVisibilityLevel,
)
from .rules import governance_check


PROTECTED_NON_MEMORY_TARGETS = frozenset(
    {
        "inner_core",
        "inner_core_raw",
        "heart_of_ray",
        "heart_of_human",
        "ray_self_health_authority_raw",
        "ray_self_health_raw",
        "ray_self_health_telemetry_raw",
    }
)
SELF_HEALTH_MEMORY_CLASS = "ray_self_health_memory"


class GovernanceService:
    """Thin Governance facade with protected-boundary preflight.

    GovernanceService:
    - receives proposed action + context;
    - rejects attempts to reinterpret protected Inner Core authorities as memory;
    - requires the specialized pathway for Ray Self-Health memory;
    - delegates ordinary policy evaluation to governance rules;
    - returns one GovernanceVerdict.

    It does NOT execute actions, modify Runtime state, contact humans, perform
    Analyst reasoning, or write memory directly.
    """

    def check(
        self,
        action: ProposedAction,
        context: GovernanceContext,
    ) -> GovernanceVerdict:
        boundary_verdict = self._protected_memory_boundary(action)
        if boundary_verdict is not None:
            return boundary_verdict

        return governance_check(
            action=action,
            context=context,
        )

    @staticmethod
    def _protected_memory_boundary(
        action: ProposedAction,
    ) -> GovernanceVerdict | None:
        if not action.requires_memory_write:
            return None

        target = action.memory_class or action.memory_target or "unknown"

        if target in PROTECTED_NON_MEMORY_TARGETS:
            reason_codes = [R.PROTECTED_MEMORY_WRITE_FORBIDDEN]
            if target in {"heart_of_ray", "heart_of_human"}:
                reason_codes.append(R.HEART_IS_NOT_MEMORY)
            if target in {"inner_core", "inner_core_raw"}:
                reason_codes.append(R.INNER_CORE_WRITE_FORBIDDEN)

            return GovernanceVerdict(
                action_id=action.action_id,
                governance_decision_status=GovernanceDecisionStatus.BLOCKED,
                governance_visibility_level=GovernanceVisibilityLevel.INTERNAL_ONLY,
                governance_target_audience=GovernanceTargetAudience.INTERNAL_RAY,
                governance_reason_codes=sorted(set(reason_codes)),
                governance_blocked_action_scopes=["full_action"],
                governance_blocked_memory_targets=[target],
                governance_restrictions=[
                    "protected_inner_core_authority_is_not_generic_memory",
                ],
                governance_policy_sources=["protected_memory_boundary"],
                governance_policy_versions=["protected_memory_boundary_v2"],
                governance_trace_id=str(uuid4()),
                governance_rule_hits=["protected_memory_boundary"],
            )

        if (
            target == SELF_HEALTH_MEMORY_CLASS
            and not action.specialized_memory_pathway
        ):
            return GovernanceVerdict(
                action_id=action.action_id,
                governance_decision_status=GovernanceDecisionStatus.BLOCKED,
                governance_visibility_level=GovernanceVisibilityLevel.INTERNAL_ONLY,
                governance_target_audience=GovernanceTargetAudience.INTERNAL_RAY,
                governance_reason_codes=[R.SELF_HEALTH_SPECIALIZED_PATH_REQUIRED],
                governance_blocked_action_scopes=["full_action"],
                governance_blocked_memory_targets=[target],
                governance_restrictions=[
                    "ray_self_health_memory_requires_specialized_pathway",
                ],
                governance_policy_sources=["ray_self_health_memory_boundary"],
                governance_policy_versions=["ray_self_health_memory_boundary_v1"],
                governance_trace_id=str(uuid4()),
                governance_rule_hits=["ray_self_health_specialized_path_required"],
            )

        return None
