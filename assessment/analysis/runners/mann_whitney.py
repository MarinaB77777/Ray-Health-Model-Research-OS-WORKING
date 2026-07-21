from assessment.analysis.statistics.mann_whitney import (
    mann_whitney_u_statistic,
    mann_whitney_two_sided_p_value,
)


def _collect_grouped_values(
    answer_records: list[dict],
    group_question_code: str,
    value_question_code: str,
) -> dict[str, list[float]]:
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

        if question_code not in {group_question_code, value_question_code}:
            continue

        by_subject.setdefault(subject_id, {})[question_code] = record.get("answer_value")

    groups = {}

    for answers in by_subject.values():
        group_value = answers.get(group_question_code)
        outcome_value = answers.get(value_question_code)

        if (
            group_value is None
            or group_value == ""
            or outcome_value is None
            or outcome_value == ""
        ):
            continue

        try:
            numeric_outcome = float(outcome_value)
        except (TypeError, ValueError):
            continue

        group_key = str(group_value)
        groups.setdefault(group_key, []).append(numeric_outcome)

    return groups


def run_mann_whitney_u(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    groups = _collect_grouped_values(
        answer_records=answer_records,
        group_question_code=left_question_code,
        value_question_code=right_question_code,
    )

    if len(groups) != 2:
        groups = _collect_grouped_values(
            answer_records=answer_records,
            group_question_code=right_question_code,
            value_question_code=left_question_code,
        )

    if len(groups) != 2:
        return {
            "ok": False,
            "status": "two_groups_required",
            "method_id": "mann_whitney_u",
            "observed_group_count": len(groups),
        }

    group_names = sorted(groups.keys())
    group_1_name = group_names[0]
    group_2_name = group_names[1]

    group_1 = groups[group_1_name]
    group_2 = groups[group_2_name]

    n1 = len(group_1)
    n2 = len(group_2)

    if n1 < 1 or n2 < 1:
        return {
            "ok": False,
            "status": "not_enough_group_data",
            "method_id": "mann_whitney_u",
            "group_sizes": {
                group_1_name: n1,
                group_2_name: n2,
            },
        }

    u_result = mann_whitney_u_statistic(
        group_1=group_1,
        group_2=group_2,
    )

    p_result = mann_whitney_two_sided_p_value(
        u_min=u_result["u_min"],
        group_1=group_1,
        group_2=group_2,
    )

    p_value = p_result.get("p_value")
    alpha = 0.05

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "mann_whitney_u",
        "method_title": "Mann-Whitney U test",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": n1 + n2,
        "test_statistic": u_result["u_min"],
        "test_statistic_name": "Mann-Whitney U",
        "degrees_of_freedom": None,
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": (
            p_value is not None and p_value < alpha
        ),
        "null_hypothesis": (
            "The distributions of the outcome variable are the same in the two groups."
        ),
        "alternative_hypothesis": (
            "The distributions of the outcome variable differ between the two groups."
        ),
        "decision": (
            "Reject H₀"
            if p_value is not None and p_value < alpha
            else "Fail to reject H₀"
        ),
        "group_summary": {
            group_1_name: {
                "n": n1,
            },
            group_2_name: {
                "n": n2,
            },
        },
        "p_value_method": p_result.get("p_value_method"),
        "tie_correction_used": p_result.get("tie_correction_used"),
        "results": {
            "u_statistic": u_result["u_min"],
            "u1": u_result["u1"],
            "u2": u_result["u2"],
            "p_value": p_value,
        },
        "interpretation": {
            "summary": (
                "Mann-Whitney U test was calculated for two independent groups "
                "using the selected outcome variable."
            ),
        },
    }