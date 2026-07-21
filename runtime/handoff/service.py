from typing import Optional

from runtime.handoff.contracts import (
    RuntimeHandoffDecision,
    RuntimeHandoffRequest,
    RuntimeHandoffStatus,
)

from runtime.handoff.registry import (
    HandoffBoundaryRule,
    HandoffCapability,
    HandoffTargetDefinition,
    HandoffTargetRegistry,
    build_default_handoff_registry,
)


class RuntimeHandoffService:
    """
    Bounded Runtime Handoff Service.

    HandoffService performs:
    - registry validation;
    - boundary surfacing;
    - operational handoff preparation.

    HandoffService is NOT:
    - executor;
    - adapter transport;
    - governance;
    - policy evaluator;
    - risk interpreter;
    - truth authority.

    It does not grant permission,
    infer consent, execute calls,
    or verify real-world outcomes.
    """

    def __init__(
        self,
        registry: Optional[HandoffTargetRegistry] = None,
    ) -> None:
        self.registry = registry or build_default_handoff_registry()

    def prepare_handoff(
        self,
        request: RuntimeHandoffRequest,
    ) -> RuntimeHandoffDecision:

        trace = list(request.routing_trace)
        trace.append("handoff_service_received_request")

        target = self.registry.get(request.target_id)

        if target is None:
            trace.append("handoff_target_not_found")

            return RuntimeHandoffDecision(
                handoff_id=request.handoff_id,
                status=RuntimeHandoffStatus.TARGET_NOT_FOUND,
                target_id=request.target_id,
                requested_capability=request.requested_capability,
                explanation="Requested handoff target is not registered.",
                routing_trace=trace,
                uncertainty_notes=request.uncertainty_notes,
            )

        if not target.is_available():
            trace.append("handoff_target_unavailable")

            return RuntimeHandoffDecision(
                handoff_id=request.handoff_id,
                status=RuntimeHandoffStatus.TARGET_UNAVAILABLE,
                target_id=request.target_id,
                requested_capability=request.requested_capability,
                visible_boundary_rules=target.boundary_rules,
                truth_limits=target.truth_limits,
                explanation="Requested handoff target is not available.",
                routing_trace=trace,
                uncertainty_notes=request.uncertainty_notes,
            )

        if request.requested_capability not in target.capabilities:
            trace.append("handoff_capability_not_declared")

            return RuntimeHandoffDecision(
                handoff_id=request.handoff_id,
                status=RuntimeHandoffStatus.CAPABILITY_NOT_DECLARED,
                target_id=request.target_id,
                requested_capability=request.requested_capability,
                visible_boundary_rules=target.boundary_rules,
                truth_limits=target.truth_limits,
                explanation=(
                    "Requested capability is not declared by handoff target."
                ),
                routing_trace=trace,
                uncertainty_notes=request.uncertainty_notes,
            )

        requires_governance = self._requires_governance(
            target=target,
            request=request,
        )

        requires_confirmation = self._requires_confirmation(
            target=target,
            request=request,
        )

        if requires_governance:
            trace.append("handoff_requires_governance")

            return RuntimeHandoffDecision(
                handoff_id=request.handoff_id,
                status=RuntimeHandoffStatus.REQUIRES_GOVERNANCE,
                target_id=request.target_id,
                requested_capability=request.requested_capability,
                requires_governance=True,
                requires_confirmation=requires_confirmation,
                visible_boundary_rules=target.boundary_rules,
                truth_limits=target.truth_limits,
                explanation=(
                    "Handoff target boundary requires Governance review. "
                    "HandoffService does not grant permission."
                ),
                routing_trace=trace,
                uncertainty_notes=request.uncertainty_notes,
            )

        if requires_confirmation:
            trace.append("handoff_requires_confirmation")

            return RuntimeHandoffDecision(
                handoff_id=request.handoff_id,
                status=RuntimeHandoffStatus.REQUIRES_CONFIRMATION,
                target_id=request.target_id,
                requested_capability=request.requested_capability,
                requires_confirmation=True,
                visible_boundary_rules=target.boundary_rules,
                truth_limits=target.truth_limits,
                explanation=(
                    "Handoff target boundary requires explicit confirmation. "
                    "HandoffService does not infer consent."
                ),
                routing_trace=trace,
                uncertainty_notes=request.uncertainty_notes,
            )

        trace.append("handoff_prepared")

        return RuntimeHandoffDecision(
            handoff_id=request.handoff_id,
            status=RuntimeHandoffStatus.PREPARED,
            target_id=request.target_id,
            requested_capability=request.requested_capability,
            visible_boundary_rules=target.boundary_rules,
            truth_limits=target.truth_limits,
            explanation=(
                "Bounded operational handoff prepared. "
                "Prepared does not mean executed, sent, delivered, "
                "successful, verified, or authorized by Governance."
            ),
            routing_trace=trace,
            uncertainty_notes=request.uncertainty_notes,
        )

    def _requires_governance(
        self,
        target: HandoffTargetDefinition,
        request: RuntimeHandoffRequest,
    ) -> bool:
        """
        Surface governance requirement.

        This does NOT perform governance reasoning.
        """

        if request.requires_governance:
            return True

        return any(
            rule in {
                HandoffBoundaryRule.REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE,
                HandoffBoundaryRule.REQUIRES_GOVERNANCE_FOR_SENSITIVE_ACQUISITION,
            }
            for rule in target.boundary_rules
        )

    def _requires_confirmation(
        self,
        target: HandoffTargetDefinition,
        request: RuntimeHandoffRequest,
    ) -> bool:
        """
        Surface confirmation requirement.

        This does NOT infer consent.
        """

        if request.requires_confirmation:
            return True

        if target.requires_confirmation:
            return True

        return any(
            rule
            in {
                HandoffBoundaryRule.REQUIRES_CONFIRMATION_FOR_REAL_WORLD_ACTION,
                HandoffBoundaryRule.REQUIRES_EXPLICIT_MONITORING_CONSENT,
            }
            for rule in target.boundary_rules
        )