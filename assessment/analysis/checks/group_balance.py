from collections import Counter


def check_group_balance(
    *,
    group_values: list,
    max_ratio: float = 4.0,
) -> dict:
    non_missing = [
        value
        for value in group_values
        if value is not None and value != ""
    ]

    groups = Counter(non_missing)

    if len(groups) < 2:
        status = "blocked"
        ratio = None
    else:
        counts = list(groups.values())
        minimum = min(counts)
        maximum = max(counts)

        if minimum == 0:
            status = "blocked"
            ratio = None
        else:
            ratio = maximum / minimum
            status = "passed" if ratio <= max_ratio else "warning"

    return {
        "check_id": "group_balance",
        "status": status,
        "details": {
            "groups": dict(groups),
            "max_ratio_allowed": max_ratio,
            "observed_ratio": ratio,
        },
    }
