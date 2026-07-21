import pytest
from pydantic import ValidationError

from runtime.contracts.runtime_acquisition_request import (
    RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES,
    RuntimeAcquisitionRequest,
    RuntimeAcquisitionRequestStatus,
    RuntimeAcquisitionRequestType,
)


def make_request(**kwargs) -> RuntimeAcquisitionRequest:
    data = {
        "runtime_request_id": "runtime-acq-1",
        "action_id": "action-1",
        "requested_acquisition_type": (
            RuntimeAcquisitionRequestType.DIALOGUE_QUESTION
        ),
        "reason": "Need missing field from user",
        "required_fields": ["d0"],
    }
    data.update(kwargs)
    return RuntimeAcquisitionRequest(**data)


def test_runtime_acquisition_request_requires_runtime_request_id():
    with pytest.raises(ValidationError):
        make_request(runtime_request_id="")


def test_runtime_acquisition_request_requires_action_id():
    with pytest.raises(ValidationError):
        make_request(action_id="")


def test_runtime_acquisition_request_requires_reason():
    with pytest.raises(ValidationError):
        make_request(reason="")


def test_runtime_acquisition_request_requires_required_fields():
    with pytest.raises(ValidationError):
        make_request(required_fields=[])


def test_external_source_lookup_requires_policy_context():
    with pytest.raises(ValidationError):
        make_request(
            requested_acquisition_type=(
                RuntimeAcquisitionRequestType.EXTERNAL_SOURCE_LOOKUP
            ),
            policy_context={},
        )


def test_external_source_lookup_accepts_policy_context():
    request = make_request(
        requested_acquisition_type=(
            RuntimeAcquisitionRequestType.EXTERNAL_SOURCE_LOOKUP
        ),
        policy_context={
            "source_class": "official_source",
            "privacy_policy_known": True,
        },
    )

    assert request.policy_context["source_class"] == "official_source"


def test_prepared_status_is_allowed_but_not_sent_by_boundary_rule():
    request = make_request(
        status=RuntimeAcquisitionRequestStatus.PREPARED,
    )

    assert request.status == RuntimeAcquisitionRequestStatus.PREPARED
    assert "PREPARED_IS_NOT_SENT" in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES


def test_boundary_rules_prevent_layer_collapse():
    assert (
        "RUNTIME_ACQUISITION_REQUEST_IS_NOT_PERMISSION"
        in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES
    )
    assert (
        "RUNTIME_ACQUISITION_REQUEST_IS_NOT_ACQUISITION_RESULT"
        in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES
    )
    assert (
        "RUNTIME_ACQUISITION_REQUEST_IS_NOT_COORDINATOR_OUTPUT"
        in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES
    )
    assert (
        "RUNTIME_ACQUISITION_REQUEST_IS_NOT_COORDINATOR_SIGNAL"
        in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES
    )
    assert (
        "RUNTIME_ACQUISITION_REQUEST_IS_NOT_CORE_ENGINE_TRUTH"
        in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES
    )
    assert (
        "NO_LAYER_MAY_REINTERPRET_ANOTHER_LAYER_SNAPSHOT_AS_EXECUTION_AUTHORITY"
        in RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES
    )