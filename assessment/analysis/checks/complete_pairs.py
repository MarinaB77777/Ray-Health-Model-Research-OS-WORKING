def check_minimum_complete_pairs(
    *,
    left_values: list,
    right_values: list,
    minimum_required: int = 3,
) -> dict:
    complete_pairs = [
        (left, right)
        for left, right in zip(left_values, right_values)
        if left is not None
        and left != ""
        and right is not None
        and right != ""
    ]

    count = len(complete_pairs)

    return {
        "check_id": "minimum_complete_pairs",
        "status": "passed" if count >= minimum_required else "failed",
        "details": {
            "complete_pair_count": count,
            "minimum_required": minimum_required,
        },
    }