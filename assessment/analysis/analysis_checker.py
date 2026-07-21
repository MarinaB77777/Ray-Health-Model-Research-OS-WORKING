from assessment.analysis.analysis_method_registry import METHODS
from assessment.analysis.variable_metadata import build_variable_metadata
from assessment.analysis.checks.data_available import (
    check_variable_has_data,
)
from assessment.analysis.checks.scale_pattern import (
    check_scale_pattern_supported,
)
from assessment.analysis.checks.observed_groups import (
    check_observed_groups,
)
from assessment.analysis.checks.paired_observations import (
    check_paired_observations,
)
from assessment.analysis.checks.sample_size import (
    check_minimum_paired_sample_size,
)
from assessment.analysis.checks.monotonic_relationship import (
    check_monotonic_relationship_plausible,
)
from assessment.analysis.method_check_map import METHOD_CHECK_MAP
from assessment.analysis.checks.scale_defined import (
    check_scale_defined,
)
from assessment.analysis.checks.complete_pairs import (
    check_minimum_complete_pairs,
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
from assessment.analysis.checks.constant_variable import (
    check_not_constant_variable,
)
from assessment.measurement.scale_registry import (
    scale_matches_requirement,
)

def _values_for_question(answer_records: list[dict], question_code: str) -> list:
    return [
        record.get("answer_value")
        for record in answer_records
        if record.get("question_code") == question_code
    ]


def _non_missing(values: list) -> list:
    return [
        value for value in values
        if value is not None and value != ""
    ]


def _find_method(method_id: str) -> dict | None:
    for method in METHODS:
        if method.get("method_id") == method_id:
            return method
    return None


def _scale_matches(method: dict, left_scale: str | None, right_scale: str | None) -> bool:
    if not left_scale or not right_scale:
        return False

    for pattern in method.get("scale_patterns", []):
        if (
            any(
                scale_matches_requirement(left_scale, requirement)
                for requirement in pattern.get("left", [])
            )
            and any(
                scale_matches_requirement(right_scale, requirement)
                for requirement in pattern.get("right", [])
            )
        ):
            return True

    return False


def check_pair_analysis(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    method_id: str,
    answer_records: list[dict],
) -> dict:
    metadata = build_variable_metadata(study_id)

    record_metadata = _metadata_from_answer_records(answer_records)
    if not metadata:
        metadata = record_metadata
    else:
        metadata = dict(metadata)
        for code, values in record_metadata.items():
            current = dict(metadata.get(code) or {})
            for key, value in values.items():
                if current.get(key) in (None, ""):
                    current[key] = value
            metadata[code] = current

    left_meta = metadata.get(left_question_code, {})
    right_meta = metadata.get(right_question_code, {})

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

    left_values = _values_for_question(answer_records, left_question_code)
    right_values = _values_for_question(answer_records, right_question_code)

    left_non_missing = _non_missing(left_values)
    right_non_missing = _non_missing(right_values)

    left_scale = left_meta.get("scale_type")
    right_scale = right_meta.get("scale_type")

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


    for condition in method.get("required_conditions", []):
        if condition == "paired_observations":
            paired_check = check_paired_observations(
                answer_records=answer_records,
                left_question_code=left_question_code,
                right_question_code=right_question_code,
            )

            checks.append(paired_check)

            checks.append(
                check_minimum_paired_sample_size(
                    paired_count=paired_check["details"]["paired_subject_count"],
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
            checks.append(check_expected_cell_counts(
                left_values=left_values,
                right_values=right_values,
            ))
            continue

        if condition == "two_by_two_table":
            checks.append(check_two_by_two_table(
                left_values=left_values,
                right_values=right_values,
            ))
            continue

        if condition in {"two_groups", "three_or_more_groups"}:
            grouping_is_left = scale_matches_requirement(
                left_scale, "grouping"
            )
            group_values = left_non_missing if grouping_is_left else right_non_missing
            side = "left" if grouping_is_left else "right"
            checks.append(
                check_two_groups(values=group_values, variable_side=side)
                if condition == "two_groups"
                else check_three_or_more_groups(values=group_values, variable_side=side)
            )
            continue

        if condition == "linear_relationship_plausible":
            checks.append(check_linear_relationship_plausible(
                left_values=left_values,
                right_values=right_values,
            ))
            continue

        if condition == "no_extreme_outliers":
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
                "reason": "not implemented yet in analyzer checks",
            },
        })

    failed = [
        check for check in checks
        if check.get("status") == "failed"
    ]

    pending = [
        check for check in checks
        if check.get("status") == "pending"
    ]

    if failed:
        status = "not_applicable"
    elif pending:
        status = "candidate_needs_more_checks"
    else:
        status = "applicable"

    return {
        "ok": True,
        "analysis_type": "pair_analysis_check",
        "study_id": study_id,
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "method": method,
        "required_checks": required_checks,
        "left_variable": left_meta,
        "right_variable": right_meta,
        "status": status,
        "checks": checks,
    }

def _metadata_from_answer_records(
    answer_records: list[dict],
) -> dict:
    metadata = {}

    for record in answer_records:
        code = record.get("question_code")

        if not code:
            continue

        if code not in metadata:
            metadata[code] = {
                "question_code": code,
                "title": record.get("title"),
                "scale_type": record.get("scale_type"),
                "question_type": record.get("question_type"),
            }

        for key in ["title", "scale_type", "question_type"]:
            if metadata[code].get(key) is None and record.get(key) is not None:
                metadata[code][key] = record.get(key)

    return metadata
