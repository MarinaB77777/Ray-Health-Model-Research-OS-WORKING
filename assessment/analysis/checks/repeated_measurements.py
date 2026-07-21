def _participant_key(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("account_id")
    )


def check_repeated_measurements(
    *,
    answer_records: list[dict],
) -> dict:
    participant_session_counts = {}

    for record in answer_records:
        participant_key = _participant_key(record)
        session_id = record.get("session_id")

        if not participant_key or not session_id:
            continue

        if participant_key not in participant_session_counts:
            participant_session_counts[participant_key] = set()

        participant_session_counts[participant_key].add(session_id)

    repeated_participants = {
        participant: len(sessions)
        for participant, sessions in participant_session_counts.items()
        if len(sessions) > 1
    }

    if not participant_session_counts:
        status = "blocked"
    elif repeated_participants:
        status = "warning"
    else:
        status = "passed"

    return {
        "check_id": "repeated_measurements",
        "status": status,
        "details": {
            "participant_count": len(participant_session_counts),
            "repeated_participant_count": len(repeated_participants),
            "repeated_participants": repeated_participants,
            "note": "Warning means the dataset may contain repeated measurements and should not be treated as fully independent without explicit design handling.",
        },
    }