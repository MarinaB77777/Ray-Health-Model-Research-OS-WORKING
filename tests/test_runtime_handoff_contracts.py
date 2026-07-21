from runtime.handoff.contracts import (
    RuntimeHandoffDirection,
    RuntimeHandoffStatus,
    RuntimeHandoffRequest,
    RuntimeHandoffDecision,
    RuntimeHandoffResult,
    RUNTIME_HANDOFF_INVARIANTS,
)

from runtime.handoff.registry import (
    HandoffCapability,
    HandoffBoundaryRule,
    HandoffTruthLimit,
)


def test_handoff_request_defaults_are_safe():
    request = RuntimeHandoffRequest(
        handoff_id="h1",
        direction=RuntimeHandoffDirection.OUTBOUND,
        target_id="email_adapter",
        requested_capability=(
            HandoffCapability.CALL_EMAIL_ADAPTER
        ),
    )

    assert request.requires_governance is False
    assert request.requires_confirmation is False

    assert request.routing_trace == []
    assert request.uncertainty_notes == []


def test_handoff_decision_preserves_truth_limits():
    decision = RuntimeHandoffDecision(
        handoff_id="h2",
        status=RuntimeHandoffStatus.PREPARED,
        target_id="external_ai",
        requested_capability=(
            HandoffCapability.CALL_EXTERNAL_AI
        ),
        truth_limits=[
            HandoffTruthLimit.EXTERNAL_RESULT_NOT_RAY_TRUTH,
        ],
    )

    assert (
        HandoffTruthLimit.EXTERNAL_RESULT_NOT_RAY_TRUTH
        in decision.truth_limits
    )


def test_handoff_decision_preserves_boundary_rules():
    decision = RuntimeHandoffDecision(
        handoff_id="h3",
        status=RuntimeHandoffStatus.REQUIRES_GOVERNANCE,
        visible_boundary_rules=[
            (
                HandoffBoundaryRule
                .REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE
            ),
        ],
    )

    assert (
        HandoffBoundaryRule
        .REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE
        in decision.visible_boundary_rules
    )


def test_handoff_result_is_not_verified_truth_by_default():
    result = RuntimeHandoffResult(
        handoff_id="h4",
        direction=RuntimeHandoffDirection.INBOUND,
        status=RuntimeHandoffStatus.PREPARED,
        decision=RuntimeHandoffDecision(
            handoff_id="h4",
            status=RuntimeHandoffStatus.PREPARED,
        ),
    )

    assert result.result_is_verified_reality is False
    assert result.result_is_execution_success is False
    assert result.result_is_ray_truth is False


def test_handoff_requires_governance_is_not_allowed_truth():
    decision = RuntimeHandoffDecision(
        handoff_id="h5",
        status=RuntimeHandoffStatus.REQUIRES_GOVERNANCE,
        requires_governance=True,
    )

    assert decision.requires_governance is True

    assert (
        decision.status
        == RuntimeHandoffStatus.REQUIRES_GOVERNANCE
    )


def test_handoff_requires_confirmation_is_not_execution():
    decision = RuntimeHandoffDecision(
        handoff_id="h6",
        status=RuntimeHandoffStatus.REQUIRES_CONFIRMATION,
        requires_confirmation=True,
    )

    assert decision.requires_confirmation is True

    assert (
        decision.status
        == RuntimeHandoffStatus.REQUIRES_CONFIRMATION
    )


def test_bidirectional_handoff_supported():
    outbound = RuntimeHandoffRequest(
        handoff_id="h7",
        direction=RuntimeHandoffDirection.OUTBOUND,
        target_id="communicator",
        requested_capability=(
            HandoffCapability.COMMUNICATE
        ),
    )

    inbound = RuntimeHandoffResult(
        handoff_id="h8",
        direction=RuntimeHandoffDirection.INBOUND,
        status=RuntimeHandoffStatus.PREPARED,
        decision=RuntimeHandoffDecision(
            handoff_id="h8",
            status=RuntimeHandoffStatus.PREPARED,
        ),
    )

    assert (
        outbound.direction
        == RuntimeHandoffDirection.OUTBOUND
    )

    assert (
        inbound.direction
        == RuntimeHandoffDirection.INBOUND
    )


def test_uncertainty_notes_are_preserved():
    result = RuntimeHandoffResult(
        handoff_id="h9",
        direction=RuntimeHandoffDirection.INBOUND,
        status=RuntimeHandoffStatus.PREPARED,
        decision=RuntimeHandoffDecision(
            handoff_id="h9",
            status=RuntimeHandoffStatus.PREPARED,
        ),
        uncertainty_notes=[
            "External system response not independently verified.",
        ],
    )

    assert len(result.uncertainty_notes) == 1


def test_routing_trace_is_preserved():
    result = RuntimeHandoffResult(
        handoff_id="h10",
        direction=RuntimeHandoffDirection.OUTBOUND,
        status=RuntimeHandoffStatus.PREPARED,
        decision=RuntimeHandoffDecision(
            handoff_id="h10",
            status=RuntimeHandoffStatus.PREPARED,
        ),
        routing_trace=[
            "dispatcher_selected_ready_item",
            "coordinator_prepared_handoff",
        ],
    )

    assert (
        "dispatcher_selected_ready_item"
        in result.routing_trace
    )

    assert (
        "coordinator_prepared_handoff"
        in result.routing_trace
    )


def test_handoff_invariants_present():
    invariant_names = {
        invariant.name
        for invariant in RUNTIME_HANDOFF_INVARIANTS
    }

    assert "handoff_is_bidirectional" in invariant_names

    assert (
        "handoff_registry_is_not_governance"
        in invariant_names
    )

    assert "handoff_is_not_execution" in invariant_names

    assert (
        "handoff_result_is_operational_only"
        in invariant_names
    )

    assert (
        "adapter_response_is_not_verified_reality"
        in invariant_names
    )

    assert (
        "truth_limits_must_be_preserved"
        in invariant_names
    )