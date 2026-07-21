def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _variance(values: list[float]) -> float | None:
    if len(values) < 2:
        return None

    mean_value = sum(values) / len(values)

    return sum(
        (value - mean_value) ** 2
        for value in values
    ) / (len(values) - 1)


def check_variance_assumption(
    *,
    groups: dict,
) -> dict:
    group_variances = {}

    for group_name, raw_values in groups.items():
        numeric_values = [
            _to_number(value)
            for value in raw_values
        ]

        numeric_values = [
            value
            for value in numeric_values
            if value is not None
        ]

        group_variances[group_name] = _variance(numeric_values)

    available_variances = [
        value
        for value in group_variances.values()
        if value is not None
    ]

    if len(available_variances) < 2:
        status = "blocked"
    else:
        min_variance = min(available_variances)
        max_variance = max(available_variances)

        if min_variance == 0:
            status = "warning"
        elif max_variance / min_variance <= 4:
            status = "passed"
        else:
            status = "warning"

    return {
        "check_id": "variance_assumption_checked",
        "status": status,
        "details": {
            "group_variances": group_variances,
            "rule": "warning if max/min variance ratio is greater than 4",
        },
    }