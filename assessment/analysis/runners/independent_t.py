from assessment.analysis.statistics.descriptive import group_descriptive_summary
from assessment.analysis.statistics.parametric_groups import (
    collect_independent_groups,
    independent_samples_t_test,
)


def run_independent_t_test(
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
        return {"ok": False, "method_id": "independent_t_test", **collected}
    test = independent_samples_t_test(groups=collected["groups"])
    if not test.get("ok"):
        return {"ok": False, "method_id": "independent_t_test", **test}
    alpha = 0.05
    p_value = test["p_value"]
    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "independent_t_test",
        "method_title": "Independent samples t-test",
        "method_variant": test["variant"],
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "group_question_code": collected["group_question_code"],
        "outcome_question_code": collected["outcome_question_code"],
        "sample_size": test["group_sizes"],
        "test_statistic": test["test_statistic"],
        "test_statistic_name": "t",
        "degrees_of_freedom": test["degrees_of_freedom"],
        "alpha": alpha,
        "p_value": p_value,
        "p_value_distribution": test["p_value_distribution"],
        "is_statistically_significant": p_value < alpha,
        "null_hypothesis": "The two independent population means are equal.",
        "alternative_hypothesis": "The two independent population means differ.",
        "decision": "Reject H₀" if p_value < alpha else "Fail to reject H₀",
        "group_summary": {
            name: group_descriptive_summary(values)
            for name, values in collected["groups"].items()
        },
        "mean_difference": test["mean_difference"],
        "standard_error": test["standard_error"],
        "cohens_d": test["cohens_d"],
        "variance_homogeneity_check": test["variance_homogeneity_check"],
        "excluded_subject_ids": collected["excluded_subject_ids"],
    }
