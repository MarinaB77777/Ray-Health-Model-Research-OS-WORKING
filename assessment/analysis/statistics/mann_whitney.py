import math
from collections import Counter


def normal_cdf(value: float) -> float:
    return 0.5 * math.erfc(-value / math.sqrt(2.0))


def rank_values(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)

    i = 0
    while i < len(indexed):
        j = i

        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1

        average_rank = (i + 1 + j + 1) / 2.0

        for k in range(i, j + 1):
            ranks[indexed[k][0]] = average_rank

        i = j + 1

    return ranks


def has_ties(values: list[float]) -> bool:
    return any(count > 1 for count in Counter(values).values())


def mann_whitney_u_statistic(
    group_1: list[float],
    group_2: list[float],
) -> dict:
    combined = group_1 + group_2
    ranks = rank_values(combined)

    n1 = len(group_1)
    n2 = len(group_2)

    rank_sum_1 = sum(ranks[:n1])
    u1 = rank_sum_1 - (n1 * (n1 + 1) / 2.0)
    u2 = n1 * n2 - u1

    return {
        "u1": u1,
        "u2": u2,
        "u_min": min(u1, u2),
        "rank_sum_1": rank_sum_1,
    }


def _exact_u_distribution_counts(n1: int, n2: int) -> dict[int, int]:
    total_n = n1 + n2
    min_rank_sum = n1 * (n1 + 1) // 2

    dp = {
        (0, 0): 1,
    }

    for rank in range(1, total_n + 1):
        next_dp = dict(dp)

        for (k, rank_sum), count in dp.items():
            if k >= n1:
                continue

            key = (k + 1, rank_sum + rank)
            next_dp[key] = next_dp.get(key, 0) + count

        dp = next_dp

    counts = {}

    for (k, rank_sum), count in dp.items():
        if k != n1:
            continue

        u = rank_sum - min_rank_sum
        counts[u] = counts.get(u, 0) + count

    return counts


def mann_whitney_exact_two_sided_p_value(
    *,
    u_min: float,
    n1: int,
    n2: int,
) -> float:
    counts = _exact_u_distribution_counts(n1, n2)
    total = math.comb(n1 + n2, n1)

    observed = int(round(u_min))

    lower_tail_count = sum(
        count
        for u, count in counts.items()
        if u <= observed
    )

    p_value = 2.0 * lower_tail_count / total

    return min(1.0, p_value)


def mann_whitney_asymptotic_two_sided_p_value(
    *,
    u_min: float,
    group_1: list[float],
    group_2: list[float],
) -> float | None:
    n1 = len(group_1)
    n2 = len(group_2)
    total_n = n1 + n2

    if n1 == 0 or n2 == 0 or total_n < 2:
        return None

    mean_u = n1 * n2 / 2.0

    tie_counts = Counter(group_1 + group_2)

    tie_correction = sum(
        count ** 3 - count
        for count in tie_counts.values()
        if count > 1
    )

    variance = (
        n1 * n2 / 12.0
        * (
            total_n + 1
            - tie_correction / (total_n * (total_n - 1))
        )
    )

    if variance <= 0:
        return None

    sd = math.sqrt(variance)

    if u_min < mean_u:
        z = (u_min - mean_u + 0.5) / sd
    elif u_min > mean_u:
        z = (u_min - mean_u - 0.5) / sd
    else:
        z = 0.0

    lower_tail = normal_cdf(z)
    upper_tail = 1.0 - lower_tail

    return min(1.0, 2.0 * min(lower_tail, upper_tail))


def mann_whitney_two_sided_p_value(
    *,
    u_min: float,
    group_1: list[float],
    group_2: list[float],
) -> dict:
    n1 = len(group_1)
    n2 = len(group_2)
    tied = has_ties(group_1 + group_2)

    if not tied and n1 <= 20 and n2 <= 20:
        return {
            "p_value": mann_whitney_exact_two_sided_p_value(
                u_min=u_min,
                n1=n1,
                n2=n2,
            ),
            "p_value_method": "exact",
            "tie_correction_used": False,
        }

    return {
        "p_value": mann_whitney_asymptotic_two_sided_p_value(
            u_min=u_min,
            group_1=group_1,
            group_2=group_2,
        ),
        "p_value_method": "asymptotic_normal_approximation",
        "tie_correction_used": tied,
    }