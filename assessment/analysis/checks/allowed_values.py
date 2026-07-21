def check_allowed_values(
    *,
    values: list,
    allowed_values: list | None,
    variable_name: str,
) -> dict:
    non_missing = [
        value
        for value in values
        if value is not None and value != ""
    ]

    if allowed_values is None:
        return {
            "check_id": "allowed_values",
            "status": "blocked",
            "details": {
                "variable_name": variable_name,
                "reason": "allowed_values is not defined",
            },
        }

    allowed_as_strings = set(str(value) for value in allowed_values)

    invalid_values = [
        value
        for value in non_missing
        if str(value) not in allowed_as_strings
    ]

    return {
        "check_id": "allowed_values",
        "status": "passed" if not invalid_values else "failed",
        "details": {
            "variable_name": variable_name,
            "allowed_values": allowed_values,
            "invalid_count": len(invalid_values),
            "invalid_values": invalid_values,
        },
    }