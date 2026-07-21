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


def check_sampling_interval_consistency(
    *,
    records: list[dict],
    max_interval_ratio: float = 2.0,
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

    timestamps = sorted(timestamps)

    if len(timestamps) < 3:
        return {
            "check_id": "sampling_interval_consistency",
            "status": "blocked",
            "details": {
                "timestamp_count": len(timestamps),
                "reason": "At least 3 timestamps are required to check interval consistency.",
            },
        }

    intervals = [
        (timestamps[index] - timestamps[index - 1]).total_seconds()
        for index in range(1, len(timestamps))
    ]

    positive_intervals = [
        interval
        for interval in intervals
        if interval > 0
    ]

    if not positive_intervals:
        status = "failed"
        ratio = None
    else:
        minimum = min(positive_intervals)
        maximum = max(positive_intervals)
        ratio = maximum / minimum if minimum > 0 else None

        status = (
            "passed"
            if ratio is not None and ratio <= max_interval_ratio
            else "warning"
        )

    return {
        "check_id": "sampling_interval_consistency",
        "status": status,
        "details": {
            "timestamp_count": len(timestamps),
            "intervals_seconds": intervals,
            "max_interval_ratio_allowed": max_interval_ratio,
            "observed_interval_ratio": ratio,
        },
    }