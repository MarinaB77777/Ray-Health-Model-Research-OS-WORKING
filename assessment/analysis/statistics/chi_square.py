from assessment.analysis.statistics.chi_square_distribution import (
    chi_square_survival_function,
)


def chi_square_test_of_independence(
    *,
    table: list[list[int]],
) -> dict:
    row_count = len(table)

    if row_count < 2:
        return {
            "ok": False,
            "status": "at_least_two_rows_required",
        }

    column_count = len(table[0]) if table else 0

    if column_count < 2:
        return {
            "ok": False,
            "status": "at_least_two_columns_required",
        }

    row_totals = [
        sum(row)
        for row in table
    ]

    column_totals = [
        sum(table[row_index][column_index] for row_index in range(row_count))
        for column_index in range(column_count)
    ]

    total = sum(row_totals)

    if total == 0:
        return {
            "ok": False,
            "status": "empty_contingency_table",
        }

    chi_square = 0.0
    expected = []

    for row_index in range(row_count):
        expected_row = []

        for column_index in range(column_count):
            expected_count = (
                row_totals[row_index]
                * column_totals[column_index]
                / total
            )

            expected_row.append(expected_count)

            if expected_count > 0:
                observed = table[row_index][column_index]
                chi_square += (
                    (observed - expected_count) ** 2
                    / expected_count
                )

        expected.append(expected_row)

    degrees_of_freedom = (
        (row_count - 1)
        * (column_count - 1)
    )

    p_value = chi_square_survival_function(
        chi_square=chi_square,
        degrees_of_freedom=degrees_of_freedom,
    )

    alpha = 0.05

    return {
        "ok": True,
        "status": "completed",
        "test_statistic": chi_square,
        "test_statistic_name": "χ²",
        "degrees_of_freedom": degrees_of_freedom,
        "p_value": p_value,
        "alpha": alpha,
        "is_statistically_significant": (
            p_value is not None
            and p_value < alpha
        ),
        "decision": (
            "Reject H₀"
            if p_value is not None and p_value < alpha
            else "Fail to reject H₀"
        ),
        "expected_counts": expected,
        "row_totals": row_totals,
        "column_totals": column_totals,
        "total": total,
    }