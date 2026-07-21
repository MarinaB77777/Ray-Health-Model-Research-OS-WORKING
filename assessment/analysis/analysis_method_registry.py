METHODS = [
    {
        "method_id": "chi_square",
        "title": "Chi-square test of independence",
        "category": "standard",
        "purpose": "association_between_categorical_variables",
        "scale_patterns": [
            {"left": ["categorical_association"], "right": ["categorical_association"]},
        ],
        "required_conditions": [
            "independent_observations",
            "sufficient_expected_cell_counts",
        ],
    },
    {
        "method_id": "fisher_exact",
        "title": "Fisher exact test",
        "category": "standard",
        "purpose": "association_between_two_binary_categorical_variables",
        "scale_patterns": [
            {"left": ["categorical_association"], "right": ["categorical_association"]},
        ],
        "required_conditions": [
            "two_by_two_table",
            "independent_observations",
        ],
    },
    {
        "method_id": "spearman_correlation",
        "title": "Spearman rank correlation",
        "category": "standard",
        "purpose": "monotonic_association_between_ordered_or_numeric_variables",
        "scale_patterns": [
            {"left": ["rank_based"], "right": ["rank_based"]},
        ],
        "required_conditions": [
            "paired_observations",
            "monotonic_relationship_plausible",
        ],
    },
    {
        "method_id": "pearson_correlation",
        "title": "Pearson correlation",
        "category": "standard",
        "purpose": "linear_association_between_numeric_variables",
        "scale_patterns": [
            {"left": ["parametric_numeric"], "right": ["parametric_numeric"]},
        ],
        "required_conditions": [
            "paired_observations",
            "linear_relationship_plausible",
            "no_extreme_outliers",
        ],
    },
    {
        "method_id": "mann_whitney_u",
        "title": "Mann-Whitney U test",
        "category": "standard",
        "purpose": "compare_numeric_or_ordinal_outcome_between_two_independent_groups",
        "scale_patterns": [
            {"left": ["grouping"], "right": ["rank_based"]},
            {"left": ["rank_based"], "right": ["grouping"]},
        ],
        "required_conditions": [
            "two_groups",
            "independent_observations",
        ],
    },
    {
        "method_id": "kruskal_wallis",
        "title": "Kruskal-Wallis test",
        "category": "standard",
        "purpose": "compare_numeric_or_ordinal_outcome_between_three_or_more_independent_groups",
        "scale_patterns": [
            {"left": ["grouping"], "right": ["rank_based"]},
            {"left": ["rank_based"], "right": ["grouping"]},
        ],
        "required_conditions": [
            "three_or_more_groups",
            "independent_observations",
        ],
    },
    {
        "method_id": "independent_t_test",
        "title": "Independent samples t-test",
        "category": "standard",
        "purpose": "compare_numeric_outcome_between_two_independent_groups",
        "scale_patterns": [
            {"left": ["grouping"], "right": ["parametric_numeric"]},
            {"left": ["parametric_numeric"], "right": ["grouping"]},
        ],
        "required_conditions": [
            "two_groups",
            "independent_observations",
            "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
            "variance_assumption_checked",
        ],
    },
    {
        "method_id": "one_way_anova",
        "title": "One-way ANOVA",
        "category": "standard",
        "purpose": "compare_numeric_outcome_between_three_or_more_independent_groups",
        "scale_patterns": [
            {"left": ["grouping"], "right": ["parametric_numeric"]},
            {"left": ["parametric_numeric"], "right": ["grouping"]},
        ],
        "required_conditions": [
            "three_or_more_groups",
            "independent_observations",
            "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
            "variance_assumption_checked",
        ],
    },
]


# A method may be scientifically registered before its numerical runner is
# implemented. Selection UIs must never present such a definition as directly
# executable.
EXECUTABLE_METHOD_IDS = {
    "chi_square",
    "fisher_exact",
    "spearman_correlation",
    "pearson_correlation",
    "mann_whitney_u",
    "kruskal_wallis",
}

for method in METHODS:
    method["execution_status"] = (
        "implemented"
        if method.get("method_id") in EXECUTABLE_METHOD_IDS
        else "registered_without_runner"
    )
