from assessment.analysis.statistics.descriptive import group_descriptive_summary
from assessment.analysis.statistics.parametric_groups import (
    brown_forsythe_test,
    collect_independent_groups,
    welch_one_way_anova,
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
    test = welch_one_way_anova(groups=collected["groups"])
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
        "method_title": "Welch one-way ANOVA",
        "method_variant": test["variant"],
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
        "p_value_method": "welch_approximate_f",
        "is_statistically_significant": p_value < alpha,
        "null_hypothesis": "All independent population means are equal.",
        "alternative_hypothesis": "At least one independent population mean differs.",
        "decision": "Reject H₀" if p_value < alpha else "Fail to reject H₀",
        "group_summary": {
            name: group_descriptive_summary(values)
            for name, values in collected["groups"].items()
        },
        "welch_details": {
            "group_variances": test["group_variances"],
            "weighted_grand_mean": test["weighted_grand_mean"],
            "correction": test["welch_correction"],
        },
        "variance_homogeneity_check": variance_check,
        "excluded_subject_ids": collected["excluded_subject_ids"],
    }
