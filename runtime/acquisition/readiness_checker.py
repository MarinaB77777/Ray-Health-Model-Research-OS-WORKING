# runtime/acquisition/readiness_checker.py

from __future__ import annotations

from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionRequest,
    ReadinessEvaluation,
    SufficiencyStatus,
)


class ReadinessChecker:
    """
    Acquisition Readiness Checker.

    This module evaluates whether collected acquisition data is sufficient
    for the next analytical step.

    It is NOT:
    - Analyst;
    - Governance;
    - truth authority;
    - answer engine;
    - memory authority;
    - result sanitizer;
    - acquisition executor.

    Readiness means:
    enough structured information for a declared next step.

    Readiness does NOT mean:
    truth,
    verification,
    permission,
    final answer,
    forecast approval,
    or task completion.
    """

    def evaluate(
        self,
        request: AcquisitionRequest,
    ) -> ReadinessEvaluation:
        missing_fields = self._get_missing_required_fields(request)

        if missing_fields:
            return ReadinessEvaluation(
                request_id=request.request_id,
                sufficiency_status=SufficiencyStatus.INSUFFICIENT,
                missing_required_fields=missing_fields,
                allowed_next_step="ask_or_acquire_missing_fields",
                reason_codes=[
                    AcquisitionReasonCode.MISSING_REQUIRED_FIELDS,
                    AcquisitionReasonCode.NO_DATA_ASK_OR_ACQUIRE,
                ],
                readiness_metadata={
                    "ready_for_analysis": False,
                    "ready_for_forecast": False,
                    "missing_count": len(missing_fields),
                },
            )

        return ReadinessEvaluation(
            request_id=request.request_id,
            sufficiency_status=SufficiencyStatus.BOUNDED_ANALYSIS_READY,
            allowed_next_step="analyst_answer_builder",
            reason_codes=[
                AcquisitionReasonCode.CLEANED_NOT_TRUSTED,
                AcquisitionReasonCode.TRUSTED_NOT_VERIFIED,
            ],
            readiness_metadata={
                "ready_for_analysis": True,
                "ready_for_forecast": False,
                "forecast_not_granted_by_this_checker": True,
            },
        )

    def _get_missing_required_fields(
        self,
        request: AcquisitionRequest,
    ) -> list[str]:
        return [
            field
            for field in request.required_fields
            if field not in request.filled_fields
            or request.filled_fields[field] in (None, "")
        ]