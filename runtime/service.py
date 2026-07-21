# runtime/service.py

from __future__ import annotations

from typing import Any, Dict, Optional

from runtime.communication_router import CommunicationRouter, RuntimeDeliveryPlan
from runtime.event_log import RuntimeEventLog
from runtime.executor import RuntimeExecutor
from runtime.governance_client import GovernanceClient
from runtime.queue_manager import RuntimeQueueManager
from runtime.schemas import (
    RuntimeActionRecord,
    RuntimeEventType,
    RuntimeExecutionResult,
    RuntimeStatus,
)

class RuntimeService:
    """
    Main Runtime lifecycle service.

    Runtime:
    - reads GovernanceVerdict;
    - obeys GovernanceVerdict;
    - builds delivery plan;
    - executes only allowed/restricted scope;
    - logs lifecycle events.

    Runtime does NOT:
    - reason;
    - govern;
    - modify Analyst decisions;
    - mutate GovernanceVerdict;
    - invent permissions.
    """

    def __init__(
        self,
        governance_client: Optional[GovernanceClient] = None,
        event_log: Optional[RuntimeEventLog] = None,
        communication_router: Optional[CommunicationRouter] = None,
        queue_manager: Optional[RuntimeQueueManager] = None,
        executor: Optional[RuntimeExecutor] = None,
    ) -> None:
        self.event_log = event_log or RuntimeEventLog()
        self.governance_client = governance_client or GovernanceClient()
        self.communication_router = communication_router or CommunicationRouter()
        self.queue_manager = queue_manager or RuntimeQueueManager()
        self.executor = executor or RuntimeExecutor(event_log=self.event_log)

    def process_action(
        self,
        action: RuntimeActionRecord,
        governance_payload: Optional[Dict[str, Any]] = None,
    ) -> RuntimeExecutionResult:
        """
        Main entrypoint.

        If action already has governance_verdict, Runtime uses it.
        If not, Runtime requests one through GovernanceClient.
        """

        self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.ACTION_RECEIVED,
            previous_status=None,
            new_status=action.runtime_status,
            note="Runtime received action.",
        )

        previous_status = action.runtime_status
        action = self.queue_manager.prepare_for_queue(action)

        if action.runtime_status != previous_status:
            self.event_log.create_and_append(
                action_id=action.action_id,
                event_type=RuntimeEventType.ACTION_RECEIVED,
                previous_status=previous_status,
                new_status=action.runtime_status,
                note="Runtime action prepared by queue manager.",
           )

        if action.governance_verdict is None:
            verdict = self.governance_client.get_verdict(
                governance_payload or action.payload
            )
            action.governance_verdict = verdict

            self.event_log.create_and_append(
                action_id=action.action_id,
                event_type=RuntimeEventType.GOVERNANCE_VERDICT_RECEIVED,
                previous_status=action.runtime_status,
                new_status=action.runtime_status,
                payload={
                    "governance_decision_status": verdict.governance_decision_status.value,
                    "governance_visibility_level": verdict.governance_visibility_level.value,
                    "governance_target_audience": verdict.governance_target_audience.value,
                    "governance_confirmation_required": verdict.governance_confirmation_required,
                    "trace_id": verdict.trace_id,
                },
                note="Runtime stored read-only GovernanceVerdict snapshot.",
            )

        delivery_plan = self.communication_router.build_delivery_plan(action)

        if delivery_plan.blocked:
            return self._blocked_from_delivery_plan(action, delivery_plan)

        if delivery_plan.requires_human_confirmation:
            return self.executor.execute(action)

        return self.executor.execute(action)

    def build_delivery_plan(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeDeliveryPlan:
        return self.communication_router.build_delivery_plan(action)

    def get_events_for_action(self, action_id: str):
        return self.event_log.list_for_action(action_id)

    def _blocked_from_delivery_plan(
        self,
        action: RuntimeActionRecord,
        delivery_plan: RuntimeDeliveryPlan,
    ) -> RuntimeExecutionResult:
        if delivery_plan.reason == "human_prohibition_active":
            new_status = RuntimeStatus.BLOCKED_BY_HUMAN
            error_code = "BLOCKED_BY_HUMAN"

        elif delivery_plan.reason == "governance_not_enough_data":
            new_status = RuntimeStatus.NEEDS_REANALYSIS
            error_code = "GOVERNANCE_NOT_ENOUGH_DATA"

        else:
            new_status = RuntimeStatus.BLOCKED_BY_GOVERNANCE
            error_code = "BLOCKED_BY_GOVERNANCE"

        event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.EXECUTION_FAILED,
            previous_status=action.runtime_status,
            new_status=new_status,
            payload={
                "delivery_plan_reason": delivery_plan.reason,
                "restrictions": delivery_plan.restrictions,
            },
            note="Runtime stopped before execution by delivery plan.",
        )

        return RuntimeExecutionResult(
            action_id=action.action_id,
            status=new_status,
            success=False,
            blocked=(
                new_status
                in {
                    RuntimeStatus.BLOCKED_BY_HUMAN,
                    RuntimeStatus.BLOCKED_BY_GOVERNANCE,
                }
            ),
            message=delivery_plan.reason,
            error_code=error_code,
            events=[event],
            reanalysis_requested=(
                new_status == RuntimeStatus.NEEDS_REANALYSIS
            ),
        )