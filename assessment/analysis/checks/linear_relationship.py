def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check_linear_relationship_plausible(
    *,
    left_values: list,
    right_values: list,
    minimum_pairs: int = 3,
) -> dict:
    numeric_pairs = []

    for left, right in zip(left_values, right_values):
        left_number = _to_number(left)
        right_number = _to_number(right)

        if left_number is not None and right_number is not None:
            numeric_pairs.append((left_number, right_number))

    left_unique = len(set(pair[0] for pair in numeric_pairs))
    right_unique = len(set(pair[1] for pair in numeric_pairs))

    if len(numeric_pairs) < minimum_pairs:
        status = "blocked"
    elif left_unique < 2 or right_unique < 2:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "linear_relationship_plausible",
        "status": status,
        "details": {
            "numeric_pair_count": len(numeric_pairs),
            "minimum_pairs": minimum_pairs,
            "left_unique_values": left_unique,
            "right_unique_values": right_unique,
            "note": "This is a basic plausibility check; visual inspection or residual diagnostics may be added later.",
        },
    }