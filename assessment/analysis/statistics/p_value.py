import math


def _betacf(a: float, b: float, x: float) -> float:
    max_iter = 200
    eps = 3e-14
    fpmin = 1e-300

    qab = a + b
    qap = a + 1.0
    qam = a - 1.0

    c = 1.0
    d = 1.0 - qab * x / qap

    if abs(d) < fpmin:
        d = fpmin

    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m

        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < eps:
            break

    return h


def regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    if x < 0.0 or x > 1.0:
        raise ValueError("x must be in [0, 1]")

    if x == 0.0:
        return 0.0

    if x == 1.0:
        return 1.0

    log_bt = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log(1.0 - x)
    )

    bt = math.exp(log_bt)

    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a

    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def student_t_two_tailed_p_value(
    *,
    t_statistic: float,
    degrees_of_freedom: float,
) -> float:
    if degrees_of_freedom <= 0:
        raise ValueError("degrees_of_freedom must be positive")

    t = abs(t_statistic)
    df = float(degrees_of_freedom)

    x = df / (df + t * t)

    return regularized_incomplete_beta(
        df / 2.0,
        0.5,
        x,
    )


def f_distribution_survival_function(
    *,
    f_statistic: float,
    numerator_degrees_of_freedom: float,
    denominator_degrees_of_freedom: float,
) -> float:
    """Upper-tail probability for the F distribution.

    The transformation to the regularized incomplete beta function is exact
    for positive degrees of freedom; no normal approximation is used.
    """
    if numerator_degrees_of_freedom <= 0:
        raise ValueError("numerator_degrees_of_freedom must be positive")
    if denominator_degrees_of_freedom <= 0:
        raise ValueError("denominator_degrees_of_freedom must be positive")
    if f_statistic < 0:
        raise ValueError("f_statistic must be non-negative")
    if math.isinf(f_statistic):
        return 0.0

    dfn = float(numerator_degrees_of_freedom)
    dfd = float(denominator_degrees_of_freedom)
    x = dfd / (dfd + dfn * f_statistic)
    probability = regularized_incomplete_beta(
        dfd / 2.0,
        dfn / 2.0,
        x,
    )
    return max(0.0, min(1.0, probability))


def spearman_p_value(
    *,
    rho: float,
    sample_size: int,
) -> float | None:
    if sample_size < 3:
        return None

    if rho <= -1.0 or rho >= 1.0:
        return 0.0

    denominator = 1.0 - rho * rho

    if denominator <= 0:
        return 0.0

    t_statistic = rho * math.sqrt((sample_size - 2) / denominator)

    return student_t_two_tailed_p_value(
        t_statistic=t_statistic,
        degrees_of_freedom=sample_size - 2,
    )

def correlation_p_value(
    *,
    correlation: float,
    sample_size: int,
) -> float | None:
    if sample_size < 3:
        return None

    if correlation <= -1.0 or correlation >= 1.0:
        return 0.0

    denominator = 1.0 - correlation * correlation

    if denominator <= 0:
        return 0.0

    t_statistic = correlation * math.sqrt(
        (sample_size - 2) / denominator
    )

    return student_t_two_tailed_p_value(
        t_statistic=t_statistic,
        degrees_of_freedom=sample_size - 2,
    )
