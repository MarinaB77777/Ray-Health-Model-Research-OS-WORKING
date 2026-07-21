def _participant_key(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("session_id")
        or record.get("record_id")
    )


def check_independent_observations(
    *,
    answer_records: list[dict],
) -> dict:
    keys = []

    for record in answer_records:
        key = _participant_key(record)

        if key:
            keys.append(key)

    unique_count = len(set(keys))
    total_count = len(keys)

    repeated_count = total_count - unique_count

    if total_count == 0:
        status = "blocked"
    elif repeated_count == 0:
        status = "passed"
    else:
        status = "warning"

    return {
        "check_id": "independent_observations",
        "status": status,
        "details": {
            "total_observation_keys": total_count,
            "unique_observation_keys": unique_count,
            "repeated_observation_keys": repeated_count,
            "note": "Warning means repeated records exist; repeated-measure/session structure may need explicit handling.",
        },
    }