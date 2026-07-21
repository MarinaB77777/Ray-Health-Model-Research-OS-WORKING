def check_ordinal_order_defined(
    *,
    options: list | None,
    variable_name: str,
) -> dict:
    if not options:
        return {
            "check_id": "ordinal_order_defined",
            "status": "blocked",
            "details": {
                "variable_name": variable_name,
                "reason": "No options are defined.",
            },
        }

    values = [
        option.get("value")
        for option in options
        if isinstance(option, dict)
    ]

    numeric_values = []

    for value in values:
        try:
            numeric_values.append(float(value))
        except (TypeError, ValueError):
            pass

    if len(numeric_values) != len(values):
        status = "failed"
    elif len(set(numeric_values)) != len(numeric_values):
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "ordinal_order_defined",
        "status": status,
        "details": {
            "variable_name": variable_name,
            "option_count": len(options),
            "numeric_ordered_value_count": len(numeric_values),
            "unique_numeric_value_count": len(set(numeric_values)),
        },
    }