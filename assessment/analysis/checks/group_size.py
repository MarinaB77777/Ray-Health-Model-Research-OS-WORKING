from collections import Counter


def check_minimum_group_size(
    *,
    group_values: list,
    minimum_per_group: int = 2,
) -> dict:
    non_missing = [
        value
        for value in group_values
        if value is not None and value != ""
    ]

    groups = Counter(non_missing)

    small_groups = {
        group: count
        for group, count in groups.items()
        if count < minimum_per_group
    }

    if not groups:
        status = "blocked"
    elif small_groups:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "minimum_group_size",
        "status": status,
        "details": {
            "minimum_per_group": minimum_per_group,
            "groups": dict(groups),
            "small_groups": small_groups,
        },
    }
