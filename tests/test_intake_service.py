from datetime import timedelta

from runtime.intake.contracts import (
    IntakeEvent,
    IntakeGovernanceSurface,
    IntakeLifecycleStatus,
    IntakePayloadType,
    IntakeRoutingHints,
    IntakeSourceMetadata,
    IntakeSourceType,
    RuntimeAuthorityBoundary,
    RuntimeTargetLayer,
)
from runtime.intake.router import RuntimeRoutingStatus
from runtime.intake.service import IntakeService
from runtime.intake.store import utc_now


def make_event(
    intake_id: str = "intake-service-1",
    **overrides,
) -> IntakeEvent:
    data = {
        "intake_id": intake_id,
        "payload_type": IntakePayloadType.MESSAGE,
        "payload": {"text": "hello"},
        "source": IntakeSourceMetadata(
            source_type=IntakeSourceType.HUMAN_CHAT,
        ),
    }
    data.update(overrides)
    return IntakeEvent(**data)


def test_receive_stores_intake():
    service = IntakeService()
    event = make_event()

    result = service.receive(event)
    record = service.get_record(event.intake_id)

    assert result.accepted is True
    assert result.stored is True
    assert record is not None
    assert record.intake_event.intake_id == event.intake_id


def test_receive_attaches_route_result():
    service = IntakeService()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        routing_hints=IntakeRoutingHints(
            target_layer=RuntimeTargetLayer.RUNTIME,
        ),
    )

    result = service.receive(event)
    record = service.get_record(event.intake_id)

    assert result.route_result is not None
    assert record is not None
    assert record.route_result is not None
    assert record.last_routed_at is not None


def test_receive_updates_lifecycle_from_route_result():
    service = IntakeService()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        routing_hints=IntakeRoutingHints(
            target_layer=RuntimeTargetLayer.RUNTIME,
        ),
    )

    result = service.receive(event)
    record = service.get_record(event.intake_id)

    assert result.routed is True
    assert result.lifecycle_status == IntakeLifecycleStatus.ROUTED
    assert record is not None
    assert record.intake_event.lifecycle_status == IntakeLifecycleStatus.ROUTED


def test_receive_preserves_not_routed_warning():
    service = IntakeService()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.INTAKE_ONLY,
    )

    result = service.receive(event)

    assert result.routed is False
    assert "Intake was not routed; uncertainty or boundary preserved." in result.warnings


def test_receive_governance_warning():
    service = IntakeService()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        governance_surface=IntakeGovernanceSurface(
            governance_required=True,
        ),
    )

    result = service.receive(event)

    assert result.routed is False
    assert "Governance required before further runtime action." in result.warnings
    assert (
        result.route_result.routing_decision.routing_status
        == RuntimeRoutingStatus.NEEDS_GOVERNANCE
    )


def test_receive_human_confirmation_warning():
    service = IntakeService()
    event = make_event(
        authority_boundary=RuntimeAuthorityBoundary.ROUTING_ALLOWED,
        governance_surface=IntakeGovernanceSurface(
            human_confirmation_required=True,
        ),
    )

    result = service.receive(event)

    assert result.routed is False
    assert "Human confirmation required before further routing." in result.warnings


def test_operational_notes_state_accepted_is_not_trusted():
    service = IntakeService()
    event = make_event()

    result = service.receive(event)

    assert any(
        "Accepted does not mean trusted" in note
        for note in result.operational_notes
    )


def test_mark_unresolved_through_service():
    service = IntakeService()
    event = make_event()
    service.receive(event)

    record = service.mark_unresolved(event.intake_id, True)

    assert record is not None
    assert record.unresolved is True


def test_expire_records_through_service():
    service = IntakeService()
    event = make_event()
    service.receive(event)

    record = service.get_record(event.intake_id)
    assert record is not None
    record.created_at = utc_now() - timedelta(hours=25)

    expired = service.expire_records()

    assert expired == [event.intake_id]
    assert record.expired is True


def test_soft_delete_expired_through_service():
    service = IntakeService()
    event = make_event()
    service.receive(event)

    record = service.get_record(event.intake_id)
    assert record is not None
    record.created_at = utc_now() - timedelta(hours=25)

    deleted = service.soft_delete_expired()

    assert deleted == [event.intake_id]
    assert record.deleted is True


def test_purge_deleted_through_service():
    service = IntakeService()
    event = make_event()
    service.receive(event)

    service.soft_delete_expired()

    record = service.get_record(event.intake_id)
    if record is not None:
        record.created_at = utc_now() - timedelta(hours=25)
        service.soft_delete_expired()

    purged = service.purge_deleted()

    assert isinstance(purged, list)