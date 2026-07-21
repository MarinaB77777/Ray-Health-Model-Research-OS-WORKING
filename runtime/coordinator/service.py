from __future__ import annotations

from copy import deepcopy
from typing import Optional

from runtime.coordinator.contracts import (
    CoordinationGroup,
    CoordinatorBlockReason,
    CoordinatorOutput,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorStatus,
)
from runtime.coordinator.store import CoordinatorStore


class CoordinatorService:
    """
    Bounded operational lifecycle service for Runtime Coordinator.

    CoordinatorService is:
    - explicit coordination API over Store;
    - lifecycle-safe operational snapshot layer;
    - bounded operational state exposure layer.

    CoordinatorService is NOT:
    - planner;
    - Analyst;
    - Governance;
    - Runtime lifecycle owner;
    - retry engine;
    - acquisition executor;
    - hidden orchestrator;
    - reasoning layer;
    - truth authority;
    - answer builder.

    Core invariant:
    CoordinatorService may expose operational state.
    CoordinatorService must not decide operational meaning.
    """

    def __init__(
        self,
        store: Optional[CoordinatorStore] = None,
    ) -> None:
        self._store = store or CoordinatorStore()

    def create_record(
        self,
        record: CoordinatorRecord,
    ) -> CoordinatorOutput:
        stored = self._store.add_record(record)
        return self.build_output(stored)

    def get_record(
        self,
        coordinator_id: str,
    ) -> Optional[CoordinatorRecord]:
        return self._store.get_record(coordinator_id)

    def get_output(
        self,
        coordinator_id: str,
    ) -> Optional[CoordinatorOutput]:
        record = self._store.get_record(coordinator_id)

        if record is None:
            return None

        return self.build_output(record)

    def list_outputs_by_action_id(
        self,
        action_id: str,
    ) -> list[CoordinatorOutput]:
        return [
            self.build_output(record)
            for record in self._store.list_by_action_id(action_id)
        ]

    def list_outputs_by_operation_id(
        self,
        operation_id: str,
    ) -> list[CoordinatorOutput]:
        return [
            self.build_output(record)
            for record in self._store.list_by_operation_id(operation_id)
        ]

    def list_outputs_by_acquisition_id(
        self,
        acquisition_id: str,
    ) -> list[CoordinatorOutput]:
        return [
            self.build_output(record)
            for record in self._store.list_by_acquisition_id(acquisition_id)
        ]

    def update_status(
        self,
        coordinator_id: str,
        next_status: CoordinatorStatus,
        block_reason: Optional[CoordinatorBlockReason] = None,
        unresolved: Optional[bool] = None,
    ) -> CoordinatorOutput:
        updated = self._store.update_record_status(
            coordinator_id=coordinator_id,
            next_status=next_status,
            block_reason=block_reason,
            unresolved=unresolved,
        )
        return self.build_output(updated)

    def update_flags(
        self,
        coordinator_id: str,
        *,
        requires_runtime_action: Optional[bool] = None,
        requires_human_input: Optional[bool] = None,
        requires_governance: Optional[bool] = None,
        requires_analysis: Optional[bool] = None,
    ) -> CoordinatorOutput:
        updated = self._store.update_record_flags(
            coordinator_id=coordinator_id,
            requires_runtime_action=requires_runtime_action,
            requires_human_input=requires_human_input,
            requires_governance=requires_governance,
            requires_analysis=requires_analysis,
        )
        return self.build_output(updated)

    def append_signal(
        self,
        coordinator_id: str,
        signal: CoordinatorSignal,
    ) -> CoordinatorOutput:
        updated = self._store.append_signal(
            coordinator_id=coordinator_id,
            signal=signal,
        )
        return self.build_output(updated)

    def delete_record(
        self,
        coordinator_id: str,
    ) -> bool:
        return self._store.delete_record(coordinator_id)

    def create_group(
        self,
        group: CoordinationGroup,
    ) -> CoordinationGroup:
        return self._store.add_group(group)

    def get_group(
        self,
        coordination_group_id: str,
    ) -> Optional[CoordinationGroup]:
        return self._store.get_group(coordination_group_id)

    def update_group_status(
        self,
        coordination_group_id: str,
        next_status: CoordinatorStatus,
        block_reason: Optional[CoordinatorBlockReason] = None,
        unresolved: Optional[bool] = None,
    ) -> CoordinationGroup:
        return self._store.update_group_status(
            coordination_group_id=coordination_group_id,
            next_status=next_status,
            block_reason=block_reason,
            unresolved=unresolved,
        )

    def delete_group(
        self,
        coordination_group_id: str,
    ) -> bool:
        return self._store.delete_group(coordination_group_id)

    @staticmethod
    def build_output(
        record: CoordinatorRecord,
    ) -> CoordinatorOutput:
        """
        Mechanical projection only.

        CoordinatorRecord -> CoordinatorOutput.

        No inference.
        No routing decision.
        No retry decision.
        No cleanup.
        No semantic repair.
        """

        return CoordinatorOutput(
            coordinator_id=record.coordinator_id,
            action_id=record.action_id,
            status=record.status,
            operation_id=record.operation_id,
            acquisition_id=record.acquisition_id,
            coordination_group_id=record.coordination_group_id,
            ready_for_next_route=(
                record.status == CoordinatorStatus.READY_FOR_ROUTING
            ),
            signals=deepcopy(record.signals),
            block_reason=record.block_reason,
            requires_runtime_action=record.requires_runtime_action,
            requires_human_input=record.requires_human_input,
            requires_governance=record.requires_governance,
            requires_analysis=record.requires_analysis,
            unresolved=record.unresolved,
            warnings=[],
            metadata=deepcopy(record.metadata),
        )