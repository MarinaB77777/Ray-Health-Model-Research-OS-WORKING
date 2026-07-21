def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _percentile(sorted_values: list[float], percentile: float) -> float | None:
    if not sorted_values:
        return None

    position = (len(sorted_values) - 1) * percentile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    weight = position - lower_index

    return (
        sorted_values[lower_index] * (1 - weight)
        + sorted_values[upper_index] * weight
    )


def check_extreme_outliers_iqr(
    *,
    values: list,
    iqr_multiplier: float = 3.0,
) -> dict:
    numeric_values = [
        _to_number(value)
        for value in values
    ]

    numeric_values = sorted(
        value
        for value in numeric_values
        if value is not None
    )

    count = len(numeric_values)

    if count < 4:
        return {
            "check_id": "no_extreme_outliers",
            "status": "blocked",
            "details": {
                "numeric_count": count,
                "reason": "IQR outlier check requires at least 4 numeric values.",
            },
        }

    q1 = _percentile(numeric_values, 0.25)
    q3 = _percentile(numeric_values, 0.75)
    iqr = q3 - q1

    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr

    outliers = [
        value
        for value in numeric_values
        if value < lower_bound or value > upper_bound
    ]

    return {
        "check_id": "no_extreme_outliers",
        "status": "passed" if len(outliers) == 0 else "warning",
        "details": {
            "numeric_count": count,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "iqr_multiplier": iqr_multiplier,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": len(outliers),
            "outliers": outliers,
        },
    }