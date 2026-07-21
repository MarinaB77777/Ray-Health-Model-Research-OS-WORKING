# tests/test_runtime_coordinator_orchestration_handoff_helper.py

from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationStatus,
)
from runtime.acquisition.runtime_bridge import AcquisitionRuntimeBridge
from runtime.acquisition.runtime_request_builder import (
    RuntimeAcquisitionRequestBuilder,
)
from runtime.coordinator.contracts import (
    CoordinatorOutput,
    CoordinatorStatus,
)
from runtime.coordinator.orchestration_handoff import (
    handoff_acquisition_to_orchestration,
)
from runtime.acquisition.orchestration_service import (
    RuntimeAcquisitionOrchestrationService,
)


def _make_coordinator_output() -> CoordinatorOutput:
    return CoordinatorOutput(
        coordinator_id="coord_helper_1",
        action_id="action_helper_1",
        status=CoordinatorStatus.CREATED,
        ready_for_next_route=False,
        warnings=[],
    )


def test_handoff_helper_routes_to_orchestration_when_acquisition_required():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k40",
        reason="handoff helper integration",
    )

    assert result is not None

    assert result.status == RuntimeAcquisitionOrchestrationStatus.WAITING
    assert result.acquisition_request_id

    assert result.invariants["waiting_is_not_answered"] is True
    assert (
        result.invariants["automatic_routing_is_not_automatic_authority"]
        is True
    )

def test_handoff_helper_returns_none_when_acquisition_not_required():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=False,
        variable_code="k41",
        reason="no explicit acquisition request",
    )

    assert result is None
    assert service._states == {}

class FailingBridge:
    def create_from_runtime_request(self, runtime_request):
        raise RuntimeError("handoff helper bridge failure")


def test_handoff_helper_preserves_blocked_orchestration_state():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=FailingBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k42",
        reason="handoff helper blocked preservation",
    )

    assert result is not None

    assert result.status == RuntimeAcquisitionOrchestrationStatus.BLOCKED
    assert result.unresolved is True

    assert result.blocked_reason == "bridge_error"
    assert "handoff helper bridge failure" in result.last_error

    assert result.invariants["blocked_is_not_cancelled"] is True
    assert result.invariants["unresolved_is_not_solved"] is True

def test_handoff_helper_does_not_mutate_runtime_lifecycle_after_handoff():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k43",
        reason="lifecycle mutation protection",
    )

    assert result is not None

    state = service._states[result.orchestration_id]

    assert (
        state.status
        == RuntimeAcquisitionOrchestrationStatus.WAITING
    )

    assert state.unresolved is False

    assert (
        result.invariants[
            "automatic_routing_is_not_automatic_authority"
        ]
        is True
    )

    assert result.invariants["prepared_is_not_executed"] is True
    assert result.invariants["waiting_is_not_answered"] is True

def test_handoff_helper_preserves_retry_visibility_without_retry_authority():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k44",
        reason="retry visibility preservation",
    )

    assert result is not None

    retry_result = service.mark_retry_attempt(
        result.orchestration_id,
        last_error="handoff helper retry visibility",
        max_retry_count=2,
    )

    assert (
        retry_result.status
        == RuntimeAcquisitionOrchestrationStatus.WAITING
    )

    assert retry_result.unresolved is False

    assert (
        retry_result.invariants[
            "retry_visibility_is_not_retry_authority"
        ]
        is True
    )

    assert (
        retry_result.invariants[
            "retry_tracking_is_not_retry_execution"
        ]
        is True
    )

    assert (
        retry_result.invariants[
            "retry_execution_is_not_escalation_authority"
        ]
        is True
    )

def test_handoff_helper_does_not_infer_acquisition_success_or_freshness():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k45",
        reason="freshness boundary protection",
    )

    assert result is not None

    assert result.acquisition_request_id is not None

    assert (
        result.status
        == RuntimeAcquisitionOrchestrationStatus.WAITING
    )

    assert result.unresolved is False

    # acquisition request exists,
    # but acquisition success/freshness is NOT inferred

    assert result.invariants["waiting_is_not_answered"] is True
    assert (
        result.invariants[
            "acquisition_request_is_not_acquisition_result"
        ]
        is True
    )

    assert (
        result.invariants[
            "automatic_routing_is_not_automatic_authority"
        ]
        is True
    )

def test_handoff_helper_reuse_does_not_grant_lifecycle_authority():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    first = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k46",
        reason="first helper invocation",
    )

    second = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k46",
        reason="second helper invocation",
    )

    assert first is not None
    assert second is not None

    assert (
        first.status
        == RuntimeAcquisitionOrchestrationStatus.WAITING
    )

    assert (
        second.status
        == RuntimeAcquisitionOrchestrationStatus.WAITING
    )

    assert len(service._states) == 2

    assert (
        first.invariants[
            "automatic_routing_is_not_automatic_authority"
        ]
        is True
    )

    assert (
        second.invariants[
            "automatic_routing_is_not_automatic_authority"
        ]
        is True
    )

def test_handoff_helper_does_not_resolve_unresolved_orchestration_state():
    service = RuntimeAcquisitionOrchestrationService(
        request_builder=RuntimeAcquisitionRequestBuilder(),
        acquisition_bridge=AcquisitionRuntimeBridge(),
        ttl_minutes=30,
    )

    result = handoff_acquisition_to_orchestration(
        coordinator_output=_make_coordinator_output(),
        orchestration_service=service,
        has_acquisition_requests=True,
        variable_code="k47",
        reason="unresolved preservation boundary",
    )

    assert result is not None

    unresolved_result = service.mark_retry_attempt(
        result.orchestration_id,
        last_error="retry limit reached",
        max_retry_count=1,
    )

    assert (
        unresolved_result.status
        == RuntimeAcquisitionOrchestrationStatus.UNRESOLVED
    )

    assert unresolved_result.unresolved is True

    state = service._states[result.orchestration_id]

    assert (
        state.status
        == RuntimeAcquisitionOrchestrationStatus.UNRESOLVED
    )

    assert state.unresolved is True

    assert (
        unresolved_result.invariants[
            "unresolved_is_not_solved"
        ]
        is True
    )