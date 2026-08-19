from assessment.analysis import analyzer


def prognosis_with_active_candidate(_domain_scores):
    return {
        "level_profiles": {},
        "vulnerable_functions": {},
        "preserved_functions": {},
        "candidate_mechanisms": {"mechanism_a": [{"domain": "x"}, {"domain": "y"}]},
        "active_candidate_mechanisms": {
            "mechanism_a": [{"domain": "x"}, {"domain": "y"}]
        },
        "weak_candidate_mechanisms": {},
    }


def test_unknown_question_denominator_is_not_zero(monkeypatch):
    monkeypatch.setattr(
        analyzer,
        "build_prognosis_layer",
        prognosis_with_active_candidate,
    )

    result = analyzer.analyze_assessment(
        assessment_id="assessment-empty",
        assessment={"questions": []},
        answers={},
    )

    assert result["completion"] is None
    assert result["completion_known"] is False
    assert result["readiness_status"] == "NOT_EVALUABLE"
    assert result["forecast_allowed"] is False
    assert "COMPLETION_DENOMINATOR_UNKNOWN" in result["reason_codes"]


def test_active_candidate_does_not_enable_forecast_with_missing_required_data(
    monkeypatch,
):
    monkeypatch.setattr(
        analyzer,
        "build_prognosis_layer",
        prognosis_with_active_candidate,
    )

    result = analyzer.analyze_assessment(
        assessment_id="assessment-partial",
        assessment={
            "questions": [
                {"code": "T1"},
                {"code": "T2"},
            ]
        },
        answers={"T1": 3},
    )

    assert result["completion"] == 0.5
    assert result["completion_known"] is True
    assert result["forecast_allowed"] is False
    assert result["readiness_status"] == "ORIENTING"
    assert result["public_explanation"]["ru"]["forecast"] is None
    assert (
        "FORECAST_BLOCKED_BY_MISSING_REQUIRED_DATA"
        in result["reason_codes"]
    )


def test_complete_assessment_and_active_candidate_enable_bounded_forecast(
    monkeypatch,
):
    monkeypatch.setattr(
        analyzer,
        "build_prognosis_layer",
        prognosis_with_active_candidate,
    )

    result = analyzer.analyze_assessment(
        assessment_id="assessment-complete",
        assessment={
            "questions": [
                {"code": "T1"},
                {"code": "T2"},
            ]
        },
        answers={"T1": 3, "T2": 2},
    )

    assert result["completion"] == 1.0
    assert result["forecast_allowed"] is True
    assert result["readiness_status"] == "BOUNDED_FORECAST_READY"
