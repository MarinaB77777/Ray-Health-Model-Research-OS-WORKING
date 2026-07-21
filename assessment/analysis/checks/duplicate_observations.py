from collections import Counter


def _observation_key(record: dict) -> tuple:
    return (
        record.get("participant_id"),
        record.get("subject_link_id"),
        record.get("session_id"),
        record.get("question_code"),
    )


def check_duplicate_observations(
    *,
    answer_records: list[dict],
) -> dict:
    keys = [
        _observation_key(record)
        for record in answer_records
        if record.get("question_code")
    ]

    counts = Counter(keys)

    duplicates = {
        str(key): count
        for key, count in counts.items()
        if count > 1
    }

    if not keys:
        status = "blocked"
    elif duplicates:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "duplicate_observations",
        "status": status,
        "details": {
            "observation_count": len(keys),
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
        },
    }