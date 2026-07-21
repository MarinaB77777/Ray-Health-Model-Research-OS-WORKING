# runtime/acquisition/service.py

from __future__ import annotations

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    ExposureFilterResult,
    InboundFilterResult,
    ReadinessEvaluation,
)

from runtime.acquisition.exposure_filter import ExposureFilter
from runtime.acquisition.result_filter import ResultFilter
from runtime.acquisition.readiness_checker import ReadinessChecker


class AcquisitionService:
    """
    Acquisition Service.

    This service coordinates acquisition boundary steps.

    It is NOT:
    - Analyst;
    - Governance;
    - Runtime Coordinator;
    - truth authority;
    - answer engine;
    - memory authority;
    - external transport adapter.

    It only coordinates:
    - outbound exposure filtering;
    - inbound result filtering;
    - readiness checking.

    It does not execute external calls.
    It does not build final answers.
    It does not verify truth.
    """

    def __init__(
        self,
        exposure_filter: ExposureFilter | None = None,
        result_filter: ResultFilter | None = None,
        readiness_checker: ReadinessChecker | None = None,
    ) -> None:
        self.exposure_filter = exposure_filter or ExposureFilter()
        self.result_filter = result_filter or ResultFilter()
        self.readiness_checker = readiness_checker or ReadinessChecker()

    def prepare_outbound_request(
        self,
        request: AcquisitionRequest,
        privacy_policy_known: bool = True,
        human_permission_granted: bool = False,
    ) -> ExposureFilterResult:
        return self.exposure_filter.filter_for_external_acquisition(
            request=request,
            privacy_policy_known=privacy_policy_known,
            human_permission_granted=human_permission_granted,
        )

    def process_inbound_result(
        self,
        result: AcquisitionResult,
        domain: str | None = None,
    ) -> InboundFilterResult:
        return self.result_filter.filter_result(
            result=result,
            domain=domain,
        )

    def evaluate_readiness(
        self,
        request: AcquisitionRequest,
    ) -> ReadinessEvaluation:
        return self.readiness_checker.evaluate(request)