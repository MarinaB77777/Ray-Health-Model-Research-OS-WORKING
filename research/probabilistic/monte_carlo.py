from __future__ import annotations

from math import isfinite
from random import Random

from .numerics import mean, pearson, quantile, sample_variance


def _draw(specification: dict, rng: Random) -> float:
    distribution = specification.get("distribution")
    if distribution == "normal":
        standard_deviation = float(specification.get("standard_deviation", 0))
        if standard_deviation < 0:
            raise ValueError("NORMAL_STANDARD_DEVIATION_MUST_BE_NONNEGATIVE")
        return rng.gauss(float(specification.get("mean", 0)), standard_deviation)
    if distribution == "uniform":
        low, high = float(specification["low"]), float(specification["high"])
        if high <= low:
            raise ValueError("UNIFORM_BOUNDS_INVALID")
        return rng.uniform(low, high)
    if distribution == "triangular":
        low, high, mode = float(specification["low"]), float(specification["high"]), float(specification["mode"])
        if not low <= mode <= high or high <= low:
            raise ValueError("TRIANGULAR_PARAMETERS_INVALID")
        return rng.triangular(low, high, mode)
    if distribution == "beta":
        alpha, beta = float(specification["alpha"]), float(specification["beta"])
        if alpha <= 0 or beta <= 0:
            raise ValueError("BETA_SHAPES_MUST_BE_POSITIVE")
        return rng.betavariate(alpha, beta)
    if distribution == "constant":
        return float(specification["value"])
    raise ValueError("MONTE_CARLO_DISTRIBUTION_UNSUPPORTED")


def _combine(operation: str, values: list[float], weights: list[float] | None) -> float:
    if operation == "sum":
        return sum(values)
    if operation == "difference" and len(values) == 2:
        return values[0] - values[1]
    if operation == "product":
        result = 1.0
        for value in values:
            result *= value
        return result
    if operation == "ratio" and len(values) == 2:
        if values[1] == 0:
            raise ZeroDivisionError
        return values[0] / values[1]
    if operation == "weighted_sum" and weights is not None and len(weights) == len(values):
        return sum(value * weight for value, weight in zip(values, weights))
    raise ValueError("MONTE_CARLO_OPERATION_OR_ARITY_UNSUPPORTED")


def propagate_uncertainty(payload: dict) -> dict:
    inputs = payload.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("MONTE_CARLO_INPUTS_REQUIRED")
    if any(not isinstance(item, dict) or not item.get("name") for item in inputs):
        raise ValueError("MONTE_CARLO_INPUT_SPECIFICATION_INVALID")
    samples = int(payload.get("samples", 20000))
    if not 1000 <= samples <= 1000000:
        raise ValueError("MONTE_CARLO_SAMPLE_COUNT_OUT_OF_RANGE")
    mass = float(payload.get("interval_mass", 0.95))
    if not 0.5 < mass < 1.0:
        raise ValueError("INTERVAL_MASS_OUT_OF_RANGE")
    operation = str(payload.get("operation", "sum"))
    weights = payload.get("weights")
    weights = [float(value) for value in weights] if isinstance(weights, list) else None
    seed = int(payload.get("random_seed", 1729))
    rng = Random(seed)
    input_draws = [[] for _ in inputs]
    outputs, rejected = [], 0
    for _ in range(samples):
        draw = [_draw(specification, rng) for specification in inputs]
        try:
            output = _combine(operation, draw, weights)
        except ZeroDivisionError:
            rejected += 1
            continue
        if not isfinite(output):
            rejected += 1
            continue
        outputs.append(output)
        for column, value in zip(input_draws, draw):
            column.append(value)
    if len(outputs) < samples * 0.9:
        raise ValueError("MONTE_CARLO_TOO_MANY_REJECTED_DRAWS")
    tail = (1.0 - mass) / 2.0
    sensitivity = []
    for specification, column in zip(inputs, input_draws):
        try:
            coefficient = pearson(column, outputs)
        except ValueError:
            coefficient = None
        sensitivity.append({"input": specification["name"], "pearson_with_output": coefficient})
    return {
        "operation": operation,
        "estimate": mean(outputs),
        "simulation_standard_deviation": sample_variance(outputs) ** 0.5,
        "simulation_interval": {"mass": mass, "lower": quantile(outputs, tail), "upper": quantile(outputs, 1.0 - tail)},
        "samples_requested": samples,
        "samples_valid": len(outputs),
        "samples_rejected": rejected,
        "random_seed": seed,
        "sensitivity": sensitivity,
        "assumptions": ["input_draws_independent_unless_encoded_by_shared_input", "input_distributions_treated_as_specified"],
    }
