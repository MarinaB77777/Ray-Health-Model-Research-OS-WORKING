from assessment.analysis.statistics.grouping import (
    collect_grouped_numeric_values_bidirectional,
)
from assessment.analysis.statistics.descriptive import (
    group_descriptive_summary,
)
from assessment.analysis.statistics.kruskal_wallis import (
    kruskal_wallis_test,
)


def run_kruskal_wallis(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    groups = collect_grouped_numeric_values_bidirectional(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )

    if len(groups) < 3:
        return {
            "ok": False,
            "status": "three_or_more_groups_required",
            "method_id": "kruskal_wallis",
            "observed_group_count": len(groups),
        }

    test_result = kruskal_wallis_test(
        groups=groups,
    )

    if not test_result.get("ok"):
        return {
            "ok": False,
            "method_id": "kruskal_wallis",
            **test_result,
        }

    alpha = test_result["alpha"]
    p_value = test_result["p_value"]

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "kruskal_wallis",
        "method_title": "Kruskal-Wallis test",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": sum(len(values) for values in groups.values()),
        "test_statistic": test_result["test_statistic"],
        "test_statistic_name": test_result["test_statistic_name"],
        "degrees_of_freedom": test_result["degrees_of_freedom"],
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": (
            p_value is not None and p_value < alpha
        ),
        "null_hypothesis": (
            "The distributions of the outcome variable are the same across all groups."
        ),
        "alternative_hypothesis": (
            "At least one group distribution differs from the others."
        ),
        "decision": test_result["decision"],
        "group_summary": {
            group_name: group_descriptive_summary(values)
            for group_name, values in groups.items()
        },
        "results": {
            "h_statistic": test_result["test_statistic"],
            "p_value": p_value,
        },
        "interpretation": {
            "summary": (
                "Kruskal-Wallis test was calculated for three or more independent groups "
                "using ranked outcome values."
            ),
        },
    }