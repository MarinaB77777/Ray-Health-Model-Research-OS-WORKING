import math

from assessment.analysis.statistics.chi_square_distribution import (
    chi_square_survival_function,
)


def _jarque_bera(values: list[float]) -> dict:
    n = len(values)
    mean_value = sum(values) / n
    centered = [value - mean_value for value in values]
    second_moment = sum(value ** 2 for value in centered) / n
    if second_moment <= 0:
        return {"ok": False, "status": "constant_group"}
    third_moment = sum(value ** 3 for value in centered) / n
    fourth_moment = sum(value ** 4 for value in centered) / n
    skewness = third_moment / (second_moment ** 1.5)
    kurtosis = fourth_moment / (second_moment ** 2)
    statistic = n / 6.0 * (skewness ** 2 + (kurtosis - 3.0) ** 2 / 4.0)
    return {
        "ok": True,
        "test_statistic": statistic,
        "p_value": chi_square_survival_function(
            chi_square=statistic,
            degrees_of_freedom=2,
        ),
        "skewness": skewness,
        "kurtosis": kurtosis,
    }


def check_group_normality(*, groups: dict[str, list[float]], alpha: float = 0.05) -> dict:
    results = {}
    rejected = []
    limited_power = []
    for name, raw_values in groups.items():
        values = []
        for value in raw_values:
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(numeric):
                values.append(numeric)
        if len(values) < 8:
            limited_power.append(name)
            results[name] = {
                "n": len(values),
                "status": "insufficient_for_jarque_bera_diagnostic",
            }
            continue
        diagnostic = _jarque_bera(values)
        results[name] = {"n": len(values), **diagnostic}
        if diagnostic.get("ok") and diagnostic.get("p_value", 1.0) < alpha:
            rejected.append(name)

    if rejected:
        status = "failed"
    elif not results:
        status = "blocked"
    elif limited_power:
        status = "warning"
    else:
        status = "passed"
    return {
        "check_id": "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
        "status": status,
        "details": {
            "diagnostic": "Jarque-Bera within each group",
            "alpha": alpha,
            "groups": results,
            "rejected_group_names": rejected,
            "limited_power_group_names": limited_power,
            "note": (
                "A non-significant diagnostic does not prove normality. "
                "Groups with fewer than eight observations are reported as limited evidence, not treated as normal."
            ),
        },
    }


def check_approximately_normal_or_sufficient_sample(*, values: list, minimum_for_sample_size_assumption: int = 30) -> dict:
    # Backward-compatible entry point. It deliberately does not use sample size
    # alone as proof of normality.
    return check_group_normality(groups={"outcome": values})
