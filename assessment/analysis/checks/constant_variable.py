def check_not_constant_variable(
    *,
    values: list,
    variable_name: str,
) -> dict:
    non_missing = [
        value
        for value in values
        if value is not None and value != ""
    ]

    unique_values = set(non_missing)

    if len(non_missing) == 0:
        status = "blocked"
    elif len(unique_values) < 2:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "not_constant_variable",
        "status": status,
        "details": {
            "variable_name": variable_name,
            "non_missing_count": len(non_missing),
            "unique_count": len(unique_values),
            "unique_values": list(unique_values),
        },
    }