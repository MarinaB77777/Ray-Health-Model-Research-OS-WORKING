from assessment.analysis.statistics.ranking import (
    rank_values,
    tie_correction_term,
)
from assessment.analysis.statistics.chi_square_distribution import (
    chi_square_survival_function,
)


def kruskal_wallis_test(
    *,
    groups: dict[str, list[float]],
) -> dict:
    if len(groups) < 3:
        return {
            "ok": False,
            "status": "three_groups_required",
        }

    all_values = []
    group_sizes = {}
    group_order = []

    for group_name, values in groups.items():
        group_order.append(group_name)
        group_sizes[group_name] = len(values)

        for value in values:
            all_values.append(
                (
                    group_name,
                    float(value),
                )
            )

    n = len(all_values)

    if n < 3:
        return {
            "ok": False,
            "status": "not_enough_data",
        }

    numeric_values = [
        value
        for _, value in all_values
    ]

    ranks = rank_values(numeric_values)

    rank_sums = {
        name: 0.0
        for name in group_order
    }

    for (group_name, _), rank in zip(all_values, ranks):
        rank_sums[group_name] += rank

    h = 0.0

    for group_name in group_order:
        ni = group_sizes[group_name]
        ri = rank_sums[group_name]

        h += (ri * ri) / ni

    h *= 12.0 / (n * (n + 1))
    h -= 3.0 * (n + 1)
    

    tie_term = tie_correction_term(numeric_values)

    if tie_term > 0:
        correction = 1.0 - (
            tie_term /
            (n ** 3 - n)
        )

        if correction <= 0:
            return {
                "ok": False,
                "status": "invalid_tie_correction",
            }

        h /= correction

    degrees_of_freedom = len(groups) - 1

    p_value = chi_square_survival_function(
        chi_square=h,
        degrees_of_freedom=degrees_of_freedom,
    )

    alpha = 0.05

    return {
        "ok": True,
        "status": "completed",
        "test_statistic": h,
        "test_statistic_name": "Kruskal-Wallis H",
        "degrees_of_freedom": degrees_of_freedom,
        "p_value": p_value,
        "p_value_method": "chi_square_asymptotic_with_tie_correction",
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
        "group_sizes": group_sizes,
    }
