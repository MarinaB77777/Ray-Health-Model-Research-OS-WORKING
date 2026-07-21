# runtime/communication_router.py

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from runtime.schemas import (
    GovernanceDecisionStatus,
    GovernanceTargetAudience,
    RuntimeActionRecord,
)
from runtime.visibility_adapter import apply_runtime_visibility_scope

class RuntimeCommunicationChannel(str, Enum):
    CHAT = "chat"
    VOICE = "voice"

    NOTIFICATION = "notification"
    EMAIL = "email"

    APP = "app"

    EXTERNAL_MESSAGE = "external_message"

    EXTERNAL_AI_REQUEST = "external_ai_request"

    INTERNET_REQUEST = "internet_request"

    EMERGENCY_CHANNEL = "emergency_channel"

    NONE = "none"



class RuntimeDeliveryPlan(BaseModel):
    action_id: str
    channel: RuntimeCommunicationChannel
    target_audience: GovernanceTargetAudience

    deliverable: bool = False
    requires_human_confirmation: bool = False
    blocked: bool = False

    payload: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None
    restrictions: list[str] = Field(default_factory=list)


class CommunicationRouter:
    """
    Runtime communication router.

    Chooses delivery channel only within Governance verdict boundaries.

    It does NOT:
    - decide permissions;
    - expand visibility;
    - bypass confirmation;
    - read raw payload directly for external delivery.
    """

    def build_delivery_plan(
        self,
        action: RuntimeActionRecord,
    ) -> RuntimeDeliveryPlan:
        if action.governance_verdict is None:
            return RuntimeDeliveryPlan(
                action_id=action.action_id,
                channel=RuntimeCommunicationChannel.NONE,
                target_audience=GovernanceTargetAudience.INTERNAL_RAY,
                deliverable=False,
                blocked=True,
                reason="governance_verdict_missing",
            )

        verdict = action.governance_verdict

        if action.human_prohibition_active:
            return RuntimeDeliveryPlan(
                action_id=action.action_id,
                channel=RuntimeCommunicationChannel.NONE,
                target_audience=verdict.governance_target_audience,
                deliverable=False,
                blocked=True,
                reason="human_prohibition_active",
                restrictions=verdict.restrictions,
            )

        if verdict.governance_decision_status == GovernanceDecisionStatus.BLOCKED:
            return RuntimeDeliveryPlan(
                action_id=action.action_id,
                channel=RuntimeCommunicationChannel.NONE,
                target_audience=verdict.governance_target_audience,
                deliverable=False,
                blocked=True,
                reason="governance_blocked",
                restrictions=verdict.restrictions,
            )

        if verdict.governance_decision_status == GovernanceDecisionStatus.NOT_ENOUGH_DATA:
            return RuntimeDeliveryPlan(
                action_id=action.action_id,
                channel=RuntimeCommunicationChannel.NONE,
                target_audience=verdict.governance_target_audience,
                deliverable=False,
                blocked=True,
                reason="governance_not_enough_data",
                restrictions=verdict.restrictions,
            )

        if verdict.governance_confirmation_required:
            return RuntimeDeliveryPlan(
                action_id=action.action_id,
                channel=RuntimeCommunicationChannel.CHAT,
                target_audience=GovernanceTargetAudience.PRIMARY_HUMAN,
                deliverable=False,
                requires_human_confirmation=True,
                blocked=False,
                reason="human_confirmation_required",
                restrictions=verdict.restrictions,
            )

        visible_payload = apply_runtime_visibility_scope(
            action.payload,
            verdict,
        )

        return RuntimeDeliveryPlan(
            action_id=action.action_id,
            channel=self._select_channel(verdict.governance_target_audience),
            target_audience=verdict.governance_target_audience,
            deliverable=True,
            requires_human_confirmation=False,
            blocked=False,
            payload=visible_payload,
            restrictions=verdict.restrictions,
        )


    def _select_channel(
        self,
        target_audience: GovernanceTargetAudience,
    ) -> RuntimeCommunicationChannel:
        if target_audience == GovernanceTargetAudience.PRIMARY_HUMAN:
            return RuntimeCommunicationChannel.CHAT

        if target_audience == GovernanceTargetAudience.INTERNAL_RAY:
            return RuntimeCommunicationChannel.APP

        if target_audience == GovernanceTargetAudience.EMERGENCY_CONTACT:
            return RuntimeCommunicationChannel.EMERGENCY_CHANNEL

        if target_audience == GovernanceTargetAudience.TRUSTED_PERSON:
            return RuntimeCommunicationChannel.EXTERNAL_MESSAGE

        if target_audience == GovernanceTargetAudience.EXTERNAL_PERSON:
            return RuntimeCommunicationChannel.EXTERNAL_MESSAGE

        if target_audience == GovernanceTargetAudience.EXTERNAL_AI:
            return RuntimeCommunicationChannel.EXTERNAL_AI_REQUEST

        if target_audience == GovernanceTargetAudience.INTERNET:
            return RuntimeCommunicationChannel.INTERNET_REQUEST

        return RuntimeCommunicationChannel.NONE
    