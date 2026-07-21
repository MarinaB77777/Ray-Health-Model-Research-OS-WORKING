from __future__ import annotations

from copy import deepcopy
from typing import Optional

from runtime.coordinator.contracts import (
    CoordinationGroup,
    CoordinatorBlockReason,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorStatus,
    utc_now,
)
from runtime.coordinator.lifecycle import validate_transition


class CoordinatorStore:
    """
    Bounded operational store for Runtime Coordinator.

    Store is:
    - current operational state holder;
    - lifecycle-safe updater;
    - explicit storage boundary.

    Store is NOT:
    - audit log;
    - memory;
    - reasoning trail;
    - Runtime decision layer;
    - retry engine;
    - Analyst;
    - Governance;
    - executor;
    - hidden recovery layer.
    """

    def __init__(self) -> None:
        self._records: dict[str, CoordinatorRecord] = {}
        self._groups: dict[str, CoordinationGroup] = {}

    def add_record(
        self,
        record: CoordinatorRecord,
    ) -> CoordinatorRecord:
        if record.coordinator_id in self._records:
            raise ValueError(
                f"CoordinatorRecord already exists: {record.coordinator_id}"
            )

        stored = self._revalidate_record(deepcopy(record))
        self._records[record.coordinator_id] = stored

        return deepcopy(stored)

    def get_record(
        self,
        coordinator_id: str,
    ) -> Optional[CoordinatorRecord]:
        record = self._records.get(coordinator_id)

        if record is None:
            return None

        return deepcopy(record)

    def list_by_action_id(
        self,
        action_id: str,
    ) -> list[CoordinatorRecord]:
        return [
            deepcopy(record)
            for record in self._records.values()
            if record.action_id == action_id
        ]

    def list_by_operation_id(
        self,
        operation_id: str,
    ) -> list[CoordinatorRecord]:
        return [
            deepcopy(record)
            for record in self._records.values()
            if record.operation_id == operation_id
        ]

    def list_by_acquisition_id(
        self,
        acquisition_id: str,
    ) -> list[CoordinatorRecord]:
        return [
            deepcopy(record)
            for record in self._records.values()
            if record.acquisition_id == acquisition_id
        ]

    def update_record_status(
        self,
        coordinator_id: str,
        next_status: CoordinatorStatus,
        block_reason: Optional[CoordinatorBlockReason] = None,
        unresolved: Optional[bool] = None,
    ) -> CoordinatorRecord:
        record = self._require_record_internal(coordinator_id)

        validate_transition(record.status, next_status)

        updates = {
            "status": next_status,
            "updated_at": utc_now(),
        }

        if block_reason is not None:
            updates["block_reason"] = block_reason

        if unresolved is not None:
            updates["unresolved"] = unresolved

        candidate = record.model_copy(update=updates)

        updated = self._revalidate_record(candidate)

        self._records[coordinator_id] = updated
        return deepcopy(updated)

    def append_signal(
        self,
        coordinator_id: str,
        signal: CoordinatorSignal,
    ) -> CoordinatorRecord:
        record = self._require_record_internal(coordinator_id)

        if signal.action_id != record.action_id:
            raise ValueError(
                "CoordinatorSignal.action_id must match record.action_id"
            )

        updated_signals = [*record.signals, deepcopy(signal)]

        candidate = record.model_copy(
            update={
                "signals": updated_signals,
                "last_signal": signal.signal_type,
                "updated_at": utc_now(),
            }
        )

        updated = self._revalidate_record(candidate)

        self._records[coordinator_id] = updated
        return deepcopy(updated)

    def update_record_flags(
        self,
        coordinator_id: str,
        *,
        requires_runtime_action: Optional[bool] = None,
        requires_human_input: Optional[bool] = None,
        requires_governance: Optional[bool] = None,
        requires_analysis: Optional[bool] = None,
    ) -> CoordinatorRecord:
        record = self._require_record_internal(coordinator_id)

        updates = {
            "updated_at": utc_now(),
        }

        if requires_runtime_action is not None:
            updates["requires_runtime_action"] = requires_runtime_action

        if requires_human_input is not None:
            updates["requires_human_input"] = requires_human_input

        if requires_governance is not None:
            updates["requires_governance"] = requires_governance

        if requires_analysis is not None:
            updates["requires_analysis"] = requires_analysis

        candidate = record.model_copy(update=updates)

        updated = self._revalidate_record(candidate)

        self._records[coordinator_id] = updated
        return deepcopy(updated)

    def delete_record(
        self,
        coordinator_id: str,
    ) -> bool:
        return self._records.pop(coordinator_id, None) is not None

    def add_group(
        self,
        group: CoordinationGroup,
    ) -> CoordinationGroup:
        if group.coordination_group_id in self._groups:
            raise ValueError(
                f"CoordinationGroup already exists: {group.coordination_group_id}"
            )

        stored = self._revalidate_group(deepcopy(group))
        self._groups[group.coordination_group_id] = stored

        return deepcopy(stored)

    def get_group(
        self,
        coordination_group_id: str,
    ) -> Optional[CoordinationGroup]:
        group = self._groups.get(coordination_group_id)

        if group is None:
            return None

        return deepcopy(group)

    def update_group_status(
        self,
        coordination_group_id: str,
        next_status: CoordinatorStatus,
        block_reason: Optional[CoordinatorBlockReason] = None,
        unresolved: Optional[bool] = None,
    ) -> CoordinationGroup:
        group = self._require_group_internal(coordination_group_id)

        validate_transition(group.status, next_status)

        updates = {
            "status": next_status,
            "updated_at": utc_now(),
        }

        if block_reason is not None:
            updates["block_reason"] = block_reason

        if unresolved is not None:
            updates["unresolved"] = unresolved

        candidate = group.model_copy(update=updates)

        updated = self._revalidate_group(candidate)

        self._groups[coordination_group_id] = updated
        return deepcopy(updated)

    def delete_group(
        self,
        coordination_group_id: str,
    ) -> bool:
        return self._groups.pop(coordination_group_id, None) is not None

    def _require_record_internal(
        self,
        coordinator_id: str,
    ) -> CoordinatorRecord:
        record = self._records.get(coordinator_id)

        if record is None:
            raise KeyError(f"CoordinatorRecord not found: {coordinator_id}")

        return record

    def _require_group_internal(
        self,
        coordination_group_id: str,
    ) -> CoordinationGroup:
        group = self._groups.get(coordination_group_id)

        if group is None:
            raise KeyError(
                f"CoordinationGroup not found: {coordination_group_id}"
            )

        return group

    @staticmethod
    def _revalidate_record(
        record: CoordinatorRecord,
    ) -> CoordinatorRecord:
        return CoordinatorRecord(**record.model_dump())

    @staticmethod
    def _revalidate_group(
        group: CoordinationGroup,
    ) -> CoordinationGroup:
        return CoordinationGroup(**group.model_dump())