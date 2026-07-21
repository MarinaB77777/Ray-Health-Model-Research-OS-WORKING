from research.answer_policy import (
    ANSWER_POLICY_VERSION,
    get_answer_policy,
)
from research.answer_policy_validator import validate_answer_policy


ANSWER_EXPORT_FILTER_VERSION = "answer-export-filter-1"
RESEARCH_SNAPSHOT_SCOPE = "research_snapshot"


def _is_allowed_for_research_snapshot(policy: dict) -> bool:
    return (
        policy.get("policy_category") == "exportable"
        and policy.get("export_allowed") is True
        and policy.get("individual_snapshot_allowed") is True
        and RESEARCH_SNAPSHOT_SCOPE
        in policy.get("allowed_export_scope", [])
        and policy.get("review_status") == "reviewed"
        and policy.get("policy_version") == ANSWER_POLICY_VERSION
    )


def _build_exclusion_reason(policy: dict) -> str:
    if policy.get("policy_lookup_status") == "default_deny":
        return "ANSWER_POLICY_NOT_CLASSIFIED"

    if policy.get("policy_version") != ANSWER_POLICY_VERSION:
        return "ANSWER_POLICY_VERSION_MISMATCH"

    if policy.get("review_status") != "reviewed":
        return "ANSWER_POLICY_NOT_REVIEWED"

    if policy.get("policy_category") != "exportable":
        return "ANSWER_POLICY_NOT_EXPORTABLE"

    if policy.get("export_allowed") is not True:
        return "ANSWER_EXPORT_NOT_ALLOWED"

    if policy.get("individual_snapshot_allowed") is not True:
        return "ANSWER_INDIVIDUAL_SNAPSHOT_NOT_ALLOWED"

    if RESEARCH_SNAPSHOT_SCOPE not in policy.get(
        "allowed_export_scope",
        [],
    ):
        return "ANSWER_SCOPE_NOT_ALLOWED"

    return "ANSWER_EXCLUDED_BY_POLICY"


def filter_answers_for_research_snapshot(
    answers: dict,
) -> dict:
    if not isinstance(answers, dict):
        raise ValueError("answers must be a dict")

    included_answers = {}
    excluded_answers = {}
    seen_variable_codes = set()
    duplicate_variable_codes = []
    duplicate_exclusions = []

    for raw_variable_code, value in answers.items():
        policy = get_answer_policy(raw_variable_code)
        variable_code = policy["variable_code"]

        validation = validate_answer_policy(policy)

        if validation["valid"] is not True:
            excluded_answers[variable_code] = {
                "policy_category": policy.get("policy_category"),
                "reason_code": "ANSWER_POLICY_INVALID",
                "policy_version": policy.get("policy_version"),
                "review_status": policy.get("review_status"),
                "allowed_export_scope": policy.get(
                    "allowed_export_scope",
                    [],
                ),
                "policy_validation": validation,
            }
            continue

        if variable_code in seen_variable_codes:
            duplicate_variable_codes.append(variable_code)
            duplicate_exclusions.append(
                {
                    "variable_code": variable_code,
                    "reason_code": "DUPLICATE_NORMALIZED_VARIABLE_CODE",
                }
            )
            excluded_answers[variable_code] = {
                "policy_category": policy.get("policy_category"),
                "reason_code": "DUPLICATE_NORMALIZED_VARIABLE_CODE",
                "policy_version": policy.get("policy_version"),
                "review_status": policy.get("review_status"),
                "allowed_export_scope": policy.get(
                    "allowed_export_scope",
                    [],
                ),
            }

            if variable_code in included_answers:
                del included_answers[variable_code]

            continue

        seen_variable_codes.add(variable_code)

        if _is_allowed_for_research_snapshot(policy):
            included_answers[variable_code] = {
                "value": value,
                "policy_category": policy["policy_category"],
                "reason_code": "ANSWER_INCLUDED_BY_POLICY",
                "policy_version": policy["policy_version"],
                "review_status": policy["review_status"],
                "allowed_export_scope": policy.get(
                    "allowed_export_scope",
                    [],
                ),
            }
            continue

        excluded_answers[variable_code] = {
            "policy_category": policy.get("policy_category"),
            "reason_code": _build_exclusion_reason(policy),
            "policy_version": policy.get("policy_version"),
            "review_status": policy.get("review_status"),
            "allowed_export_scope": policy.get(
                "allowed_export_scope",
                [],
            ),
        }

    return {
        "included_answers": included_answers,
        "excluded_answers": excluded_answers,
        "answer_count": len(answers),
        "included_count": len(included_answers),
        "excluded_count": len(excluded_answers),
        "duplicate_variable_codes_detected": (
            duplicate_variable_codes
        ),
        "duplicate_exclusions": duplicate_exclusions,
        "count_basis": "unique_normalized_variable_codes",
        "answer_policy_version": ANSWER_POLICY_VERSION,
        "filter_version": ANSWER_EXPORT_FILTER_VERSION,
        "filter_method": "static_answer_policy_lookup",
        "filter_scope": RESEARCH_SNAPSHOT_SCOPE,
        "answer_values_filtered": True,
        "unknown_policy_default_deny": True,
        "policy_validation_applied": True,
        "invalid_policy_fail_closed": True,
        "malformed_policy_handling": (
            "invalid_policy_excluded_with_audit"
        ),
        "included_values_are_raw_policy_allowed": True,
        "included_answers_are_not_final_export_authorization": True,
        "consent_evaluated": False,
        "retention_evaluated": False,
        "filter_is_not_consent_resolution": True,
        "filter_is_not_retention_engine": True,
        "filter_is_not_research_analytics": True,
        "filter_is_not_auto_classifier": True,
        "filter_is_not_export_authority": True,
        "filter_is_not_policy_review": True,
    }