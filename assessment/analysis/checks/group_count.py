from collections import Counter


def check_two_groups(
    *,
    values: list,
    variable_side: str,
) -> dict:
    groups = Counter(values)
    group_count = len(groups)

    return {
        "check_id": "two_groups",
        "status": "passed" if group_count == 2 else "failed",
        "details": {
            "variable_side": variable_side,
            "group_count": group_count,
            "groups": dict(groups),
        },
    }


def check_three_or_more_groups(
    *,
    values: list,
    variable_side: str,
) -> dict:
    groups = Counter(values)
    group_count = len(groups)

    return {
        "check_id": "three_or_more_groups",
        "status": "passed" if group_count >= 3 else "failed",
        "details": {
            "variable_side": variable_side,
            "group_count": group_count,
            "groups": dict(groups),
        },
    }