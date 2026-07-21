from research.answer_policy import ANSWER_POLICY_VERSION


ANSWER_POLICY_VALIDATOR_VERSION = "answer-policy-validator-1"

ALLOWED_POLICY_CATEGORIES = {
    "exportable",
    "aggregate_only",
    "requires_additional_consent",
    "transient_only",
    "not_exportable",
    "not_yet_classified",
}

ALLOWED_REVIEW_STATUSES = {
    "reviewed",
    "not_reviewed",
}

REQUIRED_KEYS = {
    "policy_category",
    "allowed_export_scope",
    "requires_consent",
    "consent_scope",
    "retention_class",
    "linkage_allowed",
    "aggregation_allowed",
    "individual_snapshot_allowed",
    "dataset_allowed",
    "export_allowed",
    "policy_version",
    "review_status",
    "rationale",
}

BOOLEAN_KEYS = {
    "requires_consent",
    "linkage_allowed",
    "aggregation_allowed",
    "individual_snapshot_allowed",
    "dataset_allowed",
    "export_allowed",
}

STRING_KEYS = {
    "policy_category",
    "consent_scope",
    "retention_class",
    "policy_version",
    "review_status",
    "rationale",
}

RESTRICTED_NON_EXPORT_CATEGORIES = {
    "not_exportable",
    "transient_only",
    "not_yet_classified",
    "requires_additional_consent",
}


def _add_missing_key_reasons(policy: dict, reason_codes: list) -> None:
    missing_keys = sorted(
        REQUIRED_KEYS - set(policy.keys())
    )

    for key in missing_keys:
        reason_codes.append(
            f"MISSING_REQUIRED_KEY:{key}"
        )


def _add_string_field_reasons(policy: dict, reason_codes: list) -> None:
    for key in sorted(STRING_KEYS):
        value = policy.get(key)

        if value is None:
            continue

        if not isinstance(value, str) or not value.strip():
            reason_codes.append(
                f"STRING_FIELD_INVALID:{key}"
            )


def _add_boolean_field_reasons(policy: dict, reason_codes: list) -> None:
    for key in sorted(BOOLEAN_KEYS):
        value = policy.get(key)

        if value is None:
            continue

        if not isinstance(value, bool):
            reason_codes.append(
                f"BOOLEAN_FIELD_NOT_BOOL:{key}"
            )


def _add_scope_reasons(policy: dict, reason_codes: list) -> None:
    allowed_export_scope = policy.get("allowed_export_scope")

    if allowed_export_scope is None:
        return

    if not isinstance(allowed_export_scope, list):
        reason_codes.append("ALLOWED_EXPORT_SCOPE_NOT_LIST")
        return

    for item in allowed_export_scope:
        if not isinstance(item, str) or not item.strip():
            reason_codes.append("ALLOWED_EXPORT_SCOPE_ITEM_INVALID")
            break


def _add_category_review_reasons(policy: dict, reason_codes: list) -> None:
    policy_category = policy.get("policy_category")
    review_status = policy.get("review_status")

    if (
        policy_category is not None
        and policy_category not in ALLOWED_POLICY_CATEGORIES
    ):
        reason_codes.append("INVALID_POLICY_CATEGORY")

    if (
        review_status is not None
        and review_status not in ALLOWED_REVIEW_STATUSES
    ):
        reason_codes.append("INVALID_REVIEW_STATUS")


def _add_export_consistency_reasons(
    policy: dict,
    reason_codes: list,
) -> None:
    policy_category = policy.get("policy_category")
    review_status = policy.get("review_status")
    allowed_export_scope = policy.get("allowed_export_scope")

    if policy.get("export_allowed") is True:
        if policy_category != "exportable":
            reason_codes.append(
                "EXPORT_ALLOWED_REQUIRES_EXPORTABLE_CATEGORY"
            )

        if review_status != "reviewed":
            reason_codes.append(
                "EXPORT_ALLOWED_REQUIRES_REVIEWED_STATUS"
            )

        if not isinstance(allowed_export_scope, list) or not allowed_export_scope:
            reason_codes.append(
                "EXPORT_ALLOWED_REQUIRES_NON_EMPTY_SCOPE"
            )

    if (
        policy.get("individual_snapshot_allowed") is True
        and policy.get("export_allowed") is not True
    ):
        reason_codes.append(
            "INDIVIDUAL_SNAPSHOT_REQUIRES_EXPORT_ALLOWED"
        )

    if policy_category in RESTRICTED_NON_EXPORT_CATEGORIES:
        if policy.get("export_allowed") is True:
            reason_codes.append(
                "RESTRICTED_CATEGORY_CANNOT_EXPORT"
            )

        if policy.get("individual_snapshot_allowed") is True:
            reason_codes.append(
                "RESTRICTED_CATEGORY_CANNOT_ALLOW_INDIVIDUAL_SNAPSHOT"
            )

        if policy.get("dataset_allowed") is True:
            reason_codes.append(
                "RESTRICTED_CATEGORY_CANNOT_ALLOW_DATASET"
            )

        if policy.get("aggregation_allowed") is True:
            reason_codes.append(
                "RESTRICTED_CATEGORY_CANNOT_ALLOW_AGGREGATION"
            )

    if (
        policy_category == "aggregate_only"
        and policy.get("individual_snapshot_allowed") is True
    ):
        reason_codes.append(
            "AGGREGATE_ONLY_CANNOT_ALLOW_INDIVIDUAL_SNAPSHOT"
        )

def validate_answer_policy(policy: dict) -> dict:
    reason_codes = []

    if not isinstance(policy, dict):
        return {
            "valid": False,
            "reason_codes": [
                "POLICY_NOT_DICT",
            ],
            "validator_version": ANSWER_POLICY_VALIDATOR_VERSION,
            "validator_is_static_structural_validator": True,
            "validator_is_not_policy_authority": True,
            "validator_does_not_repair_policy": True,
            "validator_does_not_classify_policy": True,
            "validator_does_not_authorize_export": True,
        }

    _add_missing_key_reasons(policy, reason_codes)
    _add_string_field_reasons(policy, reason_codes)
    _add_boolean_field_reasons(policy, reason_codes)
    _add_scope_reasons(policy, reason_codes)
    _add_category_review_reasons(policy, reason_codes)

    if policy.get("policy_version") != ANSWER_POLICY_VERSION:
        reason_codes.append("POLICY_VERSION_MISMATCH")

    _add_export_consistency_reasons(policy, reason_codes)

    return {
        "valid": len(reason_codes) == 0,
        "reason_codes": reason_codes,
        "validator_version": ANSWER_POLICY_VALIDATOR_VERSION,
        "validator_is_static_structural_validator": True,
        "validator_is_not_policy_authority": True,
        "validator_does_not_repair_policy": True,
        "validator_does_not_classify_policy": True,
        "validator_does_not_authorize_export": True,
    }
