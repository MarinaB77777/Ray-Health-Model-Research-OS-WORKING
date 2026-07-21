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


def check_time_coverage(
    *,
    records: list[dict],
    minimum_duration_seconds: float,
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
        return {
            "check_id": "time_coverage",
            "status": "blocked",
            "details": {
                "timestamp_count": len(timestamps),
                "minimum_duration_seconds": minimum_duration_seconds,
            },
        }

    duration = (max(timestamps) - min(timestamps)).total_seconds()

    return {
        "check_id": "time_coverage",
        "status": "passed" if duration >= minimum_duration_seconds else "failed",
        "details": {
            "timestamp_count": len(timestamps),
            "duration_seconds": duration,
            "minimum_duration_seconds": minimum_duration_seconds,
        },
    }