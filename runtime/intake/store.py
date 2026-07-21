from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta, timezone

from runtime.intake.contracts import (
    IntakeEvent,
    IntakeLifecycleStatus,
    IntakeTrustStatus,
)

from runtime.intake.router import (
    IntakeRouteResult,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


DEFAULT_INTAKE_TTL_HOURS = 24
DEFAULT_UNRESOLVED_TTL_HOURS = 72


class IntakeRetentionPolicy(BaseModel):
    ttl_hours: int = DEFAULT_INTAKE_TTL_HOURS
    unresolved_ttl_hours: int = DEFAULT_UNRESOLVED_TTL_HOURS

    allow_cleanup: bool = True
    allow_manual_deletion: bool = True
    allow_physical_purge: bool = True

    preserve_unresolved_temporarily: bool = True

    promote_to_memory_allowed: bool = False

    retention_note: Optional[str] = None


class IntakeStoreRecord(BaseModel):
    intake_event: IntakeEvent

    route_result: Optional[IntakeRouteResult] = None

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    last_routed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    discarded_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    purged_at: Optional[datetime] = None

    unresolved: bool = False
    expired: bool = False
    discarded: bool = False
    deleted: bool = False
    purged: bool = False

    retention_policy: IntakeRetentionPolicy = Field(
        default_factory=IntakeRetentionPolicy
    )

    operational_notes: list[str] = Field(default_factory=list)
    coordination_refs: list[str] = Field(default_factory=list)

    def expires_at(self) -> datetime:
        return self.created_at + timedelta(
            hours=self.retention_policy.ttl_hours
        )

    def unresolved_expires_at(self) -> datetime:
        return self.created_at + timedelta(
            hours=self.retention_policy.unresolved_ttl_hours
        )

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or utc_now()

        if self.expired:
            return True

        return now >= self.expires_at()

    def is_unresolved_expired(
        self,
        now: Optional[datetime] = None,
    ) -> bool:
        now = now or utc_now()

        if not self.unresolved:
            return False

        return now >= self.unresolved_expires_at()

    def may_be_marked_expired(
        self,
        now: Optional[datetime] = None,
    ) -> bool:
        now = now or utc_now()

        return (
            not self.deleted
            and not self.purged
            and not self.discarded
            and self.is_expired(now)
        )

    def may_be_cleaned(
        self,
        now: Optional[datetime] = None,
    ) -> bool:
        now = now or utc_now()

        if self.deleted or self.purged:
            return False

        if not self.retention_policy.allow_cleanup:
            return False

        if self.unresolved:
            return self.is_unresolved_expired(now)

        return self.is_expired(now)

    def may_be_deleted(self) -> bool:
        return (
            self.retention_policy.allow_manual_deletion
            and not self.deleted
            and not self.purged
        )

    def may_be_purged(self) -> bool:
        return (
            self.retention_policy.allow_physical_purge
            and self.deleted
            and not self.purged
        )

    def update_timestamp(self) -> None:
        self.updated_at = utc_now()


class IntakeStoreStats(BaseModel):
    total_records: int = 0

    active_records: int = 0
    unresolved_records: int = 0
    unresolved_expired_records: int = 0

    expired_records: int = 0
    discarded_records: int = 0
    deleted_records: int = 0
    purged_records: int = 0

    routed_records: int = 0
    unrouted_records: int = 0


class IntakeStore:
    """
    Runtime Intake Store.

    Operational bounded persistence only.

    Intake Store is NOT:
    - long-term memory;
    - profiling system;
    - dialogue archive;
    - universal truth storage;
    - hidden surveillance layer.

    Retention:
    - bounded;
    - deletable;
    - TTL-aware;
    - unresolved-aware;
    - operational only.

    Important:
    unresolved intake may persist temporarily,
    but must not become a permanent archive.
    """

    def __init__(self) -> None:
        self._records: dict[str, IntakeStoreRecord] = {}

    def add_intake(
        self,
        intake_event: IntakeEvent,
        unresolved: bool = False,
    ) -> IntakeStoreRecord:

        record = IntakeStoreRecord(
            intake_event=intake_event,
            unresolved=unresolved,
        )

        self._records[intake_event.intake_id] = record

        return record

    def get_intake(
        self,
        intake_id: str,
    ) -> Optional[IntakeStoreRecord]:

        return self._records.get(intake_id)

    def attach_route_result(
        self,
        intake_id: str,
        route_result: IntakeRouteResult,
    ) -> Optional[IntakeStoreRecord]:

        record = self.get_intake(intake_id)

        if record is None:
            return None

        record.route_result = route_result
        record.last_routed_at = utc_now()

        record.update_timestamp()

        return record

    def update_lifecycle(
        self,
        intake_id: str,
        lifecycle_status: IntakeLifecycleStatus,
    ) -> Optional[IntakeStoreRecord]:

        record = self.get_intake(intake_id)

        if record is None:
            return None

        record.intake_event.lifecycle_status = lifecycle_status

        if lifecycle_status == IntakeLifecycleStatus.EXPIRED:
            record.expired = True
            record.expired_at = utc_now()

        if lifecycle_status == IntakeLifecycleStatus.DISCARDED:
            record.discarded = True
            record.discarded_at = utc_now()

        record.update_timestamp()

        return record

    def update_trust_status(
        self,
        intake_id: str,
        trust_status: IntakeTrustStatus,
    ) -> Optional[IntakeStoreRecord]:

        record = self.get_intake(intake_id)

        if record is None:
            return None

        record.intake_event.trust_status = trust_status

        record.update_timestamp()

        return record

    def add_coordination_ref(
        self,
        intake_id: str,
        ref_id: str,
    ) -> Optional[IntakeStoreRecord]:

        record = self.get_intake(intake_id)

        if record is None:
            return None

        if ref_id not in record.coordination_refs:
            record.coordination_refs.append(ref_id)

        record.update_timestamp()

        return record

    def add_operational_note(
        self,
        intake_id: str,
        note: str,
    ) -> Optional[IntakeStoreRecord]:

        record = self.get_intake(intake_id)

        if record is None:
            return None

        record.operational_notes.append(note)

        record.update_timestamp()

        return record

    def mark_unresolved(
        self,
        intake_id: str,
        unresolved: bool = True,
    ) -> Optional[IntakeStoreRecord]:

        record = self.get_intake(intake_id)

        if record is None:
            return None

        record.unresolved = unresolved

        record.update_timestamp()

        return record

    def mark_expired_records(
        self,
        now: Optional[datetime] = None,
    ) -> list[str]:

        now = now or utc_now()

        marked_ids: list[str] = []

        for intake_id, record in self._records.items():

            if not record.may_be_marked_expired(now):
                continue

            record.expired = True
            record.expired_at = now
            record.intake_event.lifecycle_status = (
                IntakeLifecycleStatus.EXPIRED
            )
            record.update_timestamp()

            marked_ids.append(intake_id)

        return marked_ids

    def soft_delete_expired(
        self,
        now: Optional[datetime] = None,
    ) -> list[str]:

        now = now or utc_now()

        deleted_ids: list[str] = []

        for intake_id, record in self._records.items():

            if record.deleted or record.purged:
                continue

            if not record.may_be_cleaned(now):
                continue

            record.deleted = True
            record.deleted_at = now
            record.update_timestamp()

            deleted_ids.append(intake_id)

        return deleted_ids

    def purge_deleted(self) -> list[str]:

        purged_ids: list[str] = []

        for intake_id, record in list(self._records.items()):

            if not record.may_be_purged():
                continue

            record.purged = True
            record.purged_at = utc_now()

            del self._records[intake_id]

            purged_ids.append(intake_id)

        return purged_ids

    def delete_intake(
        self,
        intake_id: str,
    ) -> bool:

        record = self.get_intake(intake_id)

        if record is None:
            return False

        if not record.may_be_deleted():
            return False

        record.deleted = True
        record.deleted_at = utc_now()

        record.update_timestamp()

        return True

    def list_unresolved(self) -> list[IntakeStoreRecord]:
        return [
            record
            for record in self._records.values()
            if (
                record.unresolved
                and not record.deleted
                and not record.purged
            )
        ]

    def list_expired(
        self,
        now: Optional[datetime] = None,
    ) -> list[IntakeStoreRecord]:

        now = now or utc_now()

        return [
            record
            for record in self._records.values()
            if (
                not record.deleted
                and not record.purged
                and record.is_expired(now)
            )
        ]

    def list_discarded(self) -> list[IntakeStoreRecord]:
        return [
            record
            for record in self._records.values()
            if (
                record.discarded
                and not record.deleted
                and not record.purged
            )
        ]

    def list_active(
        self,
        now: Optional[datetime] = None,
    ) -> list[IntakeStoreRecord]:

        now = now or utc_now()

        return [
            record
            for record in self._records.values()
            if (
                not record.deleted
                and not record.purged
                and not record.discarded
                and not record.is_expired(now)
            )
        ]

    def stats(
        self,
        now: Optional[datetime] = None,
    ) -> IntakeStoreStats:

        now = now or utc_now()

        records = list(self._records.values())

        return IntakeStoreStats(
            total_records=len(records),

            active_records=sum(
                1 for r in records
                if (
                    not r.deleted
                    and not r.purged
                    and not r.discarded
                    and not r.is_expired(now)
                )
            ),

            unresolved_records=sum(
                1 for r in records
                if (
                    r.unresolved
                    and not r.deleted
                    and not r.purged
                )
            ),

            unresolved_expired_records=sum(
                1 for r in records
                if (
                    r.unresolved
                    and not r.deleted
                    and not r.purged
                    and r.is_unresolved_expired(now)
                )
            ),

            expired_records=sum(
                1 for r in records
                if (
                    not r.deleted
                    and not r.purged
                    and r.is_expired(now)
                )
            ),

            discarded_records=sum(
                1 for r in records
                if (
                    r.discarded
                    and not r.deleted
                    and not r.purged
                )
            ),

            deleted_records=sum(
                1 for r in records
                if r.deleted
            ),

            purged_records=sum(
                1 for r in records
                if r.purged
            ),

            routed_records=sum(
                1 for r in records
                if r.route_result is not None
            ),

            unrouted_records=sum(
                1 for r in records
                if r.route_result is None
            ),
        )