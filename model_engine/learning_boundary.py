from __future__ import annotations

from typing import Any


LEARNING_NOT_EVALUATED = "not_evaluated"


def normalize_learning_governance(readiness: dict[str, Any]) -> dict[str, Any]:
    """Prevent a legacy no-op learning block from impersonating evaluation.

    The current model engine has no executable learning/promotion engine. Until a
    governed implementation exists, absence of detected patterns must remain
    UNKNOWN / NOT_EVALUATED rather than False.
    """

    normalized = dict(readiness)
    legacy = normalized.get("learning")

    if not isinstance(legacy, dict):
        legacy = {}

    explicitly_evaluated = bool(legacy.get("evaluated", False))

    if explicitly_evaluated:
        # Future implementations must still declare non-escalation boundaries.
        bounded = dict(legacy)
        bounded.setdefault("automatic_memory_promotion_allowed", False)
        bounded.setdefault("heart_mutation_allowed", False)
        bounded.setdefault("permission_mutation_allowed", False)
        bounded.setdefault("truth_authority_mutation_allowed", False)
        normalized["learning"] = bounded
        return normalized

    normalized["learning"] = {
        "evaluation_status": LEARNING_NOT_EVALUATED,
        "evaluated": False,
        "pattern_candidate_detected": None,
        "stable_candidate_detected": None,
        "calibration_update_recommended": None,
        "requires_user_confirmation": None,
        "allow_external_core_update_request": False,
        "automatic_memory_promotion_allowed": False,
        "heart_mutation_allowed": False,
        "permission_mutation_allowed": False,
        "truth_authority_mutation_allowed": False,
        "reason_codes": ["LEARNING_ENGINE_NOT_IMPLEMENTED"],
    }
    return normalized
