from copy import deepcopy

from research.answer_policy import (
    ANSWER_POLICY_REGISTRY,
    DEFAULT_POLICY,
)
from research.answer_policy_validator import (
    ANSWER_POLICY_VALIDATOR_VERSION,
    validate_answer_policy,
)


def test_validate_reviewed_exportable_policy_is_valid():
    policy = deepcopy(
        ANSWER_POLICY_REGISTRY["__example_d1"]
    )

    result = validate_answer_policy(policy)

    assert result["valid"] is True
    assert result["reason_codes"] == []
    assert (
        result["validator_version"]
        == ANSWER_POLICY_VALIDATOR_VERSION
    )


def test_validate_default_policy_is_valid_structurally():
    policy = deepcopy(DEFAULT_POLICY)

    result = validate_answer_policy(policy)

    assert result["valid"] is True
    assert result["reason_codes"] == []


def test_validate_policy_rejects_non_dict():
    result = validate_answer_policy("not-a-policy")

    assert result["valid"] is False
    assert result["reason_codes"] == ["POLICY_NOT_DICT"]


def test_validate_policy_requires_required_keys():
    policy = deepcopy(DEFAULT_POLICY)
    del policy["policy_category"]

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "MISSING_REQUIRED_KEY:policy_category"
        in result["reason_codes"]
    )


def test_validate_policy_rejects_invalid_policy_category():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "secret_category"

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert "INVALID_POLICY_CATEGORY" in result["reason_codes"]


def test_validate_policy_rejects_invalid_review_status():
    policy = deepcopy(DEFAULT_POLICY)
    policy["review_status"] = "auto_reviewed"

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert "INVALID_REVIEW_STATUS" in result["reason_codes"]


def test_validate_policy_rejects_non_list_scope():
    policy = deepcopy(DEFAULT_POLICY)
    policy["allowed_export_scope"] = "research_snapshot"

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "ALLOWED_EXPORT_SCOPE_NOT_LIST"
        in result["reason_codes"]
    )


def test_validate_policy_rejects_invalid_scope_item():
    policy = deepcopy(DEFAULT_POLICY)
    policy["allowed_export_scope"] = ["research_snapshot", 123]

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "ALLOWED_EXPORT_SCOPE_ITEM_INVALID"
        in result["reason_codes"]
    )


def test_validate_policy_rejects_policy_version_mismatch():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_version"] = "old-version"

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert "POLICY_VERSION_MISMATCH" in result["reason_codes"]


def test_validate_policy_rejects_non_boolean_fields():
    policy = deepcopy(DEFAULT_POLICY)
    policy["export_allowed"] = "yes"

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "BOOLEAN_FIELD_NOT_BOOL:export_allowed"
        in result["reason_codes"]
    )


def test_validate_policy_rejects_empty_string_fields():
    policy = deepcopy(DEFAULT_POLICY)
    policy["rationale"] = " "

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert "STRING_FIELD_INVALID:rationale" in result["reason_codes"]


def test_validate_export_allowed_requires_exportable_category():
    policy = deepcopy(DEFAULT_POLICY)
    policy["export_allowed"] = True
    policy["review_status"] = "reviewed"
    policy["allowed_export_scope"] = ["research_snapshot"]

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "EXPORT_ALLOWED_REQUIRES_EXPORTABLE_CATEGORY"
        in result["reason_codes"]
    )


def test_validate_export_allowed_requires_reviewed_status():
    policy = deepcopy(
        ANSWER_POLICY_REGISTRY["__example_d1"]
    )
    policy["review_status"] = "not_reviewed"

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "EXPORT_ALLOWED_REQUIRES_REVIEWED_STATUS"
        in result["reason_codes"]
    )


def test_validate_export_allowed_requires_non_empty_scope():
    policy = deepcopy(
        ANSWER_POLICY_REGISTRY["__example_d1"]
    )
    policy["allowed_export_scope"] = []

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "EXPORT_ALLOWED_REQUIRES_NON_EMPTY_SCOPE"
        in result["reason_codes"]
    )


def test_validate_restricted_categories_cannot_export():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "not_exportable"
    policy["export_allowed"] = True
    policy["review_status"] = "reviewed"
    policy["allowed_export_scope"] = ["research_snapshot"]

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "EXPORT_ALLOWED_REQUIRES_EXPORTABLE_CATEGORY"
        in result["reason_codes"]
    )
    assert (
        "RESTRICTED_CATEGORY_CANNOT_EXPORT"
        in result["reason_codes"]
    )


def test_validate_restricted_categories_cannot_allow_individual_snapshot():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "transient_only"
    policy["individual_snapshot_allowed"] = True

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "RESTRICTED_CATEGORY_CANNOT_ALLOW_INDIVIDUAL_SNAPSHOT"
        in result["reason_codes"]
    )


def test_validate_aggregate_only_cannot_allow_individual_snapshot():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "aggregate_only"
    policy["individual_snapshot_allowed"] = True

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "AGGREGATE_ONLY_CANNOT_ALLOW_INDIVIDUAL_SNAPSHOT"
        in result["reason_codes"]
    )


def test_validator_declares_non_authority_boundaries():
    result = validate_answer_policy(DEFAULT_POLICY)

    assert result["validator_is_static_structural_validator"] is True
    assert result["validator_is_not_policy_authority"] is True
    assert result["validator_does_not_repair_policy"] is True
    assert result["validator_does_not_classify_policy"] is True
    assert result["validator_does_not_authorize_export"] is True

def test_validate_restricted_categories_cannot_allow_dataset():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "not_exportable"
    policy["dataset_allowed"] = True

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "RESTRICTED_CATEGORY_CANNOT_ALLOW_DATASET"
        in result["reason_codes"]
    )


def test_validate_restricted_categories_cannot_allow_aggregation():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "not_yet_classified"
    policy["aggregation_allowed"] = True

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "RESTRICTED_CATEGORY_CANNOT_ALLOW_AGGREGATION"
        in result["reason_codes"]
    )


def test_validate_requires_additional_consent_cannot_export_by_default():
    policy = deepcopy(DEFAULT_POLICY)
    policy["policy_category"] = "requires_additional_consent"
    policy["export_allowed"] = True
    policy["review_status"] = "reviewed"
    policy["allowed_export_scope"] = ["research_snapshot"]

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "RESTRICTED_CATEGORY_CANNOT_EXPORT"
        in result["reason_codes"]
    )
