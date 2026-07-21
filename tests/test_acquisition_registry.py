import pytest

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionSourceClass,
    AcquisitionStatus,
    SufficiencyStatus,
)
from runtime.acquisition.registry import AcquisitionRegistry


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": "Internal question",
        "source_class": AcquisitionSourceClass.STANDARD_AI_SERVICE,
    }
    data.update(kwargs)
    return AcquisitionRequest(**data)


def test_add_and_get_request():
    registry = AcquisitionRegistry()
    request = make_request()

    registry.add_request(request)

    stored = registry.get_request("req-1")

    assert stored is not None
    assert stored.request_id == "req-1"


def test_duplicate_request_is_rejected():
    registry = AcquisitionRegistry()
    request = make_request()

    registry.add_request(request)

    with pytest.raises(ValueError):
        registry.add_request(request)


def test_get_request_returns_copy_not_original():
    registry = AcquisitionRegistry()
    request = make_request()

    registry.add_request(request)

    stored = registry.get_request("req-1")
    stored.filled_fields["answer"] = "mutated outside"

    fresh = registry.get_request("req-1")

    assert "answer" not in fresh.filled_fields


def test_update_status_revalidates_and_updates():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    updated = registry.update_status(
        "req-1",
        AcquisitionStatus.WAITING,
    )

    assert updated is not None
    assert updated.status == AcquisitionStatus.WAITING


def test_update_missing_request_returns_none():
    registry = AcquisitionRegistry()

    result = registry.update_status(
        "missing",
        AcquisitionStatus.WAITING,
    )

    assert result is None


def test_update_sufficiency_status_revalidates():
    registry = AcquisitionRegistry()

    registry.add_request(
        make_request(
            required_fields=["answer"],
            filled_fields={"answer": "value"},
            status=AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
        )
    )

    updated = registry.update_sufficiency_status(
        "req-1",
        SufficiencyStatus.BOUNDED_ANALYSIS_READY,
    )

    assert updated is not None
    assert updated.sufficiency_status == (
        SufficiencyStatus.BOUNDED_ANALYSIS_READY
    )


def test_update_sufficiency_status_invalid_state_raises():
    registry = AcquisitionRegistry()

    registry.add_request(make_request())

    with pytest.raises(ValueError):
        registry.update_sufficiency_status(
            "req-1",
            SufficiencyStatus.BOUNDED_ANALYSIS_READY,
        )


def test_update_filled_fields_merges_values():
    registry = AcquisitionRegistry()

    registry.add_request(
        make_request(
            required_fields=["answer", "source"],
            filled_fields={"answer": "value"},
        )
    )

    updated = registry.update_filled_fields(
        "req-1",
        {"source": "official source"},
    )

    assert updated is not None
    assert updated.filled_fields == {
        "answer": "value",
        "source": "official source",
    }


def test_update_filled_fields_outside_required_requires_metadata():
    registry = AcquisitionRegistry()

    registry.add_request(
        make_request(
            required_fields=["answer"],
        )
    )

    with pytest.raises(ValueError):
        registry.update_filled_fields(
            "req-1",
            {"extra": "value"},
        )


def test_update_filled_fields_outside_required_allowed_with_metadata():
    registry = AcquisitionRegistry()

    registry.add_request(
        make_request(
            required_fields=["answer"],
        )
    )

    updated = registry.update_filled_fields(
        "req-1",
        {"extra": "value"},
        extra_filled_fields_metadata={
            "extra": "contextual metadata",
        },
    )

    assert updated is not None
    assert updated.filled_fields["extra"] == "value"


def test_update_outbound_state_requires_metadata_when_sent():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    with pytest.raises(ValueError):
        registry.update_outbound_state(
            "req-1",
            outbound_sent=True,
        )


def test_update_outbound_state_with_metadata():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    updated = registry.update_outbound_state(
        "req-1",
        outbound_sent=True,
        outbound_source_metadata={
            "source": "external_standard_ai_service",
        },
    )

    assert updated is not None
    assert updated.outbound_sent is True


def test_remove_request():
    registry = AcquisitionRegistry()
    registry.add_request(make_request())

    assert registry.remove_request("req-1") is True
    assert registry.get_request("req-1") is None


def test_remove_missing_request_returns_false():
    registry = AcquisitionRegistry()

    assert registry.remove_request("missing") is False


def test_list_requests_returns_all_requests():
    registry = AcquisitionRegistry()

    registry.add_request(make_request(request_id="req-1"))
    registry.add_request(make_request(request_id="req-2"))

    result = registry.list_requests()

    assert len(result) == 2


def test_list_by_status_returns_matching_requests_only():
    registry = AcquisitionRegistry()

    registry.add_request(
        make_request(
            request_id="req-1",
            status=AcquisitionStatus.WAITING,
        )
    )
    registry.add_request(
        make_request(
            request_id="req-2",
            status=AcquisitionStatus.BLOCKED,
        )
    )

    waiting = registry.list_by_status(AcquisitionStatus.WAITING)

    assert len(waiting) == 1
    assert waiting[0].request_id == "req-1"


def test_clear_removes_all_requests():
    registry = AcquisitionRegistry()

    registry.add_request(make_request(request_id="req-1"))
    registry.add_request(make_request(request_id="req-2"))

    registry.clear()

    assert registry.list_requests() == []