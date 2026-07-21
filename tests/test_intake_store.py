from datetime import timedelta

from runtime.intake.contracts import (
    IntakeEvent,
    IntakeLifecycleStatus,
    IntakePayloadType,
    IntakeSourceMetadata,
    IntakeSourceType,
    IntakeTrustStatus,
)
from runtime.intake.router import (
    IntakeRouteResult,
    RuntimeRoutingDecision,
    RuntimeRoutingStatus,
)
from runtime.intake.store import (
    IntakeStore,
    IntakeRetentionPolicy,
    utc_now,
)


def make_event(intake_id: str = "intake-store-1") -> IntakeEvent:
    return IntakeEvent(
        intake_id=intake_id,
        payload_type=IntakePayloadType.MESSAGE,
        payload={"text": "hello"},
        source=IntakeSourceMetadata(
            source_type=IntakeSourceType.HUMAN_CHAT,
        ),
    )


def make_route_result(intake_id: str = "intake-store-1") -> IntakeRouteResult:
    return IntakeRouteResult(
        intake_id=intake_id,
        routed=True,
        lifecycle_status=IntakeLifecycleStatus.ROUTED,
        trust_status=IntakeTrustStatus.UNVERIFIED,
        routing_decision=RuntimeRoutingDecision(
            routing_status=RuntimeRoutingStatus.ROUTED,
        ),
    )


def test_add_and_get_intake():
    store = IntakeStore()
    event = make_event()

    record = store.add_intake(event)

    loaded = store.get_intake(event.intake_id)

    assert loaded is not None
    assert loaded.intake_event.intake_id == record.intake_event.intake_id


def test_attach_route_result():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    route_result = make_route_result(event.intake_id)

    record = store.attach_route_result(event.intake_id, route_result)

    assert record is not None
    assert record.route_result is not None
    assert record.last_routed_at is not None


def test_update_lifecycle_expired_marks_expired_only():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    record = store.update_lifecycle(
        event.intake_id,
        IntakeLifecycleStatus.EXPIRED,
    )

    assert record is not None
    assert record.expired is True
    assert record.discarded is False
    assert record.expired_at is not None


def test_update_lifecycle_discarded_marks_discarded_only():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    record = store.update_lifecycle(
        event.intake_id,
        IntakeLifecycleStatus.DISCARDED,
    )

    assert record is not None
    assert record.discarded is True
    assert record.expired is False
    assert record.discarded_at is not None


def test_update_trust_status():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    record = store.update_trust_status(
        event.intake_id,
        IntakeTrustStatus.VERIFIED,
    )

    assert record is not None
    assert record.intake_event.trust_status == IntakeTrustStatus.VERIFIED


def test_add_coordination_ref_deduplicates():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    store.add_coordination_ref(event.intake_id, "action-1")
    record = store.add_coordination_ref(event.intake_id, "action-1")

    assert record is not None
    assert record.coordination_refs == ["action-1"]


def test_add_operational_note():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    record = store.add_operational_note(
        event.intake_id,
        "note",
    )

    assert record is not None
    assert record.operational_notes == ["note"]


def test_mark_unresolved():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    record = store.mark_unresolved(event.intake_id, True)

    assert record is not None
    assert record.unresolved is True


def test_list_unresolved_excludes_deleted():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event, unresolved=True)
    store.delete_intake(event.intake_id)

    assert store.list_unresolved() == []


def test_mark_expired_records_marks_ttl_expired():
    store = IntakeStore()
    event = make_event()
    record = store.add_intake(event)
    record.created_at = utc_now() - timedelta(hours=25)

    marked = store.mark_expired_records()

    assert marked == [event.intake_id]
    assert record.expired is True
    assert record.intake_event.lifecycle_status == IntakeLifecycleStatus.EXPIRED


def test_soft_delete_expired_deletes_expired_record():
    store = IntakeStore()
    event = make_event()
    record = store.add_intake(event)
    record.created_at = utc_now() - timedelta(hours=25)

    deleted = store.soft_delete_expired()

    assert deleted == [event.intake_id]
    assert record.deleted is True
    assert record.deleted_at is not None


def test_unresolved_record_is_preserved_until_unresolved_ttl():
    store = IntakeStore()
    event = make_event()
    record = store.add_intake(event, unresolved=True)
    record.created_at = utc_now() - timedelta(hours=25)

    deleted = store.soft_delete_expired()

    assert deleted == []
    assert record.deleted is False


def test_unresolved_record_can_be_cleaned_after_unresolved_ttl():
    store = IntakeStore()
    event = make_event()
    record = store.add_intake(event, unresolved=True)
    record.created_at = utc_now() - timedelta(hours=73)

    deleted = store.soft_delete_expired()

    assert deleted == [event.intake_id]
    assert record.deleted is True


def test_delete_intake_soft_deletes():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)

    deleted = store.delete_intake(event.intake_id)
    record = store.get_intake(event.intake_id)

    assert deleted is True
    assert record is not None
    assert record.deleted is True


def test_purge_deleted_removes_record():
    store = IntakeStore()
    event = make_event()
    store.add_intake(event)
    store.delete_intake(event.intake_id)

    purged = store.purge_deleted()

    assert purged == [event.intake_id]
    assert store.get_intake(event.intake_id) is None


def test_list_active_excludes_ttl_expired():
    store = IntakeStore()
    event = make_event()
    record = store.add_intake(event)
    record.created_at = utc_now() - timedelta(hours=25)

    assert store.list_active() == []


def test_stats_counts_records():
    store = IntakeStore()
    event_1 = make_event("intake-1")
    event_2 = make_event("intake-2")

    store.add_intake(event_1)
    store.add_intake(event_2, unresolved=True)

    stats = store.stats()

    assert stats.total_records == 2
    assert stats.active_records == 2
    assert stats.unresolved_records == 1
    assert stats.unrouted_records == 2


def test_retention_policy_blocks_cleanup():
    store = IntakeStore()
    event = make_event()
    record = store.add_intake(event)
    record.created_at = utc_now() - timedelta(hours=25)
    record.retention_policy = IntakeRetentionPolicy(
        allow_cleanup=False,
    )

    deleted = store.soft_delete_expired()

    assert deleted == []
    assert record.deleted is False