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


def _time_bounds(records: list[dict]) -> tuple:
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

    if not timestamps:
        return None, None

    return min(timestamps), max(timestamps)


def check_time_overlap(
    *,
    left_records: list[dict],
    right_records: list[dict],
) -> dict:
    left_start, left_end = _time_bounds(left_records)
    right_start, right_end = _time_bounds(right_records)

    if not left_start or not right_start:
        status = "blocked"
        overlap_seconds = None
    else:
        overlap_start = max(left_start, right_start)
        overlap_end = min(left_end, right_end)

        overlap_seconds = max(
            0,
            (overlap_end - overlap_start).total_seconds()
        )

        status = "passed" if overlap_seconds > 0 else "failed"

    return {
        "check_id": "time_overlap",
        "status": status,
        "details": {
            "left_start": left_start.isoformat() if left_start else None,
            "left_end": left_end.isoformat() if left_end else None,
            "right_start": right_start.isoformat() if right_start else None,
            "right_end": right_end.isoformat() if right_end else None,
            "overlap_seconds": overlap_seconds,
        },
    }