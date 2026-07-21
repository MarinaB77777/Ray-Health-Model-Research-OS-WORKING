def _participant_key(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("session_id")
        or record.get("record_id")
    )


def _paired_values(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> list[tuple]:
    by_subject = {}

    for record in answer_records:
        key = _participant_key(record)

        if not key:
            continue

        if key not in by_subject:
            by_subject[key] = {}

        code = record.get("question_code")
        value = record.get("answer_value")

        if value is None or value == "":
            continue

        if code == left_question_code:
            by_subject[key]["left"] = value

        if code == right_question_code:
            by_subject[key]["right"] = value

    pairs = []

    for values in by_subject.values():
        if "left" in values and "right" in values:
            pairs.append((values["left"], values["right"]))

    return pairs


def check_monotonic_relationship_plausible(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
    minimum_pairs: int = 3,
) -> dict:
    pairs = _paired_values(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )

    left_unique = len(set(pair[0] for pair in pairs))
    right_unique = len(set(pair[1] for pair in pairs))

    if len(pairs) < minimum_pairs:
        status = "blocked"
    elif left_unique < 2 or right_unique < 2:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "monotonic_relationship_plausible",
        "status": status,
        "details": {
            "paired_count": len(pairs),
            "minimum_pairs": minimum_pairs,
            "left_unique_values": left_unique,
            "right_unique_values": right_unique,
        },
    }