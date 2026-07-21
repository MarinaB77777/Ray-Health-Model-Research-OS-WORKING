from runtime.handoff.contracts import (
    RuntimeHandoffDirection,
    RuntimeHandoffRequest,
    RuntimeHandoffStatus,
)

from runtime.handoff.registry import (
    HandoffCapability,
    HandoffBoundaryRule,
    HandoffTargetDefinition,
    HandoffTargetRegistry,
    HandoffTargetStatus,
    HandoffTargetType,
    HandoffTruthLimit,
    build_default_handoff_registry,
)

from runtime.handoff.service import RuntimeHandoffService


def make_request(
    handoff_id: str = "h1",
    target_id: str = "communicator",
    capability: HandoffCapability = HandoffCapability.COMMUNICATE,
) -> RuntimeHandoffRequest:
    return RuntimeHandoffRequest(
        handoff_id=handoff_id,
        direction=RuntimeHandoffDirection.OUTBOUND,
        target_id=target_id,
        requested_capability=capability,
        routing_trace=["coordinator_prepared_handoff"],
        uncertainty_notes=["source not verified"],
    )


def test_prepare_handoff_target_not_found():
    service = RuntimeHandoffService(
        registry=HandoffTargetRegistry(),
    )

    decision = service.prepare_handoff(
        make_request(target_id="missing_target")
    )

    assert decision.status == RuntimeHandoffStatus.TARGET_NOT_FOUND
    assert "handoff_target_not_found" in decision.routing_trace


def test_prepare_handoff_target_unavailable():
    registry = HandoffTargetRegistry()

    registry.register(
        HandoffTargetDefinition(
            target_id="disabled_email",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[HandoffCapability.CALL_EMAIL_ADAPTER],
            boundary_rules=[HandoffBoundaryRule.NO_DIRECT_EXECUTION],
            truth_limits=[
                HandoffTruthLimit.EMAIL_SENT_NOT_PROBLEM_SOLVED,
            ],
            status=HandoffTargetStatus.DISABLED,
        )
    )

    service = RuntimeHandoffService(registry=registry)

    decision = service.prepare_handoff(
        make_request(
            target_id="disabled_email",
            capability=HandoffCapability.CALL_EMAIL_ADAPTER,
        )
    )

    assert decision.status == RuntimeHandoffStatus.TARGET_UNAVAILABLE
    assert decision.truth_limits == [
        HandoffTruthLimit.EMAIL_SENT_NOT_PROBLEM_SOLVED
    ]


def test_prepare_handoff_capability_not_declared():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="communicator",
            capability=HandoffCapability.CALL_EMAIL_ADAPTER,
        )
    )

    assert decision.status == RuntimeHandoffStatus.CAPABILITY_NOT_DECLARED
    assert "handoff_capability_not_declared" in decision.routing_trace


def test_external_ai_requires_governance():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="external_ai",
            capability=HandoffCapability.CALL_EXTERNAL_AI,
        )
    )

    assert decision.status == RuntimeHandoffStatus.REQUIRES_GOVERNANCE
    assert decision.requires_governance is True
    assert (
        HandoffBoundaryRule.REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE
        in decision.visible_boundary_rules
    )


def test_sensor_acquisition_requires_sensitive_governance():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="sensor_acquisition",
            capability=HandoffCapability.REQUEST_SENSOR_ACQUISITION,
        )
    )

    assert decision.status == RuntimeHandoffStatus.REQUIRES_GOVERNANCE
    assert decision.requires_governance is True
    assert (
        HandoffBoundaryRule.REQUIRES_GOVERNANCE_FOR_SENSITIVE_ACQUISITION
        in decision.visible_boundary_rules
    )


def test_continuous_monitoring_requires_governance_and_confirmation():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="continuous_monitoring",
            capability=HandoffCapability.REQUEST_CONTINUOUS_MONITORING,
        )
    )

    assert decision.status == RuntimeHandoffStatus.REQUIRES_GOVERNANCE
    assert decision.requires_governance is True
    assert decision.requires_confirmation is True
    assert (
        HandoffBoundaryRule.REQUIRES_EXPLICIT_MONITORING_CONSENT
        in decision.visible_boundary_rules
    )


def test_email_adapter_requires_confirmation_without_governance():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="email_adapter",
            capability=HandoffCapability.CALL_EMAIL_ADAPTER,
        )
    )

    assert decision.status == RuntimeHandoffStatus.REQUIRES_CONFIRMATION
    assert decision.requires_confirmation is True
    assert decision.requires_governance is False


def test_communicator_handoff_prepared():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="communicator",
            capability=HandoffCapability.COMMUNICATE,
        )
    )

    assert decision.status == RuntimeHandoffStatus.PREPARED
    assert "handoff_prepared" in decision.routing_trace
    assert decision.truth_limits


def test_request_flag_requires_governance_even_if_target_simple():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    request = make_request(
        target_id="communicator",
        capability=HandoffCapability.COMMUNICATE,
    )
    request.requires_governance = True

    decision = service.prepare_handoff(request)

    assert decision.status == RuntimeHandoffStatus.REQUIRES_GOVERNANCE
    assert decision.requires_governance is True


def test_request_flag_requires_confirmation_even_if_target_simple():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    request = make_request(
        target_id="communicator",
        capability=HandoffCapability.COMMUNICATE,
    )
    request.requires_confirmation = True

    decision = service.prepare_handoff(request)

    assert decision.status == RuntimeHandoffStatus.REQUIRES_CONFIRMATION
    assert decision.requires_confirmation is True


def test_handoff_preserves_trace_and_uncertainty():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="communicator",
            capability=HandoffCapability.COMMUNICATE,
        )
    )

    assert decision.routing_trace == [
        "coordinator_prepared_handoff",
        "handoff_service_received_request",
        "handoff_prepared",
    ]

    assert decision.uncertainty_notes == ["source not verified"]


def test_prepared_does_not_mean_execution_success():
    service = RuntimeHandoffService(
        registry=build_default_handoff_registry()
    )

    decision = service.prepare_handoff(
        make_request(
            target_id="communicator",
            capability=HandoffCapability.COMMUNICATE,
        )
    )

    assert decision.status == RuntimeHandoffStatus.PREPARED
    assert decision.explanation is not None
    assert "does not mean executed" in decision.explanation