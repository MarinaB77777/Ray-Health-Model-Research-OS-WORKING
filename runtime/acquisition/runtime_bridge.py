from __future__ import annotations

from uuid import uuid4

from runtime.contracts.runtime_acquisition_request import (
    RuntimeAcquisitionRequest,
    RuntimeAcquisitionRequestStatus,
    RuntimeAcquisitionRequestType,
)

from runtime.acquisition.contracts import (
    AcquisitionReasonCode,
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    ExposureFilterResult,
    InboundFilterResult,
    ReadinessEvaluation,
)
from runtime.acquisition.service_with_registry import (
    AcquisitionServiceWithRegistry,
)


class AcquisitionRuntimeBridge:
    """
    Runtime ↔ Acquisition bridge.

    This bridge gives Runtime a bounded interface to the acquisition subsystem.

    It is NOT:
    - Analyst;
    - Governance;
    - answer builder;
    - retry executor;
    - acquisition transport;
    - truth authority;
    - memory authority;
    - autonomous orchestrator.

    Runtime asks for acquisition coordination.
    Acquisition returns bounded operational outputs.

    runtime_bridge ≠ Analyst
    runtime_bridge ≠ Governance
    runtime_bridge ≠ executor
    runtime_bridge ≠ answer builder

    RuntimeAcquisitionRequest ≠ permission.
    RuntimeAcquisitionRequest ≠ acquisition result.
    PREPARED ≠ sent.
    PREPARED ≠ executed.

    Source class rule:
    Runtime bridge must not infer ambiguous source class.
    Unknown source_class ≠ inferred operational truth.
    """

    def __init__(
        self,
        acquisition_service: AcquisitionServiceWithRegistry | None = None,
    ) -> None:
        self.acquisition_service = (
            acquisition_service or AcquisitionServiceWithRegistry()
        )

    def create_from_runtime_request(
        self,
        runtime_request: RuntimeAcquisitionRequest,
    ) -> AcquisitionRequest:
        """
        Convert explicit Runtime acquisition intent into internal
        AcquisitionRequest and register it.

        This method does NOT:
        - send acquisition externally;
        - execute acquisition;
        - grant permission;
        - prove acquisition success;
        - perform retry;
        - mutate Coordinator state;
        - mutate Runtime lifecycle.

        RuntimeAcquisitionRequest ≠ permission.
        RuntimeAcquisitionRequest ≠ acquisition result.
        PREPARED ≠ sent.
        PREPARED ≠ executed.
        """

        if runtime_request.status != RuntimeAcquisitionRequestStatus.PREPARED:
            raise ValueError(
                "Only PREPARED RuntimeAcquisitionRequest can be converted "
                "to AcquisitionRequest"
            )

        source_class = self._resolve_source_class(runtime_request)

        acquisition_request = AcquisitionRequest(
            request_id=f"acq-{uuid4()}",
            raw_internal_question_ref=runtime_request.runtime_request_id,
            source_class=source_class,
            domain=runtime_request.metadata.get("domain"),
            importance_level=runtime_request.metadata.get("importance_level"),
            risk_level=runtime_request.metadata.get("risk_level"),
            required_fields=list(runtime_request.required_fields),
            reason_codes=[
                AcquisitionReasonCode.NO_DATA_ASK_OR_ACQUIRE,
            ],
        )

        return self.acquisition_service.register_request(
            acquisition_request
        )

    def create_acquisition_request(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionRequest:
        return self.acquisition_service.register_request(request)

    def get_acquisition_request(
        self,
        request_id: str,
    ) -> AcquisitionRequest | None:
        return self.acquisition_service.get_request(request_id)

    def prepare_external_acquisition(
        self,
        request_id: str,
        privacy_policy_known: bool = True,
        human_permission_granted: bool = False,
    ) -> ExposureFilterResult | None:
        return self.acquisition_service.prepare_outbound_request(
            request_id=request_id,
            privacy_policy_known=privacy_policy_known,
            human_permission_granted=human_permission_granted,
        )

    def receive_external_result(
        self,
        request_id: str,
        acquisition_result: AcquisitionResult,
        domain: str | None = None,
    ) -> InboundFilterResult | None:
        return self.acquisition_service.process_inbound_result(
            request_id=request_id,
            acquisition_result=acquisition_result,
            domain=domain,
        )

    def apply_acquired_fields(
        self,
        request_id: str,
        filled_fields: dict,
        extra_filled_fields_metadata: dict | None = None,
    ) -> AcquisitionRequest | None:
        return self.acquisition_service.apply_cleaned_fields(
            request_id=request_id,
            filled_fields=filled_fields,
            extra_filled_fields_metadata=extra_filled_fields_metadata,
        )

    def evaluate_acquisition_readiness(
        self,
        request_id: str,
    ) -> ReadinessEvaluation | None:
        return self.acquisition_service.evaluate_readiness(
            request_id=request_id,
        )

    @staticmethod
    def _resolve_source_class(
        runtime_request: RuntimeAcquisitionRequest,
    ) -> AcquisitionSourceClass:
        if (
            runtime_request.requested_acquisition_type
            == RuntimeAcquisitionRequestType.DIALOGUE_QUESTION
        ):
            return AcquisitionSourceClass.HUMAN_PRIMARY

        if (
            runtime_request.requested_acquisition_type
            == RuntimeAcquisitionRequestType.SENSOR_DATA
        ):
            return AcquisitionSourceClass.SENSOR

        if (
            runtime_request.requested_acquisition_type
            == RuntimeAcquisitionRequestType.CONTEXT_LOOKUP
        ):
            return AcquisitionSourceClass.INTERNAL_RAY_LAYER

        if runtime_request.requested_acquisition_type in {
            RuntimeAcquisitionRequestType.EXTERNAL_SOURCE_LOOKUP,
            RuntimeAcquisitionRequestType.CALIBRATION_TASK,
        }:
            source_class_value = runtime_request.policy_context.get(
                "source_class"
            )

            if source_class_value is None:
                raise ValueError(
                    f"{runtime_request.requested_acquisition_type.value} "
                    "requires policy_context['source_class']"
                )

            try:
                return AcquisitionSourceClass(source_class_value)
            except ValueError as exc:
                raise ValueError(
                    "Invalid policy_context['source_class']: "
                    f"{source_class_value}"
                ) from exc
