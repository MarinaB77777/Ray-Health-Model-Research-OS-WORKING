def _is_numeric(value) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def check_numeric_data(
    *,
    values: list,
    variable_name: str,
) -> dict:
    non_missing = [
        value
        for value in values
        if value is not None and value != ""
    ]

    numeric_count = sum(
        1 for value in non_missing
        if _is_numeric(value)
    )

    total = len(non_missing)

    if total == 0:
        status = "blocked"
    elif numeric_count == total:
        status = "passed"
    else:
        status = "failed"

    return {
        "check_id": "numeric_data",
        "status": status,
        "details": {
            "variable_name": variable_name,
            "non_missing_count": total,
            "numeric_count": numeric_count,
            "non_numeric_count": total - numeric_count,
        },
    }