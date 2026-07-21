from __future__ import annotations

from temporary_memory.schemas import (
    TemporaryMemoryRecord,
    TemporaryMemoryStatus,
    TemporaryMemoryType,
)


class TemporaryMemoryRouter:
    """
    Safe selector layer for Temporary External Memory.

    Router responsibilities:
    - select operational records for Runtime / Planner usage
    - expose unresolved blockers
    - expose awaiting-human records
    - expose next questions
    - expose forecast restrictions

    Router does NOT:
    - reason
    - perform governance decisions
    - mutate records
    - promote records
    - rewrite payloads
    - infer identity or personality
    """

    def __init__(self, records: list[TemporaryMemoryRecord]) -> None:
        self.records = records

    def active_records(self) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self.records
            if record.status == TemporaryMemoryStatus.ACTIVE
        ]

    def unresolved_records(self) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self.records
            if record.status == TemporaryMemoryStatus.UNRESOLVED
        ]

    def next_questions(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.NEXT_QUESTION)

    def blockers(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.BLOCKER)

    def awaiting_human(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.AWAITING_HUMAN)

    def forecast_restrictions(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.FORECAST_RESTRICTION)

    def warnings(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.WARNING)

    def runtime_coordination(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.RUNTIME_COORDINATION)

    def planner_notes(self) -> list[TemporaryMemoryRecord]:
        return self._by_type(TemporaryMemoryType.PLANNER_NOTE)

    def _by_type(
        self,
        record_type: TemporaryMemoryType,
    ) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self.active_records()
            if record.record_type == record_type
        ]