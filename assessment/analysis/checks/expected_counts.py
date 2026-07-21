from collections import Counter


def check_expected_cell_counts(
    *,
    left_values: list,
    right_values: list,
    minimum_expected: float = 5.0,
) -> dict:
    paired = [
        (left, right)
        for left, right in zip(left_values, right_values)
        if left is not None
        and left != ""
        and right is not None
        and right != ""
    ]

    if not paired:
        return {
            "check_id": "expected_cell_counts",
            "status": "blocked",
            "details": {"reason": "No paired observations."},
        }

    left_counts = Counter(left for left, _ in paired)
    right_counts = Counter(right for _, right in paired)
    total = len(paired)
    expected = {}
    minimum = None

    for left_group, left_n in left_counts.items():
        for right_group, right_n in right_counts.items():
            expected_count = left_n * right_n / total
            expected[f"{left_group} × {right_group}"] = expected_count
            if minimum is None or expected_count < minimum:
                minimum = expected_count

    # A low expected cell count is a failed chi-square assumption, not a
    # cosmetic warning. The method selector can then offer Fisher's exact test
    # when the table is 2×2.
    status = (
        "passed"
        if minimum is not None and minimum >= minimum_expected
        else "failed"
    )
    return {
        "check_id": "expected_cell_counts",
        "status": status,
        "details": {
            "minimum_expected_count": minimum,
            "required_minimum": minimum_expected,
            "expected_counts": expected,
        },
    }
