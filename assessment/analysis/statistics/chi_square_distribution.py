import math


def _regularized_gamma_p(
    *,
    a: float,
    x: float,
) -> float:
    max_iter = 200
    eps = 3e-14

    if x <= 0:
        return 0.0

    ap = a
    total = 1.0 / a
    delta = total

    for _ in range(max_iter):
        ap += 1.0
        delta *= x / ap
        total += delta

        if abs(delta) < abs(total) * eps:
            break

    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _regularized_gamma_q(
    *,
    a: float,
    x: float,
) -> float:
    max_iter = 200
    eps = 3e-14
    fpmin = 1e-300

    if x <= 0:
        return 1.0

    b = x + 1.0 - a
    c = 1.0 / fpmin
    d = 1.0 / b
    h = d

    for i in range(1, max_iter + 1):
        an = -i * (i - a)
        b += 2.0

        d = an * d + b
        if abs(d) < fpmin:
            d = fpmin

        c = b + an / c
        if abs(c) < fpmin:
            c = fpmin

        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < eps:
            break

    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi_square_survival_function(
    *,
    chi_square: float,
    degrees_of_freedom: int,
) -> float | None:
    if degrees_of_freedom <= 0:
        return None

    if chi_square < 0:
        return None

    a = degrees_of_freedom / 2.0
    x = chi_square / 2.0

    if x < a + 1.0:
        p = _regularized_gamma_p(a=a, x=x)
        return max(0.0, min(1.0, 1.0 - p))

    q = _regularized_gamma_q(a=a, x=x)
    return max(0.0, min(1.0, q))