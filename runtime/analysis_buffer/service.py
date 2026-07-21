from typing import Optional

from runtime.analysis_buffer.contracts import (
    AnalysisBufferCleanedResult,
    AnalysisBufferEntry,
    AnalysisBufferStatus,
    AnalysisReadinessLevel,
    MissingInformationRequest,
)

from runtime.analysis_buffer.store import AnalysisBufferStore


class AnalysisBufferService:
    """
    Bounded Analysis Buffer Service.

    Service is NOT:
    - Analyst;
    - Governance;
    - truth authority;
    - long-term memory;
    - task cancellation authority.

    It coordinates analytical waiting lifecycle only.
    """

    def __init__(
        self,
        store: Optional[AnalysisBufferStore] = None,
    ) -> None:
        self.store = store or AnalysisBufferStore()

    def add_entry(
        self,
        entry: AnalysisBufferEntry,
    ) -> AnalysisBufferEntry:
        return self.store.add_entry(entry)

    def get_entry(
        self,
        buffer_id: str,
    ) -> Optional[AnalysisBufferEntry]:
        return self.store.get_entry(buffer_id)

    def attach_cleaned_result(
        self,
        buffer_id: str,
        result: AnalysisBufferCleanedResult,
    ) -> Optional[AnalysisBufferEntry]:
        """
        Attaching result does NOT mean sufficient_for_analysis.
        """
        return self.store.attach_cleaned_result(
            buffer_id=buffer_id,
            result=result,
        )

    def add_missing_information_request(
        self,
        buffer_id: str,
        request: MissingInformationRequest,
    ) -> Optional[AnalysisBufferEntry]:
        """
        Missing data triggers acquisition/clarification,
        not invention.
        """
        return self.store.add_missing_information_request(
            buffer_id=buffer_id,
            request=request,
        )

    def mark_needs_more_data(
        self,
        buffer_id: str,
    ) -> Optional[AnalysisBufferEntry]:
        return self.store.mark_needs_more_data(buffer_id)

    def mark_sufficient_for_analysis(
        self,
        buffer_id: str,
        readiness_level: AnalysisReadinessLevel,
    ) -> Optional[AnalysisBufferEntry]:
        """
        Sufficiency is a readiness decision.

        It is NOT:
        - result arrival;
        - verified truth;
        - perfect omniscience.
        """
        if readiness_level not in {
            AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
            AnalysisReadinessLevel.FORECAST_READY,
        }:
            raise ValueError(
                "Sufficiency for analysis requires "
                "BOUNDED_ANALYSIS_READY or FORECAST_READY"
            )

        return self.store.mark_sufficient_for_analysis(
            buffer_id=buffer_id,
            readiness_level=readiness_level,
        )

    def mark_governance_blocked(
        self,
        buffer_id: str,
        reason: str,
    ) -> Optional[AnalysisBufferEntry]:
        return self.store.mark_governance_blocked(
            buffer_id=buffer_id,
            reason=reason,
        )

    def mark_cancelled_by_human(
        self,
        buffer_id: str,
        reason: str,
    ) -> Optional[AnalysisBufferEntry]:
        """
        Human-confirmed cancellation only.

        Silence, timeout, missing data, or technical failure
        must not silently cancel the task.
        """
        return self.store.mark_cancelled_by_human(
            buffer_id=buffer_id,
            reason=reason,
        )

    def mark_expired_unresolved(
        self,
        buffer_id: str,
        reason: str,
    ) -> Optional[AnalysisBufferEntry]:
        """
        Expired unresolved closes waiting operationally,
        but does not fabricate completion or success.
        """
        return self.store.mark_expired_unresolved(
            buffer_id=buffer_id,
            reason=reason,
        )

    def list_open(self) -> list[AnalysisBufferEntry]:
        return self.store.list_open()

    def list_waiting(self) -> list[AnalysisBufferEntry]:
        return self.store.list_waiting()

    def list_unresolved(self) -> list[AnalysisBufferEntry]:
        return self.store.list_unresolved()

    def list_sufficient_for_analysis(self) -> list[AnalysisBufferEntry]:
        return self.store.list_sufficient_for_analysis()

    def can_continue_analysis(
        self,
        buffer_id: str,
    ) -> bool:
        entry = self.get_entry(buffer_id)

        if entry is None:
            return False

        return (
            entry.status == AnalysisBufferStatus.SUFFICIENT_FOR_ANALYSIS
            and entry.sufficient_for_analysis
            and entry.readiness_level
            in {
                AnalysisReadinessLevel.BOUNDED_ANALYSIS_READY,
                AnalysisReadinessLevel.FORECAST_READY,
            }
        )

    def remove_entry(
        self,
        buffer_id: str,
    ) -> bool:
        return self.store.remove_entry(buffer_id)