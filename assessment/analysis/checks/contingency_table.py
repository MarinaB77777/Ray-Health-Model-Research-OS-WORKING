from collections import Counter


def build_contingency_table(
    *,
    left_values: list,
    right_values: list,
) -> dict:
    paired = [
        (left, right)
        for left, right in zip(left_values, right_values)
        if left is not None
        and left != ""
        and right is not None
        and right != ""
    ]

    left_levels = sorted(set(left for left, _ in paired))
    right_levels = sorted(set(right for _, right in paired))

    counts = Counter(paired)

    table = {
        str(left): {
            str(right): counts[(left, right)]
            for right in right_levels
        }
        for left in left_levels
    }

    return {
        "paired_count": len(paired),
        "left_levels": left_levels,
        "right_levels": right_levels,
        "table": table,
    }


def check_contingency_table(
    *,
    left_values: list,
    right_values: list,
) -> dict:
    table_data = build_contingency_table(
        left_values=left_values,
        right_values=right_values,
    )

    if table_data["paired_count"] == 0:
        status = "blocked"
    elif len(table_data["left_levels"]) < 2 or len(table_data["right_levels"]) < 2:
        status = "failed"
    else:
        status = "passed"

    return {
        "check_id": "contingency_table",
        "status": status,
        "details": table_data,
    }


def check_two_by_two_table(
    *,
    left_values: list,
    right_values: list,
) -> dict:
    table_data = build_contingency_table(
        left_values=left_values,
        right_values=right_values,
    )

    left_count = len(table_data["left_levels"])
    right_count = len(table_data["right_levels"])

    if table_data["paired_count"] == 0:
        status = "blocked"
    elif left_count == 2 and right_count == 2:
        status = "passed"
    else:
        status = "failed"

    return {
        "check_id": "two_by_two_table",
        "status": status,
        "details": {
            **table_data,
            "left_level_count": left_count,
            "right_level_count": right_count,
        },
    }