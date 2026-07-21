from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionResult,
    AcquisitionSourceClass,
    InboundFilterDecision,
)

from runtime.acquisition.result_filter import ResultFilter


def make_result(
    text: str,
    source_class: AcquisitionSourceClass = AcquisitionSourceClass.INTERNET,
) -> AcquisitionResult:
    return AcquisitionResult(
        request_id="req-1",
        source_class=source_class,
        raw_external_result=text,
    )


def test_empty_result_blocked_as_irrelevant():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(""),
    )

    assert result.decision == InboundFilterDecision.BLOCKED_IRRELEVANT
    assert result.reason_codes == [
        AcquisitionReasonCode.NO_DATA_ASK_OR_ACQUIRE,
    ]


def test_fake_or_fabricated_content_is_rejected():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result("This is a fictional invented answer.")
    )

    assert result.decision == (
        InboundFilterDecision.BLOCKED_FAKE_OR_FABRICATED
    )
    assert result.reason_codes == [
        AcquisitionReasonCode.FAKE_CONTENT_REJECTED,
    ]


def test_unsafe_content_is_blocked():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result("Here is an illegal method to bypass the law.")
    )

    assert result.decision == InboundFilterDecision.BLOCKED_UNSAFE
    assert result.reason_codes == [
        AcquisitionReasonCode.UNSAFE_EXTERNAL_RESULT,
    ]


def test_academic_domain_requires_scientific_or_official_source():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Some research-like answer.",
            source_class=AcquisitionSourceClass.INTERNET,
        ),
        domain="academic",
    )

    assert result.decision == (
        InboundFilterDecision.BLOCKED_LOW_SOURCE_QUALITY
    )
    assert result.reason_codes == [
        AcquisitionReasonCode.SCIENTIFIC_SOURCE_REQUIRED,
        AcquisitionReasonCode.SOURCE_CLASS_MISMATCH,
    ]


def test_academic_domain_allows_scientific_source():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Peer-reviewed research summary.",
            source_class=AcquisitionSourceClass.SCIENTIFIC_SOURCE,
        ),
        domain="academic",
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS
    assert result.cleaned_result == "Peer-reviewed research summary."
    assert result.filter_metadata["trusted"] is False
    assert result.filter_metadata["verified"] is False


def test_legal_domain_requires_official_source():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Some legal advice from random source.",
            source_class=AcquisitionSourceClass.INTERNET,
        ),
        domain="legal",
    )

    assert result.decision == (
        InboundFilterDecision.BLOCKED_LOW_SOURCE_QUALITY
    )
    assert result.reason_codes == [
        AcquisitionReasonCode.OFFICIAL_SOURCE_REQUIRED,
        AcquisitionReasonCode.SOURCE_CLASS_MISMATCH,
    ]


def test_government_domain_allows_official_source():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Official government procedure.",
            source_class=AcquisitionSourceClass.OFFICIAL_SOURCE,
        ),
        domain="government",
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS


def test_medical_domain_blocks_sensor_source():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Sensor signal data.",
            source_class=AcquisitionSourceClass.SENSOR,
        ),
        domain="medical",
    )

    assert result.decision == (
        InboundFilterDecision.BLOCKED_LOW_SOURCE_QUALITY
    )


def test_health_domain_allows_sensor_source():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Heart rate trend increased after workload.",
            source_class=AcquisitionSourceClass.SENSOR,
        ),
        domain="health",
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS


def test_readiness_domain_allows_internal_ray_layer():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "Internal readiness context.",
            source_class=AcquisitionSourceClass.INTERNAL_RAY_LAYER,
        ),
        domain="readiness",
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS


def test_psychophysical_domain_allows_human_primary():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result(
            "User reports fatigue and low sleep quality.",
            source_class=AcquisitionSourceClass.HUMAN_PRIMARY,
        ),
        domain="psychophysical",
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS


def test_cleaned_result_is_not_trusted_or_verified():
    result_filter = ResultFilter()

    result = result_filter.filter_result(
        make_result("   Useful external result.   ")
    )

    assert result.decision == InboundFilterDecision.ALLOWED_FOR_READINESS
    assert result.cleaned_result == "Useful external result."
    assert result.reason_codes == [
        AcquisitionReasonCode.CLEANED_NOT_TRUSTED,
        AcquisitionReasonCode.TRUSTED_NOT_VERIFIED,
    ]
    assert result.filter_metadata == {
        "cleaned": True,
        "trusted": False,
        "verified": False,
    }