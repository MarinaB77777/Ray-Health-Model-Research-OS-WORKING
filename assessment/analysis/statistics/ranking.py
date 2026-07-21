from collections import Counter


def rank_values(values: list[float]) -> list[float]:
    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1],
    )

    ranks = [0.0] * len(values)
    i = 0

    while i < len(indexed):
        j = i

        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1

        average_rank = (i + 1 + j + 1) / 2.0

        for k in range(i, j + 1):
            original_index = indexed[k][0]
            ranks[original_index] = average_rank

        i = j + 1

    return ranks


def has_ties(values: list[float]) -> bool:
    return any(
        count > 1
        for count in Counter(values).values()
    )


def tie_correction_term(values: list[float]) -> float:
    counts = Counter(values)

    return sum(
        count ** 3 - count
        for count in counts.values()
        if count > 1
    )