# runtime/visibility_adapter.py

from __future__ import annotations

from typing import Any, Dict

from runtime.schemas import (
    GovernanceDecisionStatus,
    GovernanceVerdictSnapshot,
    GovernanceVisibilityLevel,
)


class RuntimeVisibilityError(PermissionError):
    pass


def _require_payload_layer(
    payload: Dict[str, Any],
    layer_name: str,
) -> Dict[str, Any]:
    layer = payload.get(layer_name)

    if layer is None:
        raise RuntimeVisibilityError(
            f"Required visibility payload layer missing: {layer_name}"
        )

    if not isinstance(layer, dict):
        raise RuntimeVisibilityError(
            f"Visibility payload layer must be dict: {layer_name}"
        )

    return layer


def apply_runtime_visibility_scope(
    payload: Dict[str, Any],
    verdict: GovernanceVerdictSnapshot,
) -> Dict[str, Any]:
    """
    Runtime visibility adapter.

    Fail-closed:
    - no silent fallback;
    - no guessing safe payload;
    - missing required layer raises error.
    """

    if verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED:
        return {
            "blocked": True,
            "reason": "governance_blocked",
            "reason_codes": verdict.reason_codes,
        }

    visibility = verdict.governance_visibility_level

    if visibility == GovernanceVisibilityLevel.INTERNAL_ONLY:
        return {
            "visibility": visibility.value,
            "payload": payload,
        }

    if visibility == GovernanceVisibilityLevel.TRUSTED_HUMAN:
        return {
            "visibility": visibility.value,
            "payload": _require_payload_layer(payload, "trusted_human"),
        }

    if visibility == GovernanceVisibilityLevel.HUMAN_SAFE:
        return {
            "visibility": visibility.value,
            "payload": _require_payload_layer(payload, "human_safe"),
        }

    if visibility == GovernanceVisibilityLevel.PUBLIC_FILTERED:
        return {
            "visibility": visibility.value,
            "payload": _require_payload_layer(payload, "public"),
        }

    if visibility == GovernanceVisibilityLevel.EXTERNAL_MINIMAL:
        return {
            "visibility": visibility.value,
            "payload": _require_payload_layer(payload, "external_minimal"),
        }

    raise RuntimeVisibilityError(
        f"Unsupported visibility level: {visibility}"
    )


def assert_runtime_can_deliver(
    verdict: GovernanceVerdictSnapshot,
) -> None:
    """
    Raises if Runtime must not deliver the action.
    """

    if verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED:
        raise PermissionError("Governance blocked this action.")

    if verdict.governance_decision_status == GovernanceDecisionStatus.NOT_ENOUGH_DATA:
        raise PermissionError("Governance returned not_enough_data.")

    if verdict.governance_confirmation_required:
        raise PermissionError("Human confirmation required before delivery.")

