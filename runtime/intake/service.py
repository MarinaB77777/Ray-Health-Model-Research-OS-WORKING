from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from runtime.intake.contracts import (
    IntakeEvent,
    IntakeLifecycleStatus,
)

from runtime.intake.router import (
    IntakeRouter,
    IntakeRouteResult,
)

from runtime.intake.store import (
    IntakeStore,
    IntakeStoreRecord,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class IntakeServiceResult(BaseModel):
    intake_id: str

    accepted: bool
    stored: bool
    routed: bool

    lifecycle_status: IntakeLifecycleStatus

    route_result: Optional[IntakeRouteResult] = None

    warnings: list[str] = Field(default_factory=list)
    operational_notes: list[str] = Field(default_factory=list)

    processed_at: datetime = Field(default_factory=utc_now)


class IntakeService:
    """
    Runtime Intake Service.

    Coordinates bounded intake flow:

    receive -> store -> route -> attach route result -> return

    IntakeService is NOT:
    - Planner;
    - Analyst;
    - Governance;
    - Memory Writer;
    - Dialogue Runtime;
    - execution authority.

    It does not turn incoming data into truth.

    MVP note:
    accepted=True means the intake event was accepted into the
    bounded intake pipeline, not that its content is trusted,
    verified, approved, or executable.
    """

    def __init__(
        self,
        store: Optional[IntakeStore] = None,
        router: Optional[IntakeRouter] = None,
    ) -> None:
        self.store = store or IntakeStore()
        self.router = router or IntakeRouter()

    def receive(
        self,
        intake_event: IntakeEvent,
        unresolved: bool = False,
    ) -> IntakeServiceResult:

        record = self.store.add_intake(
            intake_event=intake_event,
            unresolved=unresolved,
        )

        route_result = self.router.route(intake_event)

        self.store.attach_route_result(
            intake_id=intake_event.intake_id,
            route_result=route_result,
        )

        self.store.update_lifecycle(
            intake_id=intake_event.intake_id,
            lifecycle_status=route_result.lifecycle_status,
        )

        warnings: list[str] = []

        if route_result.routing_decision.requires_governance:
            warnings.append(
                "Governance required before further runtime action."
            )

        if route_result.routing_decision.requires_human_confirmation:
            warnings.append(
                "Human confirmation required before further routing."
            )

        if not route_result.routed:
            warnings.append(
                "Intake was not routed; uncertainty or boundary preserved."
            )

        operational_notes = [
            "Intake received and stored as operational intake.",
            "Accepted does not mean trusted, verified, approved, or executable.",
            "Route result attached without converting intake into truth.",
        ]

        return IntakeServiceResult(
            intake_id=intake_event.intake_id,
            accepted=True,
            stored=record is not None,
            routed=route_result.routed,
            lifecycle_status=route_result.lifecycle_status,
            route_result=route_result,
            warnings=warnings,
            operational_notes=operational_notes,
        )

    def get_record(
        self,
        intake_id: str,
    ) -> Optional[IntakeStoreRecord]:

        return self.store.get_intake(intake_id)

    def mark_unresolved(
        self,
        intake_id: str,
        unresolved: bool = True,
    ) -> Optional[IntakeStoreRecord]:

        return self.store.mark_unresolved(
            intake_id=intake_id,
            unresolved=unresolved,
        )

    def expire_records(self) -> list[str]:
        return self.store.mark_expired_records()

    def soft_delete_expired(self) -> list[str]:
        return self.store.soft_delete_expired()

    def purge_deleted(self) -> list[str]:
        return self.store.purge_deleted()