import math


def log_combination(
    n: int,
    k: int,
) -> float:
    if k < 0 or k > n:
        return float("-inf")

    return (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
    )


def hypergeometric_probability(
    *,
    a: int,
    row1: int,
    row2: int,
    col1: int,
    col2: int,
) -> float:
    total = row1 + row2

    log_p = (
        log_combination(row1, a)
        + log_combination(row2, col1 - a)
        - log_combination(total, col1)
    )

    return math.exp(log_p)