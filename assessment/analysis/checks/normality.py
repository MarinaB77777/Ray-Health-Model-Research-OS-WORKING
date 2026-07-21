def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check_approximately_normal_or_sufficient_sample(
    *,
    values: list,
    minimum_for_sample_size_assumption: int = 30,
) -> dict:
    numeric_values = [
        _to_number(value)
        for value in values
    ]

    numeric_values = [
        value
        for value in numeric_values
        if value is not None
    ]

    count = len(numeric_values)

    if count == 0:
        status = "blocked"
    elif count >= minimum_for_sample_size_assumption:
        status = "passed"
    elif count >= 3:
        status = "warning"
    else:
        status = "blocked"

    return {
        "check_id": "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
        "status": status,
        "details": {
            "numeric_count": count,
            "minimum_for_sample_size_assumption": minimum_for_sample_size_assumption,
            "note": "For small samples, real normality testing or visual inspection should be added before parametric methods.",
        },
    }