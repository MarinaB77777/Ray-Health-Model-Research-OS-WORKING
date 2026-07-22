from assessment.analysis.statistics.descriptive import group_descriptive_summary
from assessment.analysis.statistics.parametric_groups import (
    brown_forsythe_test,
    collect_independent_groups,
    one_way_anova,
)


def run_one_way_anova(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    collected = collect_independent_groups(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )
    if not collected.get("ok"):
        return {"ok": False, "method_id": "one_way_anova", **collected}
    variance_check = brown_forsythe_test(groups=collected["groups"])
    if not variance_check.get("ok"):
        return {"ok": False, "method_id": "one_way_anova", **variance_check}
    if variance_check["p_value"] < 0.05:
        return {
            "ok": False,
            "status": "homogeneity_of_variance_not_supported",
            "method_id": "one_way_anova",
            "variance_homogeneity_check": variance_check,
        }
    test = one_way_anova(groups=collected["groups"])
    if not test.get("ok"):
        return {"ok": False, "method_id": "one_way_anova", **test}
    alpha = 0.05
    p_value = test["p_value"]
    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "one_way_anova",
        "method_title": "One-way ANOVA",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "group_question_code": collected["group_question_code"],
        "outcome_question_code": collected["outcome_question_code"],
        "sample_size": sum(test["group_sizes"].values()),
        "test_statistic": test["test_statistic"],
        "test_statistic_name": "F",
        "degrees_of_freedom": {
            "between": test["numerator_degrees_of_freedom"],
            "within": test["denominator_degrees_of_freedom"],
        },
        "alpha": alpha,
        "p_value": p_value,
        "p_value_distribution": test["p_value_distribution"],
        "is_statistically_significant": p_value < alpha,
        "null_hypothesis": "All independent population means are equal.",
        "alternative_hypothesis": "At least one independent population mean differs.",
        "decision": "Reject H₀" if p_value < alpha else "Fail to reject H₀",
        "group_summary": {
            name: group_descriptive_summary(values)
            for name, values in collected["groups"].items()
        },
        "anova_table": {
            "between_groups": {
                "sum_of_squares": test["sum_of_squares_between"],
                "degrees_of_freedom": test["numerator_degrees_of_freedom"],
                "mean_square": test["mean_square_between"],
            },
            "within_groups": {
                "sum_of_squares": test["sum_of_squares_within"],
                "degrees_of_freedom": test["denominator_degrees_of_freedom"],
                "mean_square": test["mean_square_within"],
            },
        },
        "eta_squared": test["eta_squared"],
        "variance_homogeneity_check": variance_check,
        "excluded_subject_ids": collected["excluded_subject_ids"],
    }
