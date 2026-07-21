from __future__ import annotations

from math import exp, isfinite, lgamma, log, sqrt
from statistics import NormalDist


class NumericalError(ValueError):
    pass


def quantile(values: list[float], probability: float) -> float:
    if not values:
        raise NumericalError("QUANTILE_REQUIRES_VALUES")
    if not 0.0 <= probability <= 1.0:
        raise NumericalError("QUANTILE_PROBABILITY_OUT_OF_RANGE")
    ordered = sorted(float(value) for value in values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def mean(values: list[float]) -> float:
    if not values:
        raise NumericalError("MEAN_REQUIRES_VALUES")
    return sum(values) / len(values)


def sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        raise NumericalError("VARIANCE_REQUIRES_TWO_VALUES")
    center = mean(values)
    return sum((value - center) ** 2 for value in values) / (len(values) - 1)


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        raise NumericalError("CORRELATION_REQUIRES_THREE_PAIRED_VALUES")
    mx, my = mean(x), mean(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    left = sum((a - mx) ** 2 for a in x)
    right = sum((b - my) ** 2 for b in y)
    if left <= 0 or right <= 0:
        raise NumericalError("CORRELATION_REQUIRES_NONCONSTANT_VARIABLES")
    return numerator / sqrt(left * right)


def normal_quantile(probability: float) -> float:
    if not 0.0 < probability < 1.0:
        raise NumericalError("NORMAL_QUANTILE_PROBABILITY_OUT_OF_RANGE")
    return NormalDist().inv_cdf(probability)


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    maximum_iterations, epsilon, floor = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < floor:
        d = floor
    d = 1.0 / d
    h = d
    for iteration in range(1, maximum_iterations + 1):
        m2 = 2 * iteration
        aa = iteration * (b - iteration) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + aa / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        h *= d * c
        aa = -(a + iteration) * (qab + iteration) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + aa / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) <= epsilon:
            return h
    raise NumericalError("INCOMPLETE_BETA_DID_NOT_CONVERGE")


def regularized_beta(x: float, a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        raise NumericalError("BETA_SHAPES_MUST_BE_POSITIVE")
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    log_front = lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1.0 - x)
    front = exp(log_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1.0 - front * _beta_continued_fraction(b, a, 1.0 - x) / b


def beta_quantile(probability: float, a: float, b: float) -> float:
    if probability <= 0:
        return 0.0
    if probability >= 1:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(100):
        midpoint = (low + high) / 2.0
        if regularized_beta(midpoint, a, b) < probability:
            low = midpoint
        else:
            high = midpoint
    return (low + high) / 2.0


def student_t_cdf(value: float, degrees_of_freedom: float) -> float:
    if degrees_of_freedom <= 0:
        raise NumericalError("STUDENT_T_DF_MUST_BE_POSITIVE")
    if value == 0:
        return 0.5
    ratio = degrees_of_freedom / (degrees_of_freedom + value * value)
    tail = 0.5 * regularized_beta(ratio, degrees_of_freedom / 2.0, 0.5)
    return 1.0 - tail if value > 0 else tail


def student_t_quantile(probability: float, degrees_of_freedom: float) -> float:
    if not 0.0 < probability < 1.0:
        raise NumericalError("STUDENT_T_PROBABILITY_OUT_OF_RANGE")
    if probability == 0.5:
        return 0.0
    low, high = -1.0, 1.0
    while student_t_cdf(low, degrees_of_freedom) > probability:
        low *= 2.0
    while student_t_cdf(high, degrees_of_freedom) < probability:
        high *= 2.0
    for _ in range(100):
        midpoint = (low + high) / 2.0
        if student_t_cdf(midpoint, degrees_of_freedom) < probability:
            low = midpoint
        else:
            high = midpoint
    result = (low + high) / 2.0
    if not isfinite(result):
        raise NumericalError("STUDENT_T_QUANTILE_NOT_FINITE")
    return result
