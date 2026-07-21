def check_time_order_available(
    *,
    answer_records: list[dict],
) -> dict:
    timestamps = []

    for record in answer_records:
        timestamp = (
            record.get("answered_at")
            or record.get("created_at")
            or record.get("timestamp")
            or record.get("global_time")
        )

        if timestamp:
            timestamps.append(timestamp)

    unique_timestamps = set(timestamps)

    if not timestamps:
        status = "blocked"
    elif len(unique_timestamps) < 2:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "time_order_available",
        "status": status,
        "details": {
            "timestamp_count": len(timestamps),
            "unique_timestamp_count": len(unique_timestamps),
        },
    }