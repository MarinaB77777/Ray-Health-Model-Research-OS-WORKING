# tests/test_readiness_checker.py

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionSourceClass,
    SufficiencyStatus,
)

from runtime.acquisition.readiness_checker import ReadinessChecker


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Internal question",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_missing_required_fields_returns_insufficient():
    checker = ReadinessChecker()

    request = make_request(
        required_fields=["answer", "source"],
        filled_fields={"answer": "Some answer"},
    )

    result = checker.evaluate(request)

    assert result.sufficiency_status == SufficiencyStatus.INSUFFICIENT
    assert result.missing_required_fields == ["source"]
    assert result.allowed_next_step == "ask_or_acquire_missing_fields"
    assert result.readiness_metadata["ready_for_analysis"] is False


def test_empty_required_field_returns_insufficient():
    checker = ReadinessChecker()

    request = make_request(
        required_fields=["answer"],
        filled_fields={"answer": ""},
    )

    result = checker.evaluate(request)

    assert result.sufficiency_status == SufficiencyStatus.INSUFFICIENT
    assert result.missing_required_fields == ["answer"]


def test_none_required_field_returns_insufficient():
    checker = ReadinessChecker()

    request = make_request(
        required_fields=["answer"],
        filled_fields={"answer": None},
    )

    result = checker.evaluate(request)

    assert result.sufficiency_status == SufficiencyStatus.INSUFFICIENT
    assert result.missing_required_fields == ["answer"]


def test_all_required_fields_filled_returns_bounded_analysis_ready():
    checker = ReadinessChecker()

    request = make_request(
        required_fields=["answer", "source"],
        filled_fields={
            "answer": "Some answer",
            "source": "official source",
        },
    )

    result = checker.evaluate(request)

    assert result.sufficiency_status == (
        SufficiencyStatus.BOUNDED_ANALYSIS_READY
    )
    assert result.allowed_next_step == "analyst_answer_builder"
    assert result.readiness_metadata["ready_for_analysis"] is True
    assert result.readiness_metadata["ready_for_forecast"] is False


def test_readiness_checker_does_not_grant_forecast():
    checker = ReadinessChecker()

    request = make_request(
        required_fields=["answer"],
        filled_fields={"answer": "Some answer"},
    )

    result = checker.evaluate(request)

    assert result.sufficiency_status != SufficiencyStatus.FORECAST_READY
    assert (
        result.readiness_metadata[
            "forecast_not_granted_by_this_checker"
        ]
        is True
    )