import math
from statistics import median

from assessment.analysis.statistics.descriptive import mean, sample_variance
from assessment.analysis.statistics.p_value import (
    f_distribution_survival_function,
    student_t_two_tailed_p_value,
)
from assessment.measurement.scale_registry import scale_matches_requirement


def _subject_id(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("session_id")
        or record.get("parent_record_id")
    )


def _scale_type(answer_records: list[dict], question_code: str) -> str | None:
    observed = {
        str(record.get("scale_type"))
        for record in answer_records
        if record.get("question_code") == question_code
        and record.get("scale_type") not in (None, "")
    }
    return next(iter(observed)) if len(observed) == 1 else None


def collect_independent_groups(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> dict:
    """Collect one outcome per independent unit using the registered scales.

    Direction is determined from scale metadata, never guessed from the number
    of distinct numeric values. This prevents a numeric outcome from being
    silently reinterpreted as a grouping variable.
    """
    left_scale = _scale_type(answer_records, left_question_code)
    right_scale = _scale_type(answer_records, right_question_code)
    left_is_grouping = bool(
        left_scale and scale_matches_requirement(left_scale, "grouping")
    )
    right_is_grouping = bool(
        right_scale and scale_matches_requirement(right_scale, "grouping")
    )
    if left_is_grouping == right_is_grouping:
        return {
            "ok": False,
            "status": "exactly_one_grouping_variable_required",
            "left_scale_type": left_scale,
            "right_scale_type": right_scale,
        }

    group_code = left_question_code if left_is_grouping else right_question_code
    outcome_code = right_question_code if left_is_grouping else left_question_code
    by_subject: dict[str, dict] = {}
    duplicate_values: list[dict] = []

    for record in answer_records:
        code = record.get("question_code")
        if code not in {group_code, outcome_code}:
            continue
        subject_id = _subject_id(record)
        if not subject_id:
            continue
        subject = by_subject.setdefault(str(subject_id), {})
        if code in subject:
            duplicate_values.append({"subject_id": str(subject_id), "question_code": code})
            continue
        subject[code] = record.get("answer_value")

    if duplicate_values:
        return {
            "ok": False,
            "status": "repeated_observations_require_explicit_selection",
            "duplicates": duplicate_values,
        }

    groups: dict[str, list[float]] = {}
    excluded_subjects = []
    for subject_id, values in by_subject.items():
        group_value = values.get(group_code)
        outcome_value = values.get(outcome_code)
        if group_value in (None, "") or outcome_value in (None, ""):
            excluded_subjects.append(subject_id)
            continue
        try:
            numeric_outcome = float(outcome_value)
        except (TypeError, ValueError):
            excluded_subjects.append(subject_id)
            continue
        if not math.isfinite(numeric_outcome):
            excluded_subjects.append(subject_id)
            continue
        groups.setdefault(str(group_value), []).append(numeric_outcome)

    return {
        "ok": True,
        "status": "ready",
        "group_question_code": group_code,
        "outcome_question_code": outcome_code,
        "groups": groups,
        "included_subject_count": sum(len(values) for values in groups.values()),
        "excluded_subject_ids": excluded_subjects,
    }


def brown_forsythe_test(*, groups: dict[str, list[float]]) -> dict:
    if len(groups) < 2 or any(len(values) < 2 for values in groups.values()):
        return {"ok": False, "status": "at_least_two_values_per_group_required"}
    deviations = {
        name: [abs(value - median(values)) for value in values]
        for name, values in groups.items()
    }
    result = one_way_anova(groups=deviations, minimum_group_count=2)
    if not result.get("ok"):
        if result.get("status") == "zero_within_group_variation":
            return {
                "ok": True,
                "status": "completed",
                "test_statistic": 0.0,
                "p_value": 1.0,
                "numerator_degrees_of_freedom": len(groups) - 1,
                "denominator_degrees_of_freedom": sum(map(len, groups.values())) - len(groups),
            }
        return result
    return result


def independent_samples_t_test(*, groups: dict[str, list[float]]) -> dict:
    if len(groups) != 2:
        return {"ok": False, "status": "exactly_two_groups_required"}
    names = sorted(groups)
    first = [float(value) for value in groups[names[0]]]
    second = [float(value) for value in groups[names[1]]]
    if len(first) < 2 or len(second) < 2:
        return {"ok": False, "status": "at_least_two_values_per_group_required"}

    mean_1, mean_2 = mean(first), mean(second)
    variance_1, variance_2 = sample_variance(first), sample_variance(second)
    variance_check = brown_forsythe_test(groups={names[0]: first, names[1]: second})
    equal_variance_supported = bool(
        variance_check.get("ok") and variance_check.get("p_value", 0.0) >= 0.05
    )

    n1, n2 = len(first), len(second)
    if equal_variance_supported:
        degrees_of_freedom = float(n1 + n2 - 2)
        pooled_variance = (
            (n1 - 1) * variance_1 + (n2 - 1) * variance_2
        ) / degrees_of_freedom
        standard_error = math.sqrt(pooled_variance * (1.0 / n1 + 1.0 / n2))
        variant = "student_equal_variance"
    else:
        term_1 = variance_1 / n1
        term_2 = variance_2 / n2
        standard_error = math.sqrt(term_1 + term_2)
        denominator = term_1 * term_1 / (n1 - 1) + term_2 * term_2 / (n2 - 1)
        if denominator <= 0:
            return {"ok": False, "status": "degrees_of_freedom_undefined"}
        degrees_of_freedom = (term_1 + term_2) ** 2 / denominator
        pooled_variance = None
        variant = "welch_unequal_variance"

    if standard_error == 0:
        return {"ok": False, "status": "zero_standard_error"}
    t_statistic = (mean_1 - mean_2) / standard_error
    p_value = student_t_two_tailed_p_value(
        t_statistic=t_statistic,
        degrees_of_freedom=degrees_of_freedom,
    )
    pooled_sd = None
    if pooled_variance is not None and pooled_variance > 0:
        pooled_sd = math.sqrt(pooled_variance)

    return {
        "ok": True,
        "status": "completed",
        "variant": variant,
        "group_names": names,
        "group_sizes": {names[0]: n1, names[1]: n2},
        "group_means": {names[0]: mean_1, names[1]: mean_2},
        "group_variances": {names[0]: variance_1, names[1]: variance_2},
        "mean_difference": mean_1 - mean_2,
        "standard_error": standard_error,
        "test_statistic": t_statistic,
        "degrees_of_freedom": degrees_of_freedom,
        "p_value": p_value,
        "cohens_d": (mean_1 - mean_2) / pooled_sd if pooled_sd else None,
        "variance_homogeneity_check": variance_check,
        "p_value_distribution": "student_t",
    }


def one_way_anova(
    *,
    groups: dict[str, list[float]],
    minimum_group_count: int = 3,
) -> dict:
    if len(groups) < minimum_group_count:
        return {
            "ok": False,
            "status": (
                "three_or_more_groups_required"
                if minimum_group_count >= 3
                else "two_or_more_groups_required"
            ),
        }
    numeric = {name: [float(value) for value in values] for name, values in groups.items()}
    if any(len(values) < 2 for values in numeric.values()):
        return {"ok": False, "status": "at_least_two_values_per_group_required"}
    total_n = sum(len(values) for values in numeric.values())
    group_count = len(numeric)
    grand_mean = sum(sum(values) for values in numeric.values()) / total_n
    group_means = {name: mean(values) for name, values in numeric.items()}
    ss_between = sum(
        len(numeric[name]) * (group_means[name] - grand_mean) ** 2
        for name in numeric
    )
    ss_within = sum(
        sum((value - group_means[name]) ** 2 for value in values)
        for name, values in numeric.items()
    )
    df_between = group_count - 1
    df_within = total_n - group_count
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    if ms_within == 0:
        return {"ok": False, "status": "zero_within_group_variation"}
    f_statistic = ms_between / ms_within
    p_value = f_distribution_survival_function(
        f_statistic=f_statistic,
        numerator_degrees_of_freedom=df_between,
        denominator_degrees_of_freedom=df_within,
    )
    ss_total = ss_between + ss_within
    return {
        "ok": True,
        "status": "completed",
        "test_statistic": f_statistic,
        "p_value": p_value,
        "numerator_degrees_of_freedom": df_between,
        "denominator_degrees_of_freedom": df_within,
        "group_sizes": {name: len(values) for name, values in numeric.items()},
        "group_means": group_means,
        "grand_mean": grand_mean,
        "sum_of_squares_between": ss_between,
        "sum_of_squares_within": ss_within,
        "mean_square_between": ms_between,
        "mean_square_within": ms_within,
        "eta_squared": ss_between / ss_total if ss_total > 0 else None,
        "p_value_distribution": "f",
    }
