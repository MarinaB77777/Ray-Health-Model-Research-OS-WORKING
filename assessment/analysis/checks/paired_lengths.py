def check_paired_lengths(
    *,
    left_values: list,
    right_values: list,
) -> dict:
    left_count = len([
        value
        for value in left_values
        if value is not None and value != ""
    ])

    right_count = len([
        value
        for value in right_values
        if value is not None and value != ""
    ])

    complete_pair_count = len([
        (left, right)
        for left, right in zip(left_values, right_values)
        if left is not None
        and left != ""
        and right is not None
        and right != ""
    ])

    if left_count == 0 or right_count == 0:
        status = "blocked"
    elif complete_pair_count == 0:
        status = "failed"
    elif left_count != right_count:
        status = "warning"
    else:
        status = "passed"

    return {
        "check_id": "paired_lengths",
        "status": status,
        "details": {
            "left_non_missing_count": left_count,
            "right_non_missing_count": right_count,
            "complete_pair_count": complete_pair_count,
        },
    }