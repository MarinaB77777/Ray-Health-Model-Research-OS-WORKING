from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionRequest,
    AcquisitionSourceClass,
    ExposureDecision,
)

from runtime.acquisition.exposure_filter import ExposureFilter


def make_request(
    question: str,
) -> AcquisitionRequest:
    return AcquisitionRequest(
        request_id="req-1",
        raw_internal_question=question,
        source_class=AcquisitionSourceClass.STANDARD_AI_SERVICE,
    )


def test_unknown_privacy_policy_requires_permission():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request("How is this situation handled?"),
        privacy_policy_known=False,
    )

    assert result.decision == ExposureDecision.NEEDS_HUMAN_PERMISSION

    assert set(result.reason_codes) == {
        AcquisitionReasonCode.PRIVACY_POLICY_UNKNOWN,
        AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
    }


def test_missing_raw_question_is_blocked():
    exposure_filter = ExposureFilter()

    request = AcquisitionRequest(
        request_id="req-1",
        raw_internal_question_ref="private-ref",
        source_class=AcquisitionSourceClass.STANDARD_AI_SERVICE,
    )

    result = exposure_filter.filter_for_external_acquisition(
        request=request,
    )

    assert result.decision == ExposureDecision.BLOCKED

    assert result.reason_codes == [
        AcquisitionReasonCode.RAW_QUESTION_INTERNAL_ONLY,
    ]


def test_basic_anonymization_removes_email():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "Contact me at john@example.com please."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert result.outbound_sanitized_request is not None

    assert "john@example.com" not in (
        result.outbound_sanitized_request
    )

    assert "[email removed]" in (
        result.outbound_sanitized_request
    )


def test_basic_anonymization_removes_phone():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "My number is +1 (555) 222-3333."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert "+1" not in result.outbound_sanitized_request

    assert "[phone removed]" in (
        result.outbound_sanitized_request
    )


def test_basic_anonymization_generalizes_age():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "The patient is 12 years old."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert "12 years old" not in (
        result.outbound_sanitized_request
    )

    assert "child" in result.outbound_sanitized_request


def test_basic_anonymization_generalizes_family_name():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "My husband Michael has stress symptoms."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert "Michael" not in (
        result.outbound_sanitized_request
    )

    assert "a family member" in (
        result.outbound_sanitized_request
    )


def test_basic_anonymization_removes_address():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "The person lives at 123 Main Street."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert "123 Main Street" not in (
        result.outbound_sanitized_request
    )

    assert "[address removed]" in (
        result.outbound_sanitized_request
    )


def test_high_risk_personal_data_requires_permission():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "The diagnosis is severe stress disorder."
        ),
        human_permission_granted=False,
    )

    assert result.decision == (
        ExposureDecision.CANNOT_SAFELY_ANONYMIZE
    )

    assert result.reason_codes == [
        AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
    ]


def test_high_risk_personal_data_still_blocked_even_with_permission():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "The diagnosis is severe stress disorder."
        ),
        human_permission_granted=True,
    )

    assert result.decision == (
        ExposureDecision.CANNOT_SAFELY_ANONYMIZE
    )

    assert result.reason_codes == [
        AcquisitionReasonCode.HUMAN_PERMISSION_REQUIRED,
    ]


def test_remaining_high_risk_marker_after_sanitization_blocks_export():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "passport number should be checked"
        ),
    )

    assert result.decision == (
        ExposureDecision.CANNOT_SAFELY_ANONYMIZE
    )


def test_outbound_request_is_temporary_only():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "Need general stress-management information."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert result.persist_sanitized_request is False

    assert result.exposure_metadata == {
        "raw_question_used_directly": False,
        "temporary_only": True,
        "anonymization": "basic",
    }


def test_allowed_request_marks_not_stored_reason():
    exposure_filter = ExposureFilter()

    result = exposure_filter.filter_for_external_acquisition(
        request=make_request(
            "Need general scheduling advice."
        ),
    )

    assert result.decision == ExposureDecision.ALLOWED

    assert result.reason_codes == [
        AcquisitionReasonCode.OUTBOUND_SANITIZED_NOT_STORED,
    ]