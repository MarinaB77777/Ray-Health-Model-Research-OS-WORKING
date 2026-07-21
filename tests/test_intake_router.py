
from runtime.intake.contracts import (
    IntakeEvent,
    IntakeGovernanceSurface,
    IntakeLifecycleStatus,
    IntakePayloadType,
    IntakeRoutingHints,
    IntakeSourceMetadata,
    IntakeSourceType,
    IntakeTrustStatus,
    RuntimeAuthorityBoundary,
    RuntimeTargetLayer,
)
from runtime.intake.router import (
    IntakeRouter,
    RoutingBlockReason,
    RuntimeRoutingStatus,
)


def make_event(**overrides) -> IntakeEvent:
    data = {
        "intake_id": "intake-router-1",
        "payload_type": IntakePayloadType.MESSAGE,
        "payload": {"text": "hello"},
        "source": IntakeSourceMetadata(
            source_type=IntakeSourceType.HUMAN_CHAT,
        ),
    }
    data.update(overrides)
    return IntakeEvent(**data)


def test_blocked_lifecycle_is_not_routed():
    router = IntakeRouter()
    event = make_event(
        lifecycle_status=IntakeLifecycleStatus.BLOCKED,
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.BLOCKED
    assert result.routing_decision.block_reason == RoutingBlockReason.LIFECYCLE_BLOCKED


def test_authority_blocked_is_not_routed():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.BLOCKED,
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.block_reason == RoutingBlockReason.AUTHORITY_BLOCKED


def test_conflicting_intake_requires_clarification():
    router = IntakeRouter()
    event = make_event(
        trust_status=IntakeTrustStatus.CONFLICTING,
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.NEEDS_CLARIFICATION
    assert result.routing_decision.block_reason == RoutingBlockReason.TRUST_CONFLICT
    assert result.routing_decision.preserve_uncertainty is True


def test_stale_intake_is_blocked():
    router = IntakeRouter()
    event = make_event(
        trust_status=IntakeTrustStatus.STALE,
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.BLOCKED
    assert result.routing_decision.block_reason == RoutingBlockReason.STALE_EVENT


def test_governance_required_routes_to_governance_need():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        governance_surface=IntakeGovernanceSurface(
            governance_required=True,
        ),
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.NEEDS_GOVERNANCE
    assert result.routing_decision.requires_governance is True


def test_human_confirmation_required_blocks_routing():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        governance_surface=IntakeGovernanceSurface(
            human_confirmation_required=True,
        ),
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.NEEDS_CLARIFICATION
    assert result.routing_decision.requires_human_confirmation is True


def test_runtime_route_denied_when_boundary_intake_only():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.INTAKE_ONLY,
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.BLOCKED
    assert result.routing_decision.block_reason == RoutingBlockReason.AUTHORITY_BLOCKED


def test_missing_target_layer_is_unroutable():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
    )

    result = router.route(event)

    assert result.routed is False
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.UNROUTABLE
    assert result.routing_decision.block_reason == RoutingBlockReason.MISSING_TARGET


def test_bounded_route_is_prepared():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        routing_hints=IntakeRoutingHints(
            target_layer=RuntimeTargetLayer.RUNTIME,
        ),
    )

    result = router.route(event)

    assert result.routed is True
    assert result.lifecycle_status == IntakeLifecycleStatus.ROUTED
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.ROUTED
    assert result.routing_decision.target_layer == RuntimeTargetLayer.RUNTIME


def test_analyzer_request_routes_to_analyzer():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        routing_hints=IntakeRoutingHints(
            target_layer=RuntimeTargetLayer.RUNTIME,
            requires_analyzer=True,
        ),
    )

    result = router.route(event)

    assert result.routed is True
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.NEEDS_ANALYZER
    assert result.routing_decision.target_layer == RuntimeTargetLayer.ANALYZER


def test_analyst_request_routes_to_analyst():
    router = IntakeRouter()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        routing_hints=IntakeRoutingHints(
            target_layer=RuntimeTargetLayer.RUNTIME,
            requires_analyst=True,
        ),
    )

    result = router.route(event)

    assert result.routed is True
    assert result.routing_decision.routing_status == RuntimeRoutingStatus.NEEDS_ANALYST
    assert result.routing_decision.target_layer == RuntimeTargetLayer.ANALYST