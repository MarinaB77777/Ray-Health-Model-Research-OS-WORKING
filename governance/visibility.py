from copy import deepcopy
from typing import Any, Dict

from .schemas import (
    GovernanceVerdict,
    GovernanceVisibilityLevel,
    GovernanceSanitizerStatus,
)


class VisibilityFilterError(ValueError):
    pass


FORBIDDEN_EXTERNAL_KEYS = {
    "api_key",
    "password",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "raw_answers",
    "raw_data",
    "raw_sensor_stream",
    "inner_core",
    "inner_core_payload",
    "chain_of_thought",
    "internal_reasoning",
    "system_prompt",
    "participant_id",
    "subject_link_id",
    "email",
    "phone",
    "address",
}


def sanitize_external_payload(
    payload: Dict[str, Any],
) -> tuple[Dict[str, Any], list[str]]:
    """Remove structurally forbidden fields from a prepared external branch.

    This sanitizer is intentionally deterministic. It operates only on the
    already separated `public` or `external_minimal` branch; it is not a claim
    that arbitrary free text has been de-identified.
    """

    removed: list[str] = []

    def clean(value: Any, path: str) -> Any:
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                normalized = str(key).strip().lower()
                child_path = f"{path}.{key}" if path else str(key)
                if normalized in FORBIDDEN_EXTERNAL_KEYS or normalized.startswith("raw_"):
                    removed.append(child_path)
                    continue
                result[key] = clean(item, child_path)
            return result
        if isinstance(value, list):
            return [clean(item, f"{path}[{index}]") for index, item in enumerate(value)]
        if isinstance(value, tuple):
            return [clean(item, f"{path}[{index}]") for index, item in enumerate(value)]
        return deepcopy(value)

    sanitized = clean(payload, "")
    if payload and not sanitized:
        raise VisibilityFilterError("sanitizer removed the entire external payload")
    return sanitized, sorted(removed)


def apply_visibility_scope(
    payload: Dict[str, Any],
    verdict: GovernanceVerdict,
) -> Dict[str, Any]:

    """
    Runtime-side deterministic filtering.

    Governance decides:
    - visibility level
    - restrictions
    - allowed scopes

    Runtime:
    - does NOT invent filtering rules
    - does NOT reinterpret governance
    - only applies governance decision
    """

    visibility = verdict.governance_visibility_level

    # ==========================================
    # INTERNAL ONLY
    # ==========================================

    if visibility == GovernanceVisibilityLevel.INTERNAL_ONLY:

        return payload

    # ==========================================
    # TRUSTED HUMAN
    # ==========================================

    if visibility == GovernanceVisibilityLevel.TRUSTED_HUMAN:

        trusted_payload = payload.get(
            "trusted_human"
        )

        if trusted_payload is None:

            raise VisibilityFilterError(
                "trusted_human payload missing"
            )

        return trusted_payload

    # ==========================================
    # HUMAN SAFE
    # ==========================================

    if visibility == GovernanceVisibilityLevel.HUMAN_SAFE:

        human_payload = payload.get(
            "human_safe"
        )

        if human_payload is None:

            raise VisibilityFilterError(
                "human_safe payload missing"
            )

        return human_payload

    # ==========================================
    # PUBLIC FILTERED
    # ==========================================

    if visibility == GovernanceVisibilityLevel.PUBLIC_FILTERED:

        public_payload = payload.get(
            "public"
        )

        if public_payload is None:

            raise VisibilityFilterError(
                "public payload missing"
            )

        if not verdict.governance_sanitizer_required:
            raise VisibilityFilterError("public filtering requires sanitizer authorization")
        try:
            sanitized, removed = sanitize_external_payload(public_payload)
        except Exception:
            verdict.governance_sanitizer_status = GovernanceSanitizerStatus.FAILED
            raise
        verdict.governance_sanitizer_status = GovernanceSanitizerStatus.APPLIED
        verdict.governance_sanitizer_removed_fields = removed
        return sanitized

    # ==========================================
    # EXTERNAL MINIMAL
    # ==========================================

    if visibility == GovernanceVisibilityLevel.EXTERNAL_MINIMAL:

        external_payload = payload.get(
            "external_minimal"
        )

        if external_payload is None:

            raise VisibilityFilterError(
                "external_minimal payload missing"
            )

        if not verdict.governance_sanitizer_required:
            raise VisibilityFilterError("external minimal filtering requires sanitizer authorization")
        try:
            sanitized, removed = sanitize_external_payload(external_payload)
        except Exception:
            verdict.governance_sanitizer_status = GovernanceSanitizerStatus.FAILED
            raise
        verdict.governance_sanitizer_status = GovernanceSanitizerStatus.APPLIED
        verdict.governance_sanitizer_removed_fields = removed
        return sanitized

    raise VisibilityFilterError(
        f"unsupported visibility level: {visibility}"
    )
