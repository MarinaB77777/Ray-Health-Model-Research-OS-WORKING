from copy import deepcopy


ANSWER_POLICY_VERSION = "answer-policy-1"


DEFAULT_POLICY = {
    "policy_category": "not_yet_classified",
    "allowed_export_scope": [],
    "requires_consent": True,
    "consent_scope": "not_defined",
    "retention_class": "not_defined",
    "linkage_allowed": False,
    "aggregation_allowed": False,
    "individual_snapshot_allowed": False,
    "dataset_allowed": False,
    "export_allowed": False,
    "policy_version": ANSWER_POLICY_VERSION,
    "review_status": "not_reviewed",
    "rationale": (
        "Default deny until explicit policy classification exists"
    ),
}

# Only explicitly reviewed structured variables may be marked exportable.
# Free-text dialogue, raw personal narratives, and unrestricted adaptive
# interview messages must remain default-deny unless a separate reviewed
# policy explicitly allows a bounded derived representation.

ANSWER_POLICY_REGISTRY = {
    "__example_d1": {
        "policy_category": "exportable",
        "allowed_export_scope": [
            "research_snapshot"
        ],
        "requires_consent": True,
        "consent_scope": "pilot_research",
        "retention_class": "bounded_research",
        "linkage_allowed": False,
        "aggregation_allowed": True,
        "individual_snapshot_allowed": True,
        "dataset_allowed": True,
        "export_allowed": True,
        "policy_version": ANSWER_POLICY_VERSION,
        "review_status": "reviewed",
        "rationale": (
            "Example reviewed exportable variable"
        ),
    },
}


def get_answer_policy(variable_code: str) -> dict:
    if not isinstance(variable_code, str):
        raise ValueError(
            "variable_code must be a string"
        )

    normalized_code = variable_code.strip()

    if not normalized_code:
        raise ValueError(
            "variable_code must not be empty"
        )

    policy = ANSWER_POLICY_REGISTRY.get(
        normalized_code
    )

    if policy is None:
        result = deepcopy(DEFAULT_POLICY)
        result["variable_code"] = normalized_code
        result["policy_lookup_status"] = (
            "default_deny"
        )
        result["classification_method"] = (
            "static_lookup_only"
        )
        return result

    result = deepcopy(policy)
    result["variable_code"] = normalized_code
    result["policy_lookup_status"] = "found"
    result["classification_method"] = (
        "static_lookup_only"
    )

    return result
