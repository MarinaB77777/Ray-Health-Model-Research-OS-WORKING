import pytest

from research.answer_policy import (
    ANSWER_POLICY_REGISTRY,
    ANSWER_POLICY_VERSION,
    DEFAULT_POLICY,
    get_answer_policy,
)


def test_known_variable_returns_reviewed_policy():
    policy = get_answer_policy("__example_d1")

    assert policy["variable_code"] == "__example_d1"
    assert policy["policy_category"] == "exportable"
    assert policy["export_allowed"] is True
    assert policy["review_status"] == "reviewed"
    assert policy["policy_lookup_status"] == "found"
    assert (
        policy["classification_method"]
        == "static_lookup_only"
    )


def test_unknown_variable_returns_default_deny_policy():
    policy = get_answer_policy("unknown_variable")

    assert policy["variable_code"] == "unknown_variable"
    assert policy["policy_category"] == "not_yet_classified"
    assert policy["allowed_export_scope"] == []
    assert policy["export_allowed"] is False
    assert policy["requires_consent"] is True
    assert policy["review_status"] == "not_reviewed"
    assert policy["policy_lookup_status"] == "default_deny"
    assert (
        policy["classification_method"]
        == "static_lookup_only"
    )


def test_variable_code_is_normalized():
    policy = get_answer_policy("  __example_d1  ")

    assert policy["variable_code"] == "__example_d1"
    assert policy["policy_lookup_status"] == "found"


@pytest.mark.parametrize(
    "variable_code",
    [
        "",
        "   ",
    ],
)
def test_empty_variable_code_blocks(variable_code):
    with pytest.raises(ValueError):
        get_answer_policy(variable_code)


@pytest.mark.parametrize(
    "variable_code",
    [
        None,
        123,
        ["d1"],
        {"code": "d1"},
    ],
)
def test_non_string_variable_code_blocks(variable_code):
    with pytest.raises(ValueError):
        get_answer_policy(variable_code)


def test_returned_known_policy_mutation_does_not_mutate_registry():
    policy = get_answer_policy("__example_d1")
    policy["policy_category"] = "not_exportable"

    assert (
        ANSWER_POLICY_REGISTRY["__example_d1"][
            "policy_category"
        ]
        == "exportable"
    )


def test_returned_default_policy_mutation_does_not_mutate_default():
    policy = get_answer_policy("unknown_variable")
    policy["policy_category"] = "exportable"

    assert (
        DEFAULT_POLICY["policy_category"]
        == "not_yet_classified"
    )

def test_unknown_variable_has_no_export_scope():
    policy = get_answer_policy("unknown_variable")

    assert policy["allowed_export_scope"] == []
    assert policy["export_allowed"] is False
    assert policy["individual_snapshot_allowed"] is False
    assert policy["dataset_allowed"] is False
    assert policy["aggregation_allowed"] is False
    assert policy["linkage_allowed"] is False


def test_known_policy_is_static_lookup_not_inference():
    policy = get_answer_policy("__example_d1")

    assert policy["classification_method"] == "static_lookup_only"
    assert "participant" not in policy
    assert "score" not in policy
def test_nested_mutation_does_not_mutate_registry():
    policy = get_answer_policy("__example_d1")

    policy["allowed_export_scope"].append(
        "bad_scope"
    )

    assert (
        ANSWER_POLICY_REGISTRY["__example_d1"][
            "allowed_export_scope"
        ]
        == ["research_snapshot"]
    )


def test_unknown_policy_contains_policy_version():
    policy = get_answer_policy("unknown_variable")

    assert (
        policy["policy_version"]
        == ANSWER_POLICY_VERSION
    )


def test_unknown_policy_calls_return_independent_objects():
    policy_1 = get_answer_policy("unknown_variable")
    policy_2 = get_answer_policy("unknown_variable")

    policy_1["allowed_export_scope"].append(
        "bad_scope"
    )

    assert (
        policy_2["allowed_export_scope"]
        == []
    )

def test_returned_known_policy_nested_mutation_does_not_mutate_registry():
    policy = get_answer_policy("__example_d1")
    policy["allowed_export_scope"].append("bad_scope")

    assert (
        ANSWER_POLICY_REGISTRY["__example_d1"][
            "allowed_export_scope"
        ]
        == ["research_snapshot"]
    )


def test_returned_default_policy_nested_mutation_does_not_mutate_default():
    policy = get_answer_policy("unknown_variable")
    policy["allowed_export_scope"].append("bad_scope")

    assert DEFAULT_POLICY["allowed_export_scope"] == []