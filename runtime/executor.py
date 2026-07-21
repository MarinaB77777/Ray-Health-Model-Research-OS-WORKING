# runtime/executor.py

from __future__ import annotations

from runtime.event_log import RuntimeEventLog
from runtime.schemas import (
    GovernanceDecisionStatus,
    RuntimeActionRecord,
    RuntimeEventType,
    RuntimeExecutionResult,
    RuntimeStatus,
)
from runtime.statuses import require_valid_transition
from runtime.visibility_adapter import apply_runtime_visibility_scope


class RuntimeExecutor:
    """
    Runtime executor.

    Runtime executes only what Governance already allowed/restricted.
    Runtime does not reason, govern, or expand permissions.
    """

    def __init__(self, event_log: RuntimeEventLog | None = None) -> None:
        self.event_log = event_log or RuntimeEventLog()

    def execute(self, action: RuntimeActionRecord) -> RuntimeExecutionResult:
        if action.human_prohibition_active:
            return self._block_by_human(action)

        if action.governance_verdict is None:
            return self._needs_reanalysis(
                action,
                "Governance verdict missing.",
                "GOVERNANCE_VERDICT_MISSING",
            )

        verdict = action.governance_verdict

        if verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED:
            return self._block_by_governance(action)

        if verdict.governance_decision_status == GovernanceDecisionStatus.NOT_ENOUGH_DATA:
            return self._needs_reanalysis(
                action,
                "Governance returned not_enough_data.",
                "GOVERNANCE_NOT_ENOUGH_DATA",
            )

        if verdict.governance_confirmation_required:
            return self._await_human_confirmation(action)

        return self._execute_allowed_or_restricted(action)

    def _execute_allowed_or_restricted(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeExecutionResult:

        verdict = action.governance_verdict

        if (
            verdict.governance_decision_status
            == GovernanceDecisionStatus.RESTRICTED
        ):
            if not verdict.allowed_action_scopes:
                return self._needs_reanalysis(
                    action,
                    "Restricted action has no allowed action scopes.",
                    "RESTRICTED_ACTION_SCOPE_MISSING",
                )

            action.payload = {
                **action.payload,
                "runtime_allowed_action_scopes": verdict.allowed_action_scopes,
                "runtime_blocked_action_scopes": verdict.blocked_action_scopes,
            }

        previous_status = action.runtime_status
        new_status = RuntimeStatus.EXECUTING



        require_valid_transition(previous_status, new_status)

        start_event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.EXECUTION_STARTED,
            previous_status=previous_status,
            new_status=new_status,
            note="Runtime execution started within Governance scope.",
        )

        filtered_payload = apply_runtime_visibility_scope(
            action.payload,
            action.governance_verdict,
        )

        completed_status = RuntimeStatus.COMPLETED
        require_valid_transition(new_status, completed_status)

        completed_event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.EXECUTION_COMPLETED,
            previous_status=new_status,
            new_status=completed_status,
            payload={
                "delivered_payload": filtered_payload,
                "governance_trace_id": action.governance_verdict.trace_id,
            },
            note="Runtime execution completed.",
        )

        return RuntimeExecutionResult(
            action_id=action.action_id,
            status=completed_status,
            success=True,
            blocked=False,
            message="Execution completed.",
            events=[start_event, completed_event],
        )

    def _await_human_confirmation(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeExecutionResult:
        previous_status = action.runtime_status
        new_status = RuntimeStatus.AWAITING_HUMAN
        require_valid_transition(previous_status, new_status)

        event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.HUMAN_RESPONSE_REQUIRED,
            previous_status=previous_status,
            new_status=new_status,
            note="Governance requires human confirmation before execution.",
        )

        return RuntimeExecutionResult(
            action_id=action.action_id,
            status=new_status,
            success=False,
            blocked=False,
            message="Awaiting human confirmation.",
            events=[event],
            awaiting_human=True,
        )

    def _block_by_governance(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeExecutionResult:
        previous_status = action.runtime_status
        new_status = RuntimeStatus.BLOCKED_BY_GOVERNANCE
        require_valid_transition(previous_status, new_status)

        event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.EXECUTION_FAILED,
            previous_status=previous_status,
            new_status=new_status,
            payload={
                "reason_codes": action.governance_verdict.reason_codes,
                "restrictions": action.governance_verdict.restrictions,
                "governance_trace_id": action.governance_verdict.trace_id,
            },
            note="Execution blocked by Governance.",
        )

        return RuntimeExecutionResult(
            action_id=action.action_id,
            status=new_status,
            success=False,
            blocked=True,
            message="Execution blocked by Governance.",
            error_code="BLOCKED_BY_GOVERNANCE",
            events=[event],
        )

    def _block_by_human(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeExecutionResult:
        previous_status = action.runtime_status
        new_status = RuntimeStatus.BLOCKED_BY_HUMAN
        require_valid_transition(previous_status, new_status)

        event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.EXECUTION_FAILED,
            previous_status=previous_status,
            new_status=new_status,
            note="Execution blocked by active human prohibition.",
        )

        return RuntimeExecutionResult(
            action_id=action.action_id,
            status=new_status,
            success=False,
            blocked=True,
            message="Execution blocked by human prohibition.",
            error_code="BLOCKED_BY_HUMAN",
            events=[event],
        )

    def _needs_reanalysis(
        self,
        action: RuntimeActionRecord,
        message: str,
        error_code: str,
    ) -> RuntimeExecutionResult:
        previous_status = action.runtime_status
        new_status = RuntimeStatus.NEEDS_REANALYSIS
        require_valid_transition(previous_status, new_status)

        event = self.event_log.create_and_append(
            action_id=action.action_id,
            event_type=RuntimeEventType.REANALYSIS_REQUESTED,
            previous_status=previous_status,
            new_status=new_status,
            note=message,
        )

        return RuntimeExecutionResult(
            action_id=action.action_id,
            status=new_status,
            success=False,
            blocked=False,
            message=message,
            error_code=error_code,
            events=[event],
            reanalysis_requested=True,
        )