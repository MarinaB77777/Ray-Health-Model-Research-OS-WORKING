# runtime/acquisition/service_with_registry.py

from __future__ import annotations

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionStatus,
    ExposureDecision,
    ExposureFilterResult,
    InboundFilterDecision,
    InboundFilterResult,
    ReadinessEvaluation,
    SufficiencyStatus,
)
from runtime.acquisition.registry import AcquisitionRegistry
from runtime.acquisition.service import AcquisitionService


class AcquisitionServiceWithRegistry:
    """
    Acquisition Service + Registry coordinator.

    This layer coordinates acquisition operational state updates.

    It is NOT:
    - Runtime;
    - Analyst;
    - Governance;
    - autonomous orchestrator;
    - acquisition executor;
    - retry executor;
    - answer builder;
    - truth authority;
    - memory authority.

    prepared ≠ sent
    orientation-safe ≠ blocked
    service_with_registry ≠ executor
    """

    def __init__(
        self,
        registry: AcquisitionRegistry | None = None,
        acquisition_service: AcquisitionService | None = None,
    ) -> None:
        self.registry = registry or AcquisitionRegistry()
        self.acquisition_service = acquisition_service or AcquisitionService()

    def register_request(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionRequest:
        return self.registry.add_request(request)

    def get_request(
        self,
        request_id: str,
    ) -> AcquisitionRequest | None:
        return self.registry.get_request(request_id)

    def prepare_outbound_request(
        self,
        request_id: str,
        privacy_policy_known: bool = True,
        human_permission_granted: bool = False,
    ) -> ExposureFilterResult | None:
        request = self.registry.get_request(request_id)

        if request is None:
            return None

        result = self.acquisition_service.prepare_outbound_request(
            request=request,
            privacy_policy_known=privacy_policy_known,
            human_permission_granted=human_permission_granted,
        )

        if result.decision == ExposureDecision.ALLOWED:
            self.registry.update_outbound_state(
                request_id=request_id,
                outbound_sent=False,
                outbound_source_metadata={
                    "exposure_decision": result.decision.value,
                    "outbound_prepared": True,
                    "outbound_sent": False,
                    "temporary_only": True,
                    "sanitized_request_persisted": False,
                },
            )
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.WAITING,
            )
        else:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.BLOCKED,
            )

        return result

    def process_inbound_result(
        self,
        request_id: str,
        acquisition_result: AcquisitionResult,
        domain: str | None = None,
    ) -> InboundFilterResult | None:
        request = self.registry.get_request(request_id)

        if request is None:
            return None

        self._move_to_result_received_if_needed(request_id)

        result = self.acquisition_service.process_inbound_result(
            result=acquisition_result,
            domain=domain,
        )

        if result.decision in {
            InboundFilterDecision.ALLOWED_FOR_READINESS,
            InboundFilterDecision.ALLOWED_FOR_ORIENTATION,
        }:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.FILTERED,
            )
        else:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.BLOCKED,
            )

        return result

    def apply_cleaned_fields(
        self,
        request_id: str,
        filled_fields: dict,
        extra_filled_fields_metadata: dict | None = None,
    ) -> AcquisitionRequest | None:
        return self.registry.update_filled_fields(
            request_id=request_id,
            filled_fields=filled_fields,
            extra_filled_fields_metadata=extra_filled_fields_metadata,
        )

    def evaluate_readiness(
        self,
        request_id: str,
    ) -> ReadinessEvaluation | None:
        request = self.registry.get_request(request_id)

        if request is None:
            return None

        self._move_to_filtered_if_needed(request_id)

        request = self.registry.get_request(request_id)

        if request is None:
            return None

        result = self.acquisition_service.evaluate_readiness(request)

        if result.sufficiency_status == SufficiencyStatus.INSUFFICIENT:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.NEEDS_MORE_DATA,
            )
            self.registry.update_sufficiency_status(
                request_id=request_id,
                sufficiency_status=SufficiencyStatus.INSUFFICIENT,
            )

        if (
            result.sufficiency_status
            == SufficiencyStatus.BOUNDED_ANALYSIS_READY
        ):
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.SUFFICIENT_FOR_BOUNDED_ANALYSIS,
            )
            self.registry.update_sufficiency_status(
                request_id=request_id,
                sufficiency_status=(
                    SufficiencyStatus.BOUNDED_ANALYSIS_READY
                ),
            )

        return result

    def _move_to_result_received_if_needed(
        self,
        request_id: str,
    ) -> None:
        request = self.registry.get_request(request_id)

        if request is None:
            return

        if request.status == AcquisitionStatus.CREATED:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.WAITING,
            )

        request = self.registry.get_request(request_id)

        if request is None:
            return

        if request.status == AcquisitionStatus.WAITING:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.RESULT_RECEIVED,
            )

    def _move_to_filtered_if_needed(
        self,
        request_id: str,
    ) -> None:
        request = self.registry.get_request(request_id)

        if request is None:
            return

        if request.status in {
            AcquisitionStatus.CREATED,
            AcquisitionStatus.WAITING,
        }:
            self._move_to_result_received_if_needed(request_id)

        request = self.registry.get_request(request_id)

        if request is None:
            return

        if request.status == AcquisitionStatus.RESULT_RECEIVED:
            self.registry.update_status(
                request_id=request_id,
                status=AcquisitionStatus.FILTERED,
            )