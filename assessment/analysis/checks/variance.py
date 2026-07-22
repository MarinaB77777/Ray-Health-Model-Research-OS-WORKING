from assessment.analysis.statistics.parametric_groups import brown_forsythe_test


def check_variance_assumption(*, groups: dict, alpha: float = 0.05) -> dict:
    result = brown_forsythe_test(groups=groups)
    if not result.get("ok"):
        status = "blocked"
    elif result.get("p_value", 0.0) < alpha:
        status = "failed"
    else:
        status = "passed"
    return {
        "check_id": "variance_assumption_checked",
        "status": status,
        "details": {
            "test": "Brown-Forsythe median-centered Levene test",
            "alpha": alpha,
            **result,
        },
    }
