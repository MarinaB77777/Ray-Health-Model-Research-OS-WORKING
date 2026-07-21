def check_missing_values(
    *,
    values: list,
    variable_name: str,
    warning_threshold: float = 0.1,
    fail_threshold: float = 0.3,
) -> dict:
    total_count = len(values)

    missing_count = len([
        value
        for value in values
        if value is None or value == ""
    ])

    if total_count == 0:
        status = "blocked"
        missing_rate = None
    else:
        missing_rate = missing_count / total_count

        if missing_rate >= fail_threshold:
            status = "failed"
        elif missing_rate >= warning_threshold:
            status = "warning"
        else:
            status = "passed"

    return {
        "check_id": "missing_values",
        "status": status,
        "details": {
            "variable_name": variable_name,
            "total_count": total_count,
            "missing_count": missing_count,
            "missing_rate": missing_rate,
            "warning_threshold": warning_threshold,
            "fail_threshold": fail_threshold,
        },
    }