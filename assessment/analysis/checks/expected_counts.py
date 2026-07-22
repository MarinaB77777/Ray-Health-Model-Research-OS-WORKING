from collections import Counter


def check_expected_cell_counts(
    *,
    left_values: list | None = None,
    right_values: list | None = None,
    table: list[list[int]] | None = None,
    minimum_expected: float = 5.0,
) -> dict:
    if table is not None:
        if len(table) < 2 or any(len(row) < 2 for row in table):
            paired = []
        else:
            row_totals = [sum(row) for row in table]
            column_totals = [sum(row[index] for row in table) for index in range(len(table[0]))]
            total = sum(row_totals)
            expected = {}
            minimum = None
            below_five = 0
            expected_count_total = len(row_totals) * len(column_totals)
            for row_index, row_n in enumerate(row_totals):
                for column_index, column_n in enumerate(column_totals):
                    expected_count = row_n * column_n / total if total else 0.0
                    expected[f"{row_index} × {column_index}"] = expected_count
                    minimum = expected_count if minimum is None else min(minimum, expected_count)
                    if expected_count < minimum_expected:
                        below_five += 1
            below_fraction = below_five / expected_count_total if expected_count_total else 1.0
            passed = minimum is not None and minimum >= 1.0 and below_fraction <= 0.20
            return {
                "check_id": "expected_cell_counts",
                "status": "passed" if passed else "failed",
                "details": {
                    "minimum_expected_count": minimum,
                    "cells_below_five": below_five,
                    "fraction_below_five": below_fraction,
                    "rule": "no expected count below 1 and at most 20% below 5",
                    "expected_counts": expected,
                },
            }

    left_values = left_values or []
    right_values = right_values or []
    paired = [
        (left, right)
        for left, right in zip(left_values, right_values)
        if left is not None and left != "" and right is not None and right != ""
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
