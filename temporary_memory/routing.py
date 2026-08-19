from __future__ import annotations

from temporary_memory.schemas import (
    TemporaryMemoryRecord,
    TemporaryMemoryStatus,
    TemporaryMemoryType,
)


class TemporaryMemoryRouter:
    """Compatibility router for Working / Operational Memory.

    It selects only reusable operational records. It does not reason, govern,
    mutate, promote, infer identity, or expose raw Inner Core.
    """

    def __init__(self, records: list[TemporaryMemoryRecord]) -> None:
        self.records = records

    def active_records(self) -> list[TemporaryMemoryRecord]:
        return [record for record in self.records if record.is_reusable()]

    def unresolved_records(self) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self.records
            if record.status == TemporaryMemoryStatus.UNRESOLVED and record.is_reusable()
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

    def _by_type(self, record_type: TemporaryMemoryType) -> list[TemporaryMemoryRecord]:
        return [
            record
            for record in self.active_records()
            if record.record_type == record_type
        ]
