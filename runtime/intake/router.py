from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from runtime.intake.contracts import (
    IntakeEvent,
    IntakeLifecycleStatus,
    IntakeTrustStatus,
    RuntimeAuthorityBoundary,
    RuntimeTargetLayer,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeRoutingStatus(str, Enum):
    ROUTED = "routed"
    BLOCKED = "blocked"
    NEEDS_CLARIFICATION = "needs_clarification"
    NEEDS_GOVERNANCE = "needs_governance"
    NEEDS_ANALYZER = "needs_analyzer"
    NEEDS_ANALYST = "needs_analyst"
    DISCARDED = "discarded"
    UNROUTABLE = "unroutable"


class RoutingBlockReason(str, Enum):
    LIFECYCLE_BLOCKED = "lifecycle_blocked"
    AUTHORITY_BLOCKED = "authority_blocked"
    GOVERNANCE_REQUIRED = "governance_required"
    HUMAN_CONFIRMATION_REQUIRED = "human_confirmation_required"
    TRUST_CONFLICT = "trust_conflict"
    STALE_EVENT = "stale_event"
    UNKNOWN_TARGET = "unknown_target"
    MISSING_TARGET = "missing_target"
    INVALID_ROUTE = "invalid_route"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class RuntimeRoutingDecision(BaseModel):
    routing_status: RuntimeRoutingStatus

    target_layer: Optional[RuntimeTargetLayer] = None
    target_domain: Optional[str] = None

    block_reason: Optional[RoutingBlockReason] = None
    explanation: Optional[str] = None

    uncertainty_notes: list[str] = Field(default_factory=list)
    conflict_notes: list[str] = Field(default_factory=list)

    requires_governance: bool = False
    requires_human_confirmation: bool = False

    preserve_uncertainty: bool = True


class IntakeRouteResult(BaseModel):
    intake_id: str
    routed: bool

    routing_decision: RuntimeRoutingDecision

    routed_at: datetime = Field(default_factory=utc_now)

    lifecycle_status: IntakeLifecycleStatus
    trust_status: IntakeTrustStatus

    routing_trace: list[str] = Field(default_factory=list)


class IntakeRouter:
    """
    Runtime intake router.

    Responsibilities:
    - validate routing boundaries;
    - preserve uncertainty;
    - prevent hidden authority escalation;
    - prepare bounded routing decisions.

    Router is NOT:
    - Analyst;
    - Governance;
    - execution authority;
    - truth authority;
    - hidden planner.

    Important:
    routing may happen with unverified data only as bounded routing,
    not as verified reality.
    """

    def route(
        self,
        intake_event: IntakeEvent,
    ) -> IntakeRouteResult:

        trace: list[str] = ["intake_received"]

        if intake_event.lifecycle_status in {
            IntakeLifecycleStatus.BLOCKED,
            IntakeLifecycleStatus.EXPIRED,
            IntakeLifecycleStatus.DISCARDED,
        }:
            trace.append("routing_blocked_by_lifecycle")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.BLOCKED,
                    block_reason=RoutingBlockReason.LIFECYCLE_BLOCKED,
                    explanation=(
                        "Runtime must not route blocked, expired, "
                        "or discarded intake."
                    ),
                ),
            )

        if intake_event.authority_boundary == RuntimeAuthorityBoundary.BLOCKED:
            trace.append("routing_blocked_by_authority_boundary")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.BLOCKED,
                    block_reason=RoutingBlockReason.AUTHORITY_BLOCKED,
                    explanation=(
                        "Runtime routing is blocked by authority boundary."
                    ),
                ),
            )

        if intake_event.trust_status == IntakeTrustStatus.CONFLICTING:
            trace.append("trust_conflict_detected")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.NEEDS_CLARIFICATION,
                    block_reason=RoutingBlockReason.TRUST_CONFLICT,
                    explanation=(
                        "Conflicting intake requires clarification "
                        "before bounded routing."
                    ),
                    preserve_uncertainty=True,
                    uncertainty_notes=[
                        "Conflicting source or interpretation detected."
                    ],
                ),
            )

        if intake_event.trust_status == IntakeTrustStatus.STALE:
            trace.append("stale_event_detected")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.BLOCKED,
                    block_reason=RoutingBlockReason.STALE_EVENT,
                    explanation=(
                        "Stale intake must not be silently routed "
                        "as current reality."
                    ),
                    preserve_uncertainty=True,
                ),
            )

        if intake_event.governance_surface.governance_required:
            trace.append("governance_required")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.NEEDS_GOVERNANCE,
                    block_reason=RoutingBlockReason.GOVERNANCE_REQUIRED,
                    explanation=(
                        "Governance validation required before "
                        "further runtime coordination."
                    ),
                    requires_governance=True,
                ),
            )

        if (
            intake_event.governance_surface.human_confirmation_required
            or intake_event.authority_boundary
            == RuntimeAuthorityBoundary.REQUIRES_HUMAN_CONFIRMATION
        ):
            trace.append("human_confirmation_required")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.NEEDS_CLARIFICATION,
                    block_reason=(
                        RoutingBlockReason.HUMAN_CONFIRMATION_REQUIRED
                    ),
                    explanation=(
                        "Explicit human confirmation required "
                        "before routing."
                    ),
                    requires_human_confirmation=True,
                ),
            )

        if intake_event.requires_boundary_check():
            trace.append("boundary_check_required")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.NEEDS_GOVERNANCE,
                    block_reason=RoutingBlockReason.GOVERNANCE_REQUIRED,
                    explanation=(
                        "Boundary-sensitive intake requires governance "
                        "before routing."
                    ),
                    requires_governance=True,
                ),
            )

        if not intake_event.can_runtime_route():
            trace.append("runtime_route_denied")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.BLOCKED,
                    block_reason=RoutingBlockReason.AUTHORITY_BLOCKED,
                    explanation=(
                        "Runtime routing denied by authority boundary."
                    ),
                ),
            )

        target_layer = intake_event.routing_hints.target_layer

        if target_layer is None:
            trace.append("missing_target_layer")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=False,
                lifecycle_status=intake_event.lifecycle_status,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.UNROUTABLE,
                    block_reason=RoutingBlockReason.MISSING_TARGET,
                    explanation=(
                        "Runtime cannot silently invent routing target."
                    ),
                    preserve_uncertainty=True,
                ),
            )

        trace.append(f"target_layer:{target_layer.value}")

        if intake_event.routing_hints.requires_analyzer:
            trace.append("analyzer_requested")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=True,
                lifecycle_status=IntakeLifecycleStatus.ROUTED,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.NEEDS_ANALYZER,
                    target_layer=RuntimeTargetLayer.ANALYZER,
                    target_domain=intake_event.routing_hints.target_domain,
                    explanation="Analyzer evaluation requested.",
                    preserve_uncertainty=True,
                ),
            )

        if intake_event.routing_hints.requires_analyst:
            trace.append("analyst_requested")

            return IntakeRouteResult(
                intake_id=intake_event.intake_id,
                routed=True,
                lifecycle_status=IntakeLifecycleStatus.ROUTED,
                trust_status=intake_event.trust_status,
                routing_trace=trace,
                routing_decision=RuntimeRoutingDecision(
                    routing_status=RuntimeRoutingStatus.NEEDS_ANALYST,
                    target_layer=RuntimeTargetLayer.ANALYST,
                    target_domain=intake_event.routing_hints.target_domain,
                    explanation="Analyst reasoning requested.",
                    preserve_uncertainty=True,
                ),
            )

        trace.append("bounded_route_prepared")

        return IntakeRouteResult(
            intake_id=intake_event.intake_id,
            routed=True,
            lifecycle_status=IntakeLifecycleStatus.ROUTED,
            trust_status=intake_event.trust_status,
            routing_trace=trace,
            routing_decision=RuntimeRoutingDecision(
                routing_status=RuntimeRoutingStatus.ROUTED,
                target_layer=target_layer,
                target_domain=intake_event.routing_hints.target_domain,
                explanation="Bounded runtime routing prepared.",
                preserve_uncertainty=True,
            ),
        )