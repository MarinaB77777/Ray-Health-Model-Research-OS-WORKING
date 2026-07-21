from typing import Optional

from runtime.analysis_buffer.contracts import (
    AnalysisBufferCleanedResult,
    AnalysisBufferEntry,
    AnalysisBufferStatus,
    AnalysisReadinessLevel,
    MissingInformationRequest,
    utc_now,
)


class AnalysisBufferStore:
    """
    Bounded in-memory Analysis Buffer Store.

    Store is NOT:
    - long-term memory;
    - truth authority;
    - Analyst;
    - Governance;
    - task cancellation authority.

    It stores temporary analytical waiting entries only.
    """

    def __init__(self) -> None:
        self._entries: dict[str, AnalysisBufferEntry] = {}

    def add_entry(
        self,
        entry: AnalysisBufferEntry,
    ) -> AnalysisBufferEntry:
        self._entries[entry.buffer_id] = entry
        return entry

    def get_entry(
        self,
        buffer_id: str,
    ) -> Optional[AnalysisBufferEntry]:
        return self._entries.get(buffer_id)

    def update_entry(
        self,
        entry: AnalysisBufferEntry,
    ) -> AnalysisBufferEntry:
        updated = AnalysisBufferEntry.model_validate(
            entry.model_dump()
        )
        updated.updated_at = utc_now()

        self._entries[updated.buffer_id] = updated
        return updated

    def attach_cleaned_result(
        self,
        buffer_id: str,
        result: AnalysisBufferCleanedResult,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["cleaned_results"].append(result.model_dump())
        data["status"] = AnalysisBufferStatus.RESULT_RECEIVED
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def add_missing_information_request(
        self,
        buffer_id: str,
        request: MissingInformationRequest,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["missing_information_requests"].append(
            request.model_dump()
        )
        data["status"] = AnalysisBufferStatus.NEEDS_MORE_DATA
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def mark_needs_more_data(
        self,
        buffer_id: str,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["status"] = AnalysisBufferStatus.NEEDS_MORE_DATA
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def mark_sufficient_for_analysis(
        self,
        buffer_id: str,
        readiness_level: AnalysisReadinessLevel,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["status"] = AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS
        data["readiness_level"] = readiness_level
        data["sufficient_for_analysis"] = True
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def mark_governance_blocked(
        self,
        buffer_id: str,
        reason: str,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["status"] = AnalysisBufferStatus.BLOCKED_BY_GOVERNANCE
        data["governance_block_reason"] = reason
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def mark_cancelled_by_human(
        self,
        buffer_id: str,
        reason: str,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["status"] = AnalysisBufferStatus.CANCELLED_BY_HUMAN
        data["cancellation_reason"] = reason
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def mark_expired_unresolved(
        self,
        buffer_id: str,
        reason: str,
    ) -> Optional[AnalysisBufferEntry]:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return None

        data = entry.model_dump()
        data["status"] = AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED
        data["expiration_reason"] = reason
        data["updated_at"] = utc_now()

        updated = AnalysisBufferEntry.model_validate(data)
        self._entries[buffer_id] = updated

        return updated

    def list_all(self) -> list[AnalysisBufferEntry]:
        return list(self._entries.values())

    def list_waiting(self) -> list[AnalysisBufferEntry]:
        return [
            entry
            for entry in self._entries.values()
            if entry.status
            in {
                AnalysisBufferStatus.WAITING_FOR_RESULT,
                AnalysisBufferStatus.RESULT_RECEIVED,
                AnalysisBufferStatus.NEEDS_MORE_DATA,
            }
        ]

    def list_sufficient_for_analysis(self) -> list[AnalysisBufferEntry]:
        return [
            entry
            for entry in self._entries.values()
            if entry.status
            == AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS
        ]

    def list_open(self) -> list[AnalysisBufferEntry]:
        return [
            entry
            for entry in self._entries.values()
            if not entry.can_close_waiting_state()
        ]    

    def list_unresolved(self) -> list[AnalysisBufferEntry]:
        return [
            entry
            for entry in self._entries.values()
            if entry.status
            in {
                AnalysisBufferStatus.NEEDS_MORE_DATA,
                AnalysisBufferStatus.EXPIRED_BUT_UNRESOLVED,
            }
        ]

    def remove_entry(
        self,
        buffer_id: str,
    ) -> bool:
        if buffer_id not in self._entries:
            return False

        del self._entries[buffer_id]
        return True