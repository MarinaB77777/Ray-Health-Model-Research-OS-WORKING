def values_for_question(
    answer_records: list[dict],
    question_code: str,
) -> list:
    return [
        record.get("answer_value")
        for record in answer_records
        if record.get("question_code") == question_code
    ]


def non_missing_values(values: list) -> list:
    return [
        value
        for value in values
        if value is not None and value != ""
    ]


def check_variable_has_data(
    *,
    question_code: str,
    answer_records: list[dict],
    side: str,
) -> dict:
    values = values_for_question(
        answer_records,
        question_code,
    )

    non_missing = non_missing_values(values)

    return {
        "check_id": f"{side}_variable_has_data",
        "status": "passed" if len(non_missing) > 0 else "failed",
        "details": {
            "question_code": question_code,
            "total_count": len(values),
            "non_missing_count": len(non_missing),
            "missing_count": len(values) - len(non_missing),
        },
    }