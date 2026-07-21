from assessment.analysis.statistics.hypergeometric import (
    hypergeometric_probability,
)


def fisher_exact_two_sided_p_value(
    *,
    a: int,
    b: int,
    c: int,
    d: int,
) -> dict:
    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d

    min_a = max(0, col1 - row2)
    max_a = min(row1, col1)

    observed_probability = hypergeometric_probability(
        a=a,
        row1=row1,
        row2=row2,
        col1=col1,
        col2=col2,
    )

    p_value = 0.0

    for possible_a in range(min_a, max_a + 1):
        probability = hypergeometric_probability(
            a=possible_a,
            row1=row1,
            row2=row2,
            col1=col1,
            col2=col2,
        )

        if probability <= observed_probability + 1e-12:
            p_value += probability

    odds_ratio = None

    if b * c != 0:
        odds_ratio = (a * d) / (b * c)

    return {
        "p_value": min(1.0, p_value),
        "odds_ratio": odds_ratio,
        "observed_probability": observed_probability,
        "table": [
            [a, b],
            [c, d],
        ],
    }