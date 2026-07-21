# runtime/governance_client.py

from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.schemas import (
    GovernanceDecisionStatus,
    GovernanceTargetAudience,
    GovernanceVerdictSnapshot,
    GovernanceVisibilityLevel,
)


def snapshot_from_governance_verdict(verdict: Any) -> GovernanceVerdictSnapshot:
    """
    Converts Governance MVP v4.1 verdict object/dict into Runtime read-only snapshot.

    Runtime MUST NOT mutate or reinterpret this snapshot.
    """

    if hasattr(verdict, "model_dump"):
        data: Dict[str, Any] = verdict.model_dump()
    elif isinstance(verdict, dict):
        data = verdict
    else:
        raise TypeError("Unsupported governance verdict type")

    return GovernanceVerdictSnapshot(
        governance_decision_status=GovernanceDecisionStatus(
            data["governance_decision_status"]
        ),
        governance_visibility_level=GovernanceVisibilityLevel(
            data["governance_visibility_level"]
        ),
        governance_target_audience=GovernanceTargetAudience(
            data["governance_target_audience"]
        ),
        governance_confirmation_required=bool(
            data.get("governance_confirmation_required", False)
        ),

        allowed_action_scopes=list(
            data.get("governance_allowed_action_scopes", [])
        ),
        blocked_action_scopes=list(
            data.get("governance_blocked_action_scopes", [])
        ),
        restrictions=list(
            data.get("governance_restrictions", [])
        ),
        reason_codes=list(
            data.get("governance_reason_codes", [])
        ),

        external_targets=list(
            data.get("governance_allowed_external_targets", [])
        ),
        memory_targets=list(
            data.get("governance_allowed_memory_targets", [])
        ),

        trace_id=data.get("governance_trace_id"),

        policy_sources=list(
            data.get("governance_policy_sources", [])
        ),

        policy_versions={
            "versions": data.get("governance_policy_versions", [])
        },
    )


class GovernanceClient:
    """
    Runtime-side adapter for Governance.

    Runtime asks Governance for a verdict.
    Runtime stores the snapshot.
    Runtime obeys the snapshot.
    Runtime never changes the verdict.
    """

    def __init__(self, governance_service: Optional[Any] = None) -> None:
        self.governance_service = governance_service

    def get_verdict(self, action_payload: Dict[str, Any]) -> GovernanceVerdictSnapshot:
        if self.governance_service is None:
            return GovernanceVerdictSnapshot(
                governance_decision_status=GovernanceDecisionStatus.NOT_ENOUGH_DATA,
                governance_visibility_level=GovernanceVisibilityLevel.INTERNAL_ONLY,
                governance_target_audience=GovernanceTargetAudience.INTERNAL_RAY,
                governance_confirmation_required=True,
                restrictions=["governance_service_missing"],
                reason_codes=["GOVERNANCE_SERVICE_MISSING"],
            )

        verdict = self.governance_service.check(action_payload)
        return snapshot_from_governance_verdict(verdict)