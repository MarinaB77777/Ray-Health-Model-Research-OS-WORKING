def _participant_key(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("session_id")
        or record.get("record_id")
    )


def check_paired_observations(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> dict:
    left_subjects = set()
    right_subjects = set()

    for record in answer_records:
        key = _participant_key(record)

        if not key:
            continue

        if record.get("question_code") == left_question_code:
            if record.get("answer_value") is not None and record.get("answer_value") != "":
                left_subjects.add(key)

        if record.get("question_code") == right_question_code:
            if record.get("answer_value") is not None and record.get("answer_value") != "":
                right_subjects.add(key)

    paired_subjects = left_subjects.intersection(right_subjects)

    return {
        "check_id": "paired_observations",
        "status": "passed" if len(paired_subjects) > 0 else "failed",
        "details": {
            "left_subject_count": len(left_subjects),
            "right_subject_count": len(right_subjects),
            "paired_subject_count": len(paired_subjects),
        },
    }