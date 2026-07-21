def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check_value_range(
    *,
    values: list,
    variable_name: str,
    minimum_allowed: float | None = None,
    maximum_allowed: float | None = None,
) -> dict:
    numeric_values = [
        _to_number(value)
        for value in values
        if value is not None and value != ""
    ]

    numeric_values = [
        value
        for value in numeric_values
        if value is not None
    ]

    if minimum_allowed is None and maximum_allowed is None:
        return {
            "check_id": "value_range",
            "status": "blocked",
            "details": {
                "variable_name": variable_name,
                "reason": "No allowed numeric range is defined.",
            },
        }

    out_of_range = []

    for value in numeric_values:
        if minimum_allowed is not None and value < minimum_allowed:
            out_of_range.append(value)

        if maximum_allowed is not None and value > maximum_allowed:
            out_of_range.append(value)

    return {
        "check_id": "value_range",
        "status": "passed" if not out_of_range else "failed",
        "details": {
            "variable_name": variable_name,
            "numeric_count": len(numeric_values),
            "minimum_allowed": minimum_allowed,
            "maximum_allowed": maximum_allowed,
            "out_of_range_count": len(out_of_range),
            "out_of_range_values": out_of_range,
        },
    }