from assessment.analysis.statistics.fisher_exact import (
    fisher_exact_two_sided_p_value,
)
from assessment.analysis.statistics.grouping import (
    subject_id_from_record,
)


def _collect_contingency_table_2x2(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> dict | None:
    by_subject = {}
    duplicate_values = []

    for record in answer_records:
        subject_id = subject_id_from_record(record)
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

    observed_left_values = []
    observed_right_values = []

    paired_values = []

    for answers in by_subject.values():
        left_value = answers.get(left_question_code)
        right_value = answers.get(right_question_code)

        if (
            left_value is None
            or left_value == ""
            or right_value is None
            or right_value == ""
        ):
            continue

        left_key = str(left_value)
        right_key = str(right_value)

        paired_values.append((left_key, right_key))
        observed_left_values.append(left_key)
        observed_right_values.append(right_key)

    left_categories = sorted(set(observed_left_values))
    right_categories = sorted(set(observed_right_values))

    if len(left_categories) != 2 or len(right_categories) != 2:
        return None

    table = {
        left_categories[0]: {
            right_categories[0]: 0,
            right_categories[1]: 0,
        },
        left_categories[1]: {
            right_categories[0]: 0,
            right_categories[1]: 0,
        },
    }

    for left_key, right_key in paired_values:
        table[left_key][right_key] += 1

    a = table[left_categories[0]][right_categories[0]]
    b = table[left_categories[0]][right_categories[1]]
    c = table[left_categories[1]][right_categories[0]]
    d = table[left_categories[1]][right_categories[1]]

    return {
        "left_categories": left_categories,
        "right_categories": right_categories,
        "table": [
            [a, b],
            [c, d],
        ],
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "sample_size": len(paired_values),
    }


def run_fisher_exact(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    contingency = _collect_contingency_table_2x2(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )

    if contingency is None:
        return {
            "ok": False,
            "status": "two_by_two_table_required",
            "method_id": "fisher_exact",
        }
    if contingency.get("ok") is False:
        return {"method_id": "fisher_exact", **contingency}

    result = fisher_exact_two_sided_p_value(
        a=contingency["a"],
        b=contingency["b"],
        c=contingency["c"],
        d=contingency["d"],
    )

    p_value = result["p_value"]
    alpha = 0.05

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "fisher_exact",
        "method_title": "Fisher exact test",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": contingency["sample_size"],
        "test_statistic": result["odds_ratio"],
        "test_statistic_name": "Odds ratio",
        "degrees_of_freedom": None,
        "alpha": alpha,
        "p_value": p_value,
        "p_value_method": "exact_conditional_hypergeometric",
        "is_statistically_significant": (
            p_value is not None and p_value < alpha
        ),
        "null_hypothesis": (
            "There is no association between the two binary categorical variables."
        ),
        "alternative_hypothesis": (
            "There is an association between the two binary categorical variables."
        ),
        "decision": (
            "Reject H₀"
            if p_value is not None and p_value < alpha
            else "Fail to reject H₀"
        ),
        "contingency_table": contingency,
        "results": {
            "odds_ratio": result["odds_ratio"],
            "p_value": p_value,
            "table": result["table"],
        },
        "interpretation": {
            "summary": (
                "Fisher exact test was calculated for a 2×2 contingency table "
                "formed from paired categorical responses."
            ),
        },
    }
