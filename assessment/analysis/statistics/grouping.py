def subject_id_from_record(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("session_id")
        or record.get("parent_record_id")
    )


def collect_grouped_numeric_values(
    *,
    answer_records: list[dict],
    group_question_code: str,
    value_question_code: str,
) -> dict[str, list[float]]:
    by_subject = {}

    for record in answer_records:
        subject_id = subject_id_from_record(record)
        question_code = record.get("question_code")

        if not subject_id:
            continue

        if question_code not in {group_question_code, value_question_code}:
            continue

        by_subject.setdefault(subject_id, {})[question_code] = record.get("answer_value")

    groups = {}

    for answers in by_subject.values():
        group_value = answers.get(group_question_code)
        numeric_value = answers.get(value_question_code)

        if (
            group_value is None
            or group_value == ""
            or numeric_value is None
            or numeric_value == ""
        ):
            continue

        try:
            numeric_value = float(numeric_value)
        except (TypeError, ValueError):
            continue

        groups.setdefault(str(group_value), []).append(numeric_value)

    return groups


def collect_grouped_numeric_values_bidirectional(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> dict[str, list[float]]:
    groups = collect_grouped_numeric_values(
        answer_records=answer_records,
        group_question_code=left_question_code,
        value_question_code=right_question_code,
    )

    if len(groups) >= 2:
        return groups

    return collect_grouped_numeric_values(
        answer_records=answer_records,
        group_question_code=right_question_code,
        value_question_code=left_question_code,
    )