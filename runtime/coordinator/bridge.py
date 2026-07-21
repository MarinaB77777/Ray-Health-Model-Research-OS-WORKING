from __future__ import annotations

from typing import Optional

from runtime.coordinator.contracts import (
    CoordinationGroup,
    CoordinatorBlockReason,
    CoordinatorOutput,
    CoordinatorRecord,
    CoordinatorSignal,
    CoordinatorStatus,
)
from runtime.coordinator.service import CoordinatorService


class RuntimeCoordinatorBridge:
    """
    Ultra-thin boundary adapter between Runtime and CoordinatorService.

    RuntimeCoordinatorBridge is:
    - strict boundary adapter;
    - explicit-call transport layer;
    - bounded coordination state exposure layer.

    RuntimeCoordinatorBridge is NOT:
    - orchestration layer;
    - Runtime lifecycle owner;
    - planner;
    - Analyst;
    - Analyzer;
    - Governance;
    - Retry engine;
    - Acquisition executor;
    - Handoff router;
    - Memory authority;
    - truth authority;
    - answer builder.

    Core invariant:
    CoordinatorBridge transports coordination state.
    CoordinatorBridge does not coordinate reality.

    Dependency rule:
    RuntimeCoordinatorBridge may depend only on CoordinatorService.
    It must not call Acquisition, Retry, Governance, Analyst, Analyzer,
    Handoff, Memory, or Runtime lifecycle mutation directly.
    """

    def __init__(
        self,
        coordinator_service: Optional[CoordinatorService] = None,
    ) -> None:
        self._coordinator_service = (
            coordinator_service or CoordinatorService()
        )

    def create_coordinator(
        self,
        record: CoordinatorRecord,
    ) -> CoordinatorOutput:
        """
        Explicit coordinator creation only.

        No implicit get_or_create.
        No hidden continuation.
        No automatic runtime action lifecycle mutation.
        """

        return self._coordinator_service.create_record(record)

    def get_output(
        self,
        coordinator_id: str,
    ) -> Optional[CoordinatorOutput]:
        """
        Return bounded coordination output.

        No aggregation.
        No summarization.
        No readiness interpretation.
        """

        return self._coordinator_service.get_output(coordinator_id)

    def list_outputs_by_action_id(
        self,
        action_id: str,
    ) -> list[CoordinatorOutput]:
        """
        List coordination outputs for action_id.

        This is NOT aggregation.
        This is NOT overall readiness.
        This is NOT overall routing decision.
        """

        return self._coordinator_service.list_outputs_by_action_id(
            action_id
        )

    def list_outputs_by_operation_id(
        self,
        operation_id: str,
    ) -> list[CoordinatorOutput]:
        return self._coordinator_service.list_outputs_by_operation_id(
            operation_id
        )

    def list_outputs_by_acquisition_id(
        self,
        acquisition_id: str,
    ) -> list[CoordinatorOutput]:
        return self._coordinator_service.list_outputs_by_acquisition_id(
            acquisition_id
        )

    def update_status(
        self,
        coordinator_id: str,
        next_status: CoordinatorStatus,
        block_reason: Optional[CoordinatorBlockReason] = None,
        unresolved: Optional[bool] = None,
    ) -> CoordinatorOutput:
        """
        Explicit lifecycle update request.

        Lifecycle validation is delegated to CoordinatorService/Store.

        This method does NOT:
        - mutate Runtime action lifecycle;
        - infer operational meaning;
        - auto-route signals;
        - auto-recover blocked flows;
        - schedule retries.
        """

        return self._coordinator_service.update_status(
            coordinator_id=coordinator_id,
            next_status=next_status,
            block_reason=block_reason,
            unresolved=unresolved,
        )

    def update_flags(
        self,
        coordinator_id: str,
        *,
        requires_runtime_action: Optional[bool] = None,
        requires_human_input: Optional[bool] = None,
        requires_governance: Optional[bool] = None,
        requires_analysis: Optional[bool] = None,
    ) -> CoordinatorOutput:
        """
        Explicit flag update only.

        No semantic cleanup.
        No hidden correction.
        """

        return self._coordinator_service.update_flags(
            coordinator_id=coordinator_id,
            requires_runtime_action=requires_runtime_action,
            requires_human_input=requires_human_input,
            requires_governance=requires_governance,
            requires_analysis=requires_analysis,
        )

    def append_signal(
        self,
        coordinator_id: str,
        signal: CoordinatorSignal,
    ) -> CoordinatorOutput:
        """
        Append explicit operational signal.

        Signal is transported only.

        Signal is NOT:
        - execution;
        - permission;
        - truth;
        - retry decision;
        - runtime lifecycle mutation.
        """

        return self._coordinator_service.append_signal(
            coordinator_id=coordinator_id,
            signal=signal,
        )

    def create_group(
        self,
        group: CoordinationGroup,
    ) -> CoordinationGroup:
        return self._coordinator_service.create_group(group)

    def get_group(
        self,
        coordination_group_id: str,
    ) -> Optional[CoordinationGroup]:
        return self._coordinator_service.get_group(
            coordination_group_id
        )

    def update_group_status(
        self,
        coordination_group_id: str,
        next_status: CoordinatorStatus,
        block_reason: Optional[CoordinatorBlockReason] = None,
        unresolved: Optional[bool] = None,
    ) -> CoordinationGroup:
        return self._coordinator_service.update_group_status(
            coordination_group_id=coordination_group_id,
            next_status=next_status,
            block_reason=block_reason,
            unresolved=unresolved,
        )

    def delete_coordinator(
        self,
        coordinator_id: str,
    ) -> bool:
        """
        Technical store cleanup only.

        delete ≠ cancel
        delete ≠ resolved
        delete ≠ lifecycle transition
        """

        return self._coordinator_service.delete_record(
            coordinator_id
        )

    def delete_group(
        self,
        coordination_group_id: str,
    ) -> bool:
        """
        Technical store cleanup only.

        delete ≠ cancel
        delete ≠ resolved
        delete ≠ lifecycle transition
        """

        return self._coordinator_service.delete_group(
            coordination_group_id
        )