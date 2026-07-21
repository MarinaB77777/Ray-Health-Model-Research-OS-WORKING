import math


def mean(values: list[float]) -> float | None:
    if not values:
        return None

    return sum(values) / len(values)


def sample_variance(values: list[float]) -> float | None:
    if len(values) < 2:
        return None

    value_mean = mean(values)

    return sum(
        (value - value_mean) ** 2
        for value in values
    ) / (len(values) - 1)


def sample_standard_deviation(values: list[float]) -> float | None:
    variance = sample_variance(values)

    if variance is None:
        return None

    return math.sqrt(variance)


def median(values: list[float]) -> float | None:
    if not values:
        return None

    sorted_values = sorted(values)
    n = len(sorted_values)
    middle = n // 2

    if n % 2 == 1:
        return sorted_values[middle]

    return (
        sorted_values[middle - 1]
        + sorted_values[middle]
    ) / 2.0


def group_descriptive_summary(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "standard_deviation": sample_standard_deviation(values),
    }