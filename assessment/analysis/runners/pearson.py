import math

from assessment.analysis.statistics.p_value import correlation_p_value


def _paired_numeric_values(
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> tuple[list[float], list[float]]:
    by_subject = {}

    for record in answer_records:
        subject_id = (
            record.get("participant_id")
            or record.get("subject_link_id")
            or record.get("session_id")
            or record.get("parent_record_id")
        )

        question_code = record.get("question_code")

        if not subject_id:
            continue

        if question_code not in {left_question_code, right_question_code}:
            continue

        by_subject.setdefault(subject_id, {})[question_code] = record.get("answer_value")

    left_values = []
    right_values = []

    for answers in by_subject.values():
        left = answers.get(left_question_code)
        right = answers.get(right_question_code)

        if left is None or right is None or left == "" or right == "":
            continue

        try:
            left_values.append(float(left))
            right_values.append(float(right))
        except (TypeError, ValueError):
            continue

    return left_values, right_values


def _pearson_correlation(
    x_values: list[float],
    y_values: list[float],
) -> float | None:
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return None

    mean_x = sum(x_values) / len(x_values)
    mean_y = sum(y_values) / len(y_values)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(x_values, y_values)
    )

    denominator_x = sum((x - mean_x) ** 2 for x in x_values)
    denominator_y = sum((y - mean_y) ** 2 for y in y_values)

    denominator = math.sqrt(denominator_x * denominator_y)

    if denominator == 0:
        return None

    return numerator / denominator


def run_pearson_correlation(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    left_values, right_values = _paired_numeric_values(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )

    sample_size = len(left_values)

    if sample_size < 3:
        return {
            "ok": False,
            "status": "not_enough_data",
            "method_id": "pearson_correlation",
            "sample_size": sample_size,
        }

    r_value = _pearson_correlation(
        left_values,
        right_values,
    )

    if r_value is None:
        return {
            "ok": False,
            "status": "correlation_not_defined",
            "method_id": "pearson_correlation",
            "sample_size": sample_size,
        }

    p_value = correlation_p_value(
        correlation=r_value,
        sample_size=sample_size,
    )

    alpha = 0.05

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "pearson_correlation",
        "method_title": "Pearson correlation",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": sample_size,
        "test_statistic": r_value,
        "test_statistic_name": "Pearson's r",
        "degrees_of_freedom": sample_size - 2,
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": (
            p_value is not None and p_value < alpha
        ),
        "null_hypothesis": (
            "There is no linear association between the selected variables."
        ),
        "alternative_hypothesis": (
            "There is a linear association between the selected variables."
        ),
        "decision": (
            "Reject H₀"
            if p_value is not None and p_value < alpha
            else "Fail to reject H₀"
        ),
        "results": {
            "pearson_r": r_value,
            "p_value": p_value,
        },
        "interpretation": {
            "summary": (
                "Pearson correlation was calculated using paired numeric "
                "responses from participants who answered both selected questions."
            ),
        },
    }