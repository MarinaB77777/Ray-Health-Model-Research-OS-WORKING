from __future__ import annotations

from itertools import combinations
from math import comb, sqrt
from random import Random
from statistics import median

from .numerics import mean, pearson, quantile, sample_variance


def _statistic(code: str, values: list[float], second: list[float] | None = None) -> float:
    if code == "mean":
        return mean(values)
    if code == "median":
        return float(median(values))
    if code == "difference_in_means":
        if not second:
            raise ValueError("SECOND_SAMPLE_REQUIRED")
        return mean(values) - mean(second)
    if code == "pearson_correlation":
        if second is None:
            raise ValueError("PAIRED_SAMPLE_REQUIRED")
        return pearson(values, second)
    raise ValueError("RESAMPLING_STATISTIC_UNSUPPORTED")


def bootstrap(payload: dict) -> dict:
    raw = payload.get("values")
    if not isinstance(raw, list) or len(raw) < 3:
        raise ValueError("BOOTSTRAP_REQUIRES_AT_LEAST_THREE_VALUES")
    values = [float(value) for value in raw]
    second_raw = payload.get("second_values")
    second = [float(value) for value in second_raw] if isinstance(second_raw, list) else None
    statistic = str(payload.get("statistic", "mean"))
    if statistic == "pearson_correlation" and (second is None or len(second) != len(values)):
        raise ValueError("CORRELATION_BOOTSTRAP_REQUIRES_PAIRED_VALUES")
    if statistic == "difference_in_means" and (second is None or len(second) < 3):
        raise ValueError("DIFFERENCE_BOOTSTRAP_REQUIRES_TWO_SAMPLES")
    resamples = int(payload.get("resamples", 2000))
    if not 500 <= resamples <= 100000:
        raise ValueError("BOOTSTRAP_RESAMPLES_OUT_OF_RANGE")
    mass = float(payload.get("interval_mass", 0.95))
    if not 0.5 < mass < 1.0:
        raise ValueError("INTERVAL_MASS_OUT_OF_RANGE")
    rng = Random(int(payload.get("random_seed", 1729)))
    estimates = []
    for _ in range(resamples):
        indexes = [rng.randrange(len(values)) for _ in values]
        first_sample = [values[index] for index in indexes]
        if statistic == "pearson_correlation":
            second_sample = [second[index] for index in indexes]
        elif second is not None:
            second_sample = [second[rng.randrange(len(second))] for _ in second]
        else:
            second_sample = None
        try:
            estimates.append(_statistic(statistic, first_sample, second_sample))
        except ValueError:
            continue
    if len(estimates) < max(100, resamples // 2):
        raise ValueError("TOO_MANY_DEGENERATE_BOOTSTRAP_RESAMPLES")
    tail = (1.0 - mass) / 2.0
    estimate = _statistic(statistic, values, second)
    return {
        "statistic": statistic,
        "estimate": estimate,
        "bootstrap_standard_error": sqrt(sample_variance(estimates)),
        "percentile_interval": {
            "mass": mass,
            "lower": quantile(estimates, tail),
            "upper": quantile(estimates, 1.0 - tail),
        },
        "requested_resamples": resamples,
        "valid_resamples": len(estimates),
        "random_seed": int(payload.get("random_seed", 1729)),
        "limitations": ["percentile_interval_not_bias_corrected"],
    }


def permutation_two_sample(payload: dict) -> dict:
    left_raw, right_raw = payload.get("left_values"), payload.get("right_values")
    if not isinstance(left_raw, list) or not isinstance(right_raw, list):
        raise ValueError("TWO_SAMPLES_REQUIRED")
    left, right = [float(v) for v in left_raw], [float(v) for v in right_raw]
    if len(left) < 2 or len(right) < 2:
        raise ValueError("PERMUTATION_REQUIRES_TWO_VALUES_PER_GROUP")
    alternative = str(payload.get("alternative", "two_sided"))
    if alternative not in {"two_sided", "greater", "less"}:
        raise ValueError("PERMUTATION_ALTERNATIVE_UNSUPPORTED")
    combined, left_count = left + right, len(left)
    observed = mean(left) - mean(right)
    requested = int(payload.get("permutations", 10000))
    if not 500 <= requested <= 200000:
        raise ValueError("PERMUTATION_COUNT_OUT_OF_RANGE")
    total_exact = comb(len(combined), left_count)
    exact = total_exact <= requested and total_exact <= 200000
    rng = Random(int(payload.get("random_seed", 1729)))
    statistics = []
    if exact:
        for indexes in combinations(range(len(combined)), left_count):
            selected = set(indexes)
            a = [value for index, value in enumerate(combined) if index in selected]
            b = [value for index, value in enumerate(combined) if index not in selected]
            statistics.append(mean(a) - mean(b))
    else:
        for _ in range(requested):
            shuffled = combined[:]
            rng.shuffle(shuffled)
            statistics.append(mean(shuffled[:left_count]) - mean(shuffled[left_count:]))
    if alternative == "two_sided":
        extreme = sum(abs(value) >= abs(observed) - 1e-15 for value in statistics)
    elif alternative == "greater":
        extreme = sum(value >= observed - 1e-15 for value in statistics)
    else:
        extreme = sum(value <= observed + 1e-15 for value in statistics)
    p_value = extreme / len(statistics) if exact else (extreme + 1) / (len(statistics) + 1)
    return {
        "statistic": "difference_in_means",
        "observed": observed,
        "alternative": alternative,
        "p_value": p_value,
        "exact": exact,
        "permutations_evaluated": len(statistics),
        "random_seed": None if exact else int(payload.get("random_seed", 1729)),
    }
