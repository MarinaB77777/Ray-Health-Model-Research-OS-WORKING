def check_global_time_reference_present(
    *,
    answer_records: list[dict],
) -> dict:
    total = len(answer_records)

    with_global_time = [
        record
        for record in answer_records
        if record.get("global_time")
        or record.get("global_timestamp")
        or record.get("shared_timestamp")
    ]

    if total == 0:
        status = "blocked"
    elif len(with_global_time) == total:
        status = "passed"
    elif len(with_global_time) > 0:
        status = "warning"
    else:
        status = "failed"

    return {
        "check_id": "global_time_reference_present",
        "status": status,
        "details": {
            "record_count": total,
            "records_with_global_time": len(with_global_time),
            "records_missing_global_time": total - len(with_global_time),
            "note": "Global/shared time reference is required for sensor alignment, longitudinal analysis, and cross-source synchronization.",
        },
    }