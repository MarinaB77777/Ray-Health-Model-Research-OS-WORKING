METHOD_CHECK_MAP = {
    "spearman_correlation": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "paired_observations",
        "minimum_complete_pairs",
        "not_constant_variable",
        "monotonic_relationship_plausible",
    ],

    "pearson_correlation": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "numeric_data",
        "paired_observations",
        "minimum_complete_pairs",
        "not_constant_variable",
        "linear_relationship_plausible",
        "no_extreme_outliers",
        "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
    ],

    "mann_whitney_u": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "independent_observations",
        "two_groups",
        "minimum_group_size",
        "group_balance",
    ],

    "independent_t_test": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "numeric_data",
        "independent_observations",
        "two_groups",
        "minimum_group_size",
        "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
        "variance_assumption_checked",
        "no_extreme_outliers",
    ],

    "one_way_anova": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "numeric_data",
        "independent_observations",
        "three_or_more_groups",
        "minimum_group_size",
        "group_balance",
        "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
        "variance_assumption_checked",
        "no_extreme_outliers",
    ],

    "kruskal_wallis": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "independent_observations",
        "three_or_more_groups",
        "minimum_group_size",
        "group_balance",
    ],

    "chi_square": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "independent_observations",
        "contingency_table",
        "expected_cell_counts",
    ],

    "fisher_exact": [
        "data_available",
        "scale_defined",
        "scale_pattern_supported",
        "independent_observations",
        "two_by_two_table",
    ],
}