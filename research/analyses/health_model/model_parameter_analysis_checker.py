from assessment.analysis.analysis_method_registry import METHODS
from assessment.analysis.method_check_map import METHOD_CHECK_MAP

from assessment.analysis.checks.data_available import (
    check_variable_has_data,
)
from assessment.analysis.checks.scale_defined import (
    check_scale_defined,
)
from assessment.analysis.checks.scale_pattern import (
    check_scale_pattern_supported,
)
from assessment.analysis.checks.observed_groups import (
    check_observed_groups,
)
from assessment.analysis.checks.constant_variable import (
    check_not_constant_variable,
)
from assessment.analysis.checks.paired_observations import (
    check_paired_observations,
)
from assessment.analysis.checks.sample_size import (
    check_minimum_paired_sample_size,
)
from assessment.analysis.checks.complete_pairs import (
    check_minimum_complete_pairs,
)
from assessment.analysis.checks.monotonic_relationship import (
    check_monotonic_relationship_plausible,
)
from assessment.analysis.checks.independent_observations import (
    check_independent_observations,
)
from assessment.analysis.checks.expected_counts import (
    check_expected_cell_counts,
)
from assessment.analysis.checks.contingency_table import (
    check_two_by_two_table,
)
from assessment.analysis.checks.group_count import (
    check_three_or_more_groups,
    check_two_groups,
)
from assessment.analysis.checks.linear_relationship import (
    check_linear_relationship_plausible,
)
from assessment.analysis.checks.outliers import (
    check_extreme_outliers_iqr,
)
from assessment.analysis.checks.group_balance import check_group_balance
from assessment.analysis.checks.group_size import check_minimum_group_size
from assessment.analysis.checks.normality import check_group_normality
from assessment.analysis.checks.numeric_data import check_numeric_data
from assessment.analysis.checks.variance import check_variance_assumption
from assessment.analysis.statistics.parametric_groups import (
    collect_independent_groups,
)
from assessment.analysis.statistics.contingency import collect_contingency_table
from assessment.measurement.scale_registry import (
    scale_matches_requirement,
)


def _values_for_question(
    answer_records: list[dict],
    question_code: str,
) -> list:
    return [
        record.get("answer_value")
        for record in answer_records
        if record.get("question_code") == question_code
    ]


def _non_missing(values: list) -> list:
    return [
        value
        for value in values
        if value is not None and value != ""
    ]


def _find_method(method_id: str) -> dict | None:
    for method in METHODS:
        if method.get("method_id") == method_id:
            return method

    return None


def check_model_parameter_pair_analysis(
    *,
    dataset: dict,
    method_id: str,
) -> dict:
    if not dataset.get("ok"):
        return {
            "ok": False,
            "status": "parameter_dataset_not_ready",
            "dataset_status": dataset.get("status"),
            "dataset": dataset,
        }

    method = _find_method(method_id)

    if method is None:
        return {
            "ok": False,
            "status": "method_not_found",
            "method_id": method_id,
        }

    required_checks = METHOD_CHECK_MAP.get(method_id)

    if required_checks is None:
        return {
            "ok": False,
            "status": "method_check_map_not_found",
            "method_id": method_id,
        }

    answer_records = dataset.get(
        "compatible_answer_records",
        [],
    )

    left_meta = dataset.get("left_variable", {})
    right_meta = dataset.get("right_variable", {})

    left_question_code = left_meta.get("variable_code")
    right_question_code = right_meta.get("variable_code")

    if not left_question_code or not right_question_code:
        return {
            "ok": False,
            "status": "variable_metadata_missing",
            "left_variable": left_meta,
            "right_variable": right_meta,
        }

    left_values = _values_for_question(
        answer_records,
        left_question_code,
    )

    right_values = _values_for_question(
        answer_records,
        right_question_code,
    )

    left_non_missing = _non_missing(left_values)
    right_non_missing = _non_missing(right_values)

    left_scale = left_meta.get("scale_type")
    right_scale = right_meta.get("scale_type")

    grouped_dataset = None

    def independent_groups() -> dict:
        nonlocal grouped_dataset
        if grouped_dataset is None:
            grouped_dataset = collect_independent_groups(
                answer_records=answer_records,
                left_question_code=left_question_code,
                right_question_code=right_question_code,
            )
        return grouped_dataset

    checks = []

    checks.append(
        check_variable_has_data(
            question_code=left_question_code,
            answer_records=answer_records,
            side="left",
        )
    )

    checks.append(
        check_variable_has_data(
            question_code=right_question_code,
            answer_records=answer_records,
            side="right",
        )
    )

    checks.append(
        check_scale_defined(
            left_scale=left_scale,
            right_scale=right_scale,
        )
    )

    checks.append(
        check_scale_pattern_supported(
            method=method,
            left_scale=left_scale,
            right_scale=right_scale,
        )
    )

    checks.append(
        check_observed_groups(
            values=left_non_missing,
            side="left",
        )
    )

    checks.append(
        check_observed_groups(
            values=right_non_missing,
            side="right",
        )
    )

    checks.append(
        check_not_constant_variable(
            values=left_values,
            variable_name=left_question_code,
        )
    )

    checks.append(
        check_not_constant_variable(
            values=right_values,
            variable_name=right_question_code,
        )
    )

    for condition in method.get(
        "required_conditions",
        [],
    ):
        if condition == "paired_observations":
            paired_check = check_paired_observations(
                answer_records=answer_records,
                left_question_code=left_question_code,
                right_question_code=right_question_code,
            )

            checks.append(paired_check)

            checks.append(
                check_minimum_paired_sample_size(
                    paired_count=(
                        paired_check["details"][
                            "paired_subject_count"
                        ]
                    ),
                    minimum_required=3,
                )
            )

            checks.append(
                check_minimum_complete_pairs(
                    left_values=left_values,
                    right_values=right_values,
                    minimum_required=3,
                )
            )

            continue

        if condition == "monotonic_relationship_plausible":
            checks.append(
                check_monotonic_relationship_plausible(
                    answer_records=answer_records,
                    left_question_code=left_question_code,
                    right_question_code=right_question_code,
                    minimum_pairs=3,
                )
            )

            continue

        if condition == "independent_observations":
            checks.append(check_independent_observations(
                answer_records=[
                    record for record in answer_records
                    if record.get("question_code") == left_question_code
                ],
            ))
            continue

        if condition == "sufficient_expected_cell_counts":
            contingency = collect_contingency_table(
                answer_records=answer_records,
                left_question_code=left_question_code,
                right_question_code=right_question_code,
            )
            if not contingency.get("ok"):
                checks.append({
                    "check_id": "expected_cell_counts",
                    "status": "failed",
                    "details": contingency,
                })
            else:
                checks.append(check_expected_cell_counts(table=contingency["table"]))
            continue

        if condition == "two_by_two_table":
            checks.append(check_two_by_two_table(
                left_values=left_values,
                right_values=right_values,
            ))
            continue

        if condition in {"two_groups", "three_or_more_groups"}:
            grouping_is_left = scale_matches_requirement(left_scale, "grouping")
            group_values = left_non_missing if grouping_is_left else right_non_missing
            side = "left" if grouping_is_left else "right"
            checks.append(
                check_two_groups(values=group_values, variable_side=side)
                if condition == "two_groups"
                else check_three_or_more_groups(values=group_values, variable_side=side)
            )
            continue

        if condition == "minimum_group_size":
            grouped = independent_groups()
            if not grouped.get("ok"):
                checks.append({"check_id": condition, "status": "failed", "details": grouped})
            else:
                checks.append(check_minimum_group_size(
                    group_values=[name for name, values in grouped["groups"].items() for _ in values],
                    minimum_per_group=2,
                ))
            continue

        if condition == "group_balance":
            grouped = independent_groups()
            if not grouped.get("ok"):
                checks.append({"check_id": condition, "status": "failed", "details": grouped})
            else:
                checks.append(check_group_balance(group_values=[
                    name for name, values in grouped["groups"].items() for _ in values
                ]))
            continue

        if condition == "normality_diagnostic_within_groups":
            grouped = independent_groups()
            if not grouped.get("ok"):
                checks.append({"check_id": condition, "status": "failed", "details": grouped})
            else:
                checks.append(check_group_normality(groups=grouped["groups"]))
            continue

        if condition == "variance_assumption_checked":
            grouped = independent_groups()
            if not grouped.get("ok"):
                checks.append({"check_id": condition, "status": "failed", "details": grouped})
            else:
                variance_check = check_variance_assumption(groups=grouped["groups"])
                if method_id in {"independent_t_test", "one_way_anova"} and variance_check.get("status") == "failed":
                    variance_check["status"] = "warning"
                    variance_check["details"]["selected_variant"] = (
                        "welch_unequal_variance"
                        if method_id == "independent_t_test"
                        else "welch_heteroscedastic"
                    )
                checks.append(variance_check)
            continue

        if condition == "numeric_data":
            grouping_is_left = scale_matches_requirement(left_scale, "grouping")
            checks.append(check_numeric_data(
                values=right_values if grouping_is_left else left_values,
                variable_name=right_question_code if grouping_is_left else left_question_code,
            ))
            continue

        if condition == "linear_relationship_plausible":
            checks.append(check_linear_relationship_plausible(
                left_values=left_values,
                right_values=right_values,
            ))
            continue

        if condition == "no_extreme_outliers":
            if scale_matches_requirement(left_scale, "grouping"):
                right_check = check_extreme_outliers_iqr(values=right_values)
                right_check["details"]["variable_side"] = "right"
                checks.append(right_check)
                continue
            if scale_matches_requirement(right_scale, "grouping"):
                left_check = check_extreme_outliers_iqr(values=left_values)
                left_check["details"]["variable_side"] = "left"
                checks.append(left_check)
                continue
            left_check = check_extreme_outliers_iqr(values=left_values)
            left_check["details"]["variable_side"] = "left"
            right_check = check_extreme_outliers_iqr(values=right_values)
            right_check["details"]["variable_side"] = "right"
            checks.extend([left_check, right_check])
            continue

        checks.append({
            "check_id": condition,
            "status": "pending",
            "details": {
                "reason": (
                    "not implemented yet in analyzer checks"
                ),
            },
        })

    if str(dataset.get("analysis_scope") or "").upper() == "WITHIN_PARTICIPANT":
        checks.append({
            "check_id": "within_participant_dependence_model",
            "status": "failed",
            "details": {
                "reason": "Standard independent or cross-sectional pair methods do not model serial dependence within one participant.",
                "required_method_family": "registered_longitudinal_or_time_series_method",
            },
        })

    if str(dataset.get("analysis_scope") or "").upper() == "GROUP_COMPARISON":
        if not str(method.get("purpose") or "").startswith("compare_"):
            checks.append({
                "check_id": "group_comparison_method_family",
                "status": "failed",
                "details": {
                    "reason": "Group-comparison scope requires an explicit grouping variable and an independent-group comparison method."
                },
            })

    failed = [
        check
        for check in checks
        if check.get("status") == "failed"
    ]

    blocked = [
        check
        for check in checks
        if check.get("status") == "blocked"
    ]

    pending = [
        check
        for check in checks
        if check.get("status") == "pending"
    ]

    if failed:
        status = "not_applicable"
    elif blocked:
        status = "not_enough_data"
    elif pending:
        status = "candidate_needs_more_checks"
    else:
        status = "applicable"

    return {
        "ok": True,
        "analysis_type": (
            "parameter_pair_analysis_check"
        ),
        "model_id": dataset.get("model_id"),
        "analysis_scope": dataset.get(
            "analysis_scope"
        ),
        "observation_unit": dataset.get(
            "observation_unit"
        ),
        "repeated_measure_policy": dataset.get(
            "repeated_measure_policy"
        ),
        "participant_reference": dataset.get(
            "participant_reference"
        ),
        "selected_observation_count": dataset.get(
            "selected_observation_count"
        ),
        "method": method,
        "required_checks": required_checks,
        "left_variable": left_meta,
        "right_variable": right_meta,
        "status": status,
        "checks": checks,
    }
