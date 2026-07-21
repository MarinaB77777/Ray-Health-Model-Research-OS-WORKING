# runtime/acquisition/buffer_bridge.py

from __future__ import annotations

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    ExposureFilterResult,
    InboundFilterResult,
    ReadinessEvaluation,
)
from runtime.acquisition.service import AcquisitionService
from runtime.analysis_buffer.contracts import AnalysisBufferEntry


class AcquisitionBufferBridge:
    """
    Analysis Buffer ↔ Acquisition Service bridge.

    This bridge connects analytical waiting state with acquisition boundaries.

    It is NOT:
    - acquisition executor;
    - external transport adapter;
    - answer builder;
    - Analyst;
    - Governance;
    - Runtime Coordinator;
    - truth authority;
    - memory authority.

    buffer_bridge ≠ acquisition executor
    buffer_bridge ≠ answer builder

    Buffer stores and links.
    Acquisition remains separate.
    """

    def __init__(
        self,
        acquisition_service: AcquisitionService | None = None,
    ) -> None:
        self.acquisition_service = (
            acquisition_service or AcquisitionService()
        )

    def prepare_outbound_from_buffer(
        self,
        buffer_entry: AnalysisBufferEntry,
        acquisition_request: AcquisitionRequest,
        privacy_policy_known: bool = True,
        human_permission_granted: bool = False,
    ) -> ExposureFilterResult:
        return self.acquisition_service.prepare_outbound_request(
            request=acquisition_request,
            privacy_policy_known=privacy_policy_known,
            human_permission_granted=human_permission_granted,
        )

    def process_inbound_for_buffer(
        self,
        buffer_entry: AnalysisBufferEntry,
        acquisition_request: AcquisitionRequest,
        raw_external_result: str,
        source_class: AcquisitionSourceClass,
        domain: str | None = None,
    ) -> InboundFilterResult:
        acquisition_result = AcquisitionResult(
            request_id=acquisition_request.request_id,
            source_class=source_class,
            raw_external_result=raw_external_result,
        )

        return self.acquisition_service.process_inbound_result(
            result=acquisition_result,
            domain=domain,
        )

    def evaluate_buffer_readiness(
        self,
        buffer_entry: AnalysisBufferEntry,
        acquisition_request: AcquisitionRequest,
    ) -> ReadinessEvaluation:
        return self.acquisition_service.evaluate_readiness(
            request=acquisition_request,
        )