def build_statistical_result(
    *,
    study_id: str,
    method_id: str,
    method_title: str,
    left_question_code: str,
    right_question_code: str,
    sample_size: int,
    test_statistic,
    test_statistic_name: str,
    degrees_of_freedom,
    alpha: float,
    p_value,
    null_hypothesis: str,
    alternative_hypothesis: str,
    results: dict,
    interpretation: dict,
    **extra,
) -> dict:
    significant = (
        p_value is not None
        and p_value < alpha
    )

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": method_id,
        "method_title": method_title,
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": sample_size,
        "test_statistic": test_statistic,
        "test_statistic_name": test_statistic_name,
        "degrees_of_freedom": degrees_of_freedom,
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": significant,
        "null_hypothesis": null_hypothesis,
        "alternative_hypothesis": alternative_hypothesis,
        "decision": (
            "Reject H₀"
            if significant
            else "Fail to reject H₀"
        ),
        "results": results,
        "interpretation": interpretation,
        **extra,
    }