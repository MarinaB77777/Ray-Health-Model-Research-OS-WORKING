# runtime/queue_manager.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from runtime.schemas import (
    GovernanceDecisionStatus,
    RuntimeActionRecord,
    RuntimeRiskLevel,
    RuntimeStatus,
)
from runtime.statuses import is_terminal_status


RISK_PRIORITY = {
    RuntimeRiskLevel.CRITICAL: 5,
    RuntimeRiskLevel.HIGH: 4,
    RuntimeRiskLevel.MEDIUM: 3,
    RuntimeRiskLevel.LOW: 2,
    RuntimeRiskLevel.MINIMAL: 1,
}


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeQueueManager:
    """
    Runtime queue manager.

    Decides queue admission and ordering.

    It does NOT:
    - execute actions
    - override Governance
    - ask humans
    - rewrite Analyst decisions
    """

    def prepare_for_queue(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeActionRecord:

        if is_terminal_status(action.runtime_status):
            return action

        now = utc_now()

        expires_at = _parse_datetime(action.expires_at)

        if expires_at is not None and expires_at <= now:
            action.runtime_status = RuntimeStatus.EXPIRED
            return action

        verdict = action.governance_verdict

        if verdict is not None:

            if (
                verdict.governance_decision_status
                == GovernanceDecisionStatus.BLOCKED
            ):
                action.runtime_status = RuntimeStatus.BLOCKED_BY_GOVERNANCE
                return action

            if (
                verdict.governance_decision_status
                == GovernanceDecisionStatus.NOT_ENOUGH_DATA
            ):
                action.runtime_status = RuntimeStatus.NEEDS_REANALYSIS
                return action

            if verdict.governance_confirmation_required:
                action.runtime_status = RuntimeStatus.AWAITING_HUMAN
                return action

        if action.runtime_status == RuntimeStatus.NOT_STARTED:
            action.runtime_status = RuntimeStatus.QUEUED

        return action

    def sort_queue(
        self,
        actions: List[RuntimeActionRecord],
    ) -> List[RuntimeActionRecord]:

        queueable = [
            action
            for action in actions
            if action.runtime_status == RuntimeStatus.QUEUED
        ]

        return sorted(
            queueable,
            key=self._sort_key,
        )

    def _sort_key(
        self,
        action: RuntimeActionRecord,
    ):
        risk_score = RISK_PRIORITY.get(
            action.risk_level,
            0,
        )

        deadline = _parse_datetime(action.deadline_at)

        return (
            -risk_score,
            deadline or datetime.max.replace(tzinfo=timezone.utc),
        )