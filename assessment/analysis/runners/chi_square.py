from assessment.analysis.statistics.contingency import (
    collect_contingency_table,
)
from assessment.analysis.statistics.chi_square import (
    chi_square_test_of_independence,
)


def run_chi_square(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    contingency = collect_contingency_table(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )

    if (
        contingency["row_count"] < 2
        or contingency["column_count"] < 2
    ):
        return {
            "ok": False,
            "status": "insufficient_categories",
            "method_id": "chi_square",
        }

    result = chi_square_test_of_independence(
        table=contingency["table"],
    )

    if not result["ok"]:
        return {
            "ok": False,
            "method_id": "chi_square",
            **result,
        }

    alpha = result["alpha"]
    p_value = result["p_value"]

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "chi_square",
        "method_title": "Chi-square test of independence",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": contingency["sample_size"],
        "test_statistic": result["test_statistic"],
        "test_statistic_name": result["test_statistic_name"],
        "degrees_of_freedom": result["degrees_of_freedom"],
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": (
            p_value is not None
            and p_value < alpha
        ),
        "null_hypothesis": (
            "The two categorical variables are independent."
        ),
        "alternative_hypothesis": (
            "The two categorical variables are associated."
        ),
        "decision": result["decision"],
        "contingency_table": contingency,
        "expected_counts": result["expected_counts"],
        "results": {
            "chi_square": result["test_statistic"],
            "p_value": p_value,
        },
        "interpretation": {
            "summary": (
                "Chi-square test of independence was calculated from the contingency table."
            ),
        },
    }