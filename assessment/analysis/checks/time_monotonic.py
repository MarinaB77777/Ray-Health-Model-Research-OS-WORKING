from datetime import datetime


def _parse_time(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def check_time_is_monotonic(
    *,
    records: list[dict],
) -> dict:
    timestamps = []

    for record in records:
        raw_time = (
            record.get("global_time")
            or record.get("global_timestamp")
            or record.get("shared_timestamp")
            or record.get("timestamp")
            or record.get("created_at")
        )

        parsed = _parse_time(raw_time)

        if parsed:
            timestamps.append(parsed)

    if len(timestamps) < 2:
        status = "blocked"
        backward_jumps = 0
    else:
        backward_jumps = sum(
            1
            for index in range(1, len(timestamps))
            if timestamps[index] < timestamps[index - 1]
        )

        status = "passed" if backward_jumps == 0 else "failed"

    return {
        "check_id": "time_is_monotonic",
        "status": status,
        "details": {
            "timestamp_count": len(timestamps),
            "backward_jump_count": backward_jumps,
        },
    }