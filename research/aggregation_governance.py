from datetime import UTC, datetime


GOVERNANCE_SCOPE = "research_dataset_admission"
AGGREGATION_GOVERNANCE_VERSION = "research-aggregation-governance-1"


def _get_path(data: dict, path: list[str], default=None):
    current = data

    for key in path:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def evaluate_snapshot_dataset_admission(snapshot: dict) -> dict:
    blockers = []
    restrictions = []
    warnings = []

    if not isinstance(snapshot, dict):
        blockers.append("INVALID_SNAPSHOT_PAYLOAD")

        return {
            "governance_scope": GOVERNANCE_SCOPE,
            "governance_version": AGGREGATION_GOVERNANCE_VERSION,
            "evaluated_at": datetime.now(UTC).isoformat(),
            "evaluated_by": "research.aggregation_governance",
            "admission_allowed": False,
            "admission_status": "blocked",
            "allowed_scope": "none",
            "blockers": blockers,
            "restrictions": restrictions,
            "warnings": warnings,
            "aggregation_performed": False,
            "longitudinal_admission_allowed": False,
            "participant_comparison_allowed": False,
            "dataset_use_scope": "none",
            "admission_decision_is_not_research_correctness": True,
            "admission_allowed_is_not_aggregation": True,
            "restricted_admission_is_not_longitudinal_permission": True,
        }

    snapshot_mode = snapshot.get("snapshot_mode")
    snapshot_scope = snapshot.get("snapshot_scope")

    snapshot_status = _get_path(
        snapshot,
        ["snapshot_policy_status", "snapshot_status"],
        "unknown",
    )

    usable_preliminary = _get_path(
        snapshot,
        [
            "snapshot_policy_status",
            "usable_for_research_preliminary",
        ],
        False,
    )

    exclusion_status = _get_path(
        snapshot,
        ["snapshot_policy_status", "exclusion_status"],
        "unknown",
    )

    consent_status = _get_path(
        snapshot,
        ["snapshot_policy_status", "consent_status"],
        "unknown",
    )

    retention_status = _get_path(
        snapshot,
        ["snapshot_policy_status", "retention_status"],
        "unknown",
    )

    policy_restricted = _get_path(
        snapshot,
        ["snapshot_policy_status", "policy_restricted"],
        "unknown",
    )

    invalidated = _get_path(
        snapshot,
        ["source_session", "invalidated"],
        False,
    )

    pseudonymized = _get_path(
        snapshot,
        ["participant_reference", "pseudonymized"],
        False,
    )

    research_identity_risk = _get_path(
        snapshot,
        ["participant_reference", "research_identity_risk"],
        "unknown",
    )

    payload_safety_status = _get_path(
        snapshot,
        ["payload_safety", "payload_safety_status"],
        "unknown",
    )

    acquisition_deep_sanitized = _get_path(
        snapshot,
        ["payload_safety", "acquisition_payload_deep_sanitized"],
        False,
    )

    next_questions_deep_sanitized = _get_path(
        snapshot,
        ["payload_safety", "next_questions_deep_sanitized"],
        False,
    )

    if snapshot_mode != "research":
        blockers.append("INVALID_SNAPSHOT_MODE")

    if snapshot_scope != "bounded_research_snapshot":
        blockers.append("INVALID_SNAPSHOT_SCOPE")

    if invalidated or snapshot_status == "invalidated":
        blockers.append("SNAPSHOT_INVALIDATED")

    if usable_preliminary is not True:
        blockers.append("SNAPSHOT_NOT_USABLE_PRELIMINARY")

    if exclusion_status == "excluded_invalidated":
        blockers.append("EXCLUDED_INVALIDATED")

    if exclusion_status == "missing_public_output":
        blockers.append("MISSING_PUBLIC_OUTPUT")

    if exclusion_status == "blocked_source_status":
        blockers.append("BLOCKED_SOURCE_STATUS")

    if consent_status != "granted":
        blockers.append("CONSENT_NOT_GRANTED")

    if retention_status == "active":
        pass
    elif retention_status == "expired":
        blockers.append("RETENTION_EXPIRED")
    elif retention_status == "not_evaluated":
        blockers.append("RETENTION_NOT_EVALUATED")
    elif retention_status == "unknown":
        blockers.append("RETENTION_UNKNOWN")
    else:
        blockers.append("RETENTION_NOT_ACTIVE")

    if policy_restricted not in [False, "not_restricted"]:
        blockers.append("POLICY_RESTRICTED_OR_NOT_EVALUATED")

    if pseudonymized is not True:
        restrictions.append("NOT_PSEUDONYMIZED")

        if research_identity_risk == "direct_pilot_id_used_mvp":
            restrictions.append("DIRECT_PILOT_ID_USED_MVP")

    if payload_safety_status != "bounded_extraction_no_deep_sanitizer":
        warnings.append("UNKNOWN_PAYLOAD_SAFETY_STATUS")

    if acquisition_deep_sanitized is not True:
        restrictions.append("ACQUISITION_PAYLOAD_NOT_DEEP_SANITIZED")

    if next_questions_deep_sanitized is not True:
        restrictions.append("NEXT_QUESTIONS_NOT_DEEP_SANITIZED")

    if _get_path(
        snapshot,
        ["research_interpretation_boundaries", "no_diagnosis"],
        False,
    ) is not True:
        blockers.append("MISSING_NO_DIAGNOSIS_BOUNDARY")

    if _get_path(
        snapshot,
        ["research_interpretation_boundaries", "no_authority"],
        False,
    ) is not True:
        blockers.append("MISSING_NO_AUTHORITY_BOUNDARY")

    if _get_path(
        snapshot,
        [
            "research_interpretation_boundaries",
            "not_participant_truth",
        ],
        False,
    ) is not True:
        blockers.append("MISSING_NOT_PARTICIPANT_TRUTH_BOUNDARY")

    if _get_path(
        snapshot,
        ["limitations", "raw_engine_result_excluded"],
        False,
    ) is not True:
        blockers.append("RAW_ENGINE_RESULT_NOT_EXCLUDED")

    raw_answers_excluded = _get_path(
        snapshot,
        ["limitations", "raw_answers_excluded"],
        None,
    )

    legacy_answers_excluded = _get_path(
        snapshot,
        ["limitations", "answers_excluded"],
        None,
    )

    if (
        raw_answers_excluded is not True
        and legacy_answers_excluded is not True
    ):
        blockers.append("RAW_ANSWERS_NOT_EXCLUDED")


    if _get_path(
        snapshot,
        ["limitations", "snapshot_is_not_runtime_memory"],
        False,
    ) is not True:
        blockers.append("MISSING_NOT_RUNTIME_MEMORY_BOUNDARY")

    if _get_path(
        snapshot,
        ["limitations", "no_longitudinal_aggregation"],
        False,
    ) is not True:
        blockers.append("MISSING_NO_LONGITUDINAL_AGGREGATION_BOUNDARY")

    if blockers:
        admission_status = "blocked"
        admission_allowed = False
        allowed_scope = "none"
        dataset_use_scope = "none"
    elif restrictions:
        admission_status = "restricted"
        admission_allowed = True
        allowed_scope = "single_snapshot_dataset_only"
        dataset_use_scope = "restricted_single_snapshot_dataset_only"
    else:
        admission_status = "allowed"
        admission_allowed = True
        allowed_scope = "single_snapshot_dataset_only"
        dataset_use_scope = "single_snapshot_dataset_only"

    return {
        "governance_scope": GOVERNANCE_SCOPE,
        "governance_version": AGGREGATION_GOVERNANCE_VERSION,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "evaluated_by": "research.aggregation_governance",
        "admission_allowed": admission_allowed,
        "admission_status": admission_status,
        "allowed_scope": allowed_scope,
        "blockers": blockers,
        "restrictions": restrictions,
        "warnings": warnings,
        "aggregation_performed": False,
        "longitudinal_admission_allowed": False,
        "participant_comparison_allowed": False,
        "dataset_use_scope": dataset_use_scope,
        "admission_decision_is_not_research_correctness": True,
        "admission_allowed_is_not_aggregation": True,
        "restricted_admission_is_not_longitudinal_permission": True,
    }
