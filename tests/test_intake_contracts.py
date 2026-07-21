from runtime.intake.contracts import (
    IntakeEvent,
    IntakeSourceMetadata,
    IntakeSourceType,
    IntakeTrustStatus,
    IntakeLifecycleStatus,
    IntakePayloadType,
    RuntimeAuthorityBoundary,
)


def build_event() -> IntakeEvent:
    return IntakeEvent(
        intake_id="test-intake-1",
        payload_type=IntakePayloadType.MESSAGE,
        payload={"text": "hello"},
        source=IntakeSourceMetadata(
            source_type=IntakeSourceType.HUMAN_CHAT,
        ),
    )


def test_intake_is_unverified_by_default():

    event = build_event()

    assert (
        event.trust_status
        == IntakeTrustStatus.UNVERIFIED
    )


def test_intake_is_not_trusted_reality_by_default():

    event = build_event()

    assert event.is_trusted_reality() is False


def test_verified_intake_may_become_trusted():

    event = build_event()

    event.trust_status = IntakeTrustStatus.VERIFIED

    assert event.is_trusted_reality() is True


def test_default_lifecycle_is_received():

    event = build_event()

    assert (
        event.lifecycle_status
        == IntakeLifecycleStatus.RECEIVED
    )


def test_default_authority_boundary_is_intake_only():

    event = build_event()

    assert (
        event.authority_boundary
        == RuntimeAuthorityBoundary.INTAKE_ONLY
    )


def test_runtime_route_denied_by_default():

    event = build_event()

    assert event.can_runtime_route() is False


def test_runtime_route_allowed_when_boundary_allows():

    event = build_event()

    event.authority_boundary = (
        RuntimeAuthorityBoundary.ROUTING_ALLOWED
    )

    assert event.can_runtime_route() is True


def test_boundary_check_required_for_governance():

    event = build_event()

    event.governance_surface.governance_required = True

    assert event.requires_boundary_check() is True


def test_boundary_check_required_for_execution_request():

    event = build_event()

    event.governance_surface.execution_requested = True

    assert event.requires_boundary_check() is True


def test_boundary_check_required_for_memory_request():

    event = build_event()

    event.governance_surface.memory_write_requested = True

    assert event.requires_boundary_check() is True


def test_boundary_check_required_for_external_exposure():

    event = build_event()

    event.governance_surface.external_exposure_requested = True

    assert event.requires_boundary_check() is True


def test_boundary_check_required_for_restricted_authority():

    event = build_event()

    event.authority_boundary = (
        RuntimeAuthorityBoundary.REQUIRES_GOVERNANCE
    )

    assert event.requires_boundary_check() is True


def test_boundary_check_not_required_for_simple_intake():

    event = build_event()

    assert event.requires_boundary_check() is False


def test_uncertainty_notes_default_empty():

    event = build_event()

    assert event.uncertainty_notes == []


def test_conflict_notes_default_empty():

    event = build_event()

    assert event.conflict_notes == []