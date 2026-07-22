import math
from assessment.analysis.statistics.p_value import spearman_permutation_p_value


def _paired_numeric_values(
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> dict:
    by_subject = {}
    duplicate_values = []

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

        subject = by_subject.setdefault(subject_id, {})
        if question_code in subject:
            duplicate_values.append({
                "subject_id": str(subject_id),
                "question_code": question_code,
            })
            continue
        subject[question_code] = record.get("answer_value")

    if duplicate_values:
        return {
            "ok": False,
            "status": "repeated_observations_require_explicit_selection",
            "duplicates": duplicate_values,
        }

    left_values = []
    right_values = []

    for answers in by_subject.values():
        left = answers.get(left_question_code)
        right = answers.get(right_question_code)

        if left is None or right is None or left == "" or right == "":
            continue

        try:
            numeric_left = float(left)
            numeric_right = float(right)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(numeric_left) or not math.isfinite(numeric_right):
            continue
        left_values.append(numeric_left)
        right_values.append(numeric_right)

    return {"ok": True, "left_values": left_values, "right_values": right_values}


def _rank_values(values: list[float]) -> list[float]:
    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1],
    )

    ranks = [0.0] * len(values)
    i = 0

    while i < len(indexed):
        j = i

        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1

        average_rank = (i + 1 + j + 1) / 2

        for k in range(i, j + 1):
            original_index = indexed[k][0]
            ranks[original_index] = average_rank

        i = j + 1

    return ranks


def _pearson_correlation(x_values: list[float], y_values: list[float]) -> float | None:
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


def run_spearman_correlation(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    paired = _paired_numeric_values(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )
    if not paired.get("ok"):
        return {"method_id": "spearman_correlation", **paired}
    left_values = paired["left_values"]
    right_values = paired["right_values"]

    sample_size = len(left_values)

    if sample_size < 3:
        return {
            "ok": False,
            "status": "not_enough_data",
            "method_id": "spearman_correlation",
            "sample_size": sample_size,
        }

    left_ranks = _rank_values(left_values)
    right_ranks = _rank_values(right_values)

    rho = _pearson_correlation(left_ranks, right_ranks)

    if rho is None:
        return {
            "ok": False,
            "status": "correlation_not_defined",
            "method_id": "spearman_correlation",
            "sample_size": sample_size,
        }
    p_result = spearman_permutation_p_value(
        left_ranks=left_ranks,
        right_ranks=right_ranks,
    )
    p_value = p_result["p_value"]
    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "spearman_correlation",
        "method_title": "Spearman rank correlation",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": sample_size,
        "test_statistic": rho,
        "test_statistic_name": "Spearman's ρ",
        "degrees_of_freedom": sample_size - 2,
        "alpha": 0.05,
        "p_value": p_value,
        "p_value_method": p_result["p_value_method"],
        "permutation_count": p_result.get("permutation_count"),
        "is_statistically_significant": (
            p_value is not None and p_value < 0.05
        ),
        "null_hypothesis": (
            "There is no monotonic association between the selected variables."
        ),
        "alternative_hypothesis": (
            "There is a monotonic association between the selected variables."
        ),
        "decision": (
            "Reject H₀"
            if p_value is not None and p_value < 0.05
            else "Fail to reject H₀"
        ),



        "results": {
            "spearman_rho": rho,
            "p_value": p_value,
        },
        "interpretation": {
            "summary": (
                "Spearman rank correlation was calculated using ranked paired "
                "responses from participants who answered both selected questions."
            ),
        },
    }
