from __future__ import annotations

from uuid import uuid4

from runtime.coordinator.contracts import CoordinatorOutput
from runtime.contracts.runtime_acquisition_request import (
    RuntimeAcquisitionRequest,
    RuntimeAcquisitionRequestStatus,
    RuntimeAcquisitionRequestType,
)


class RuntimeAcquisitionRequestBuilder:
    """
    Explicit Runtime-level acquisition request builder.

    This builder converts bounded Runtime interpretation
    into explicit RuntimeAcquisitionRequest contracts.

    Builder is NOT:
    - acquisition executor;
    - permission authority;
    - retry engine;
    - Coordinator lifecycle owner;
    - signal interpreter;
    - automatic router.

    Core invariant:
    CoordinatorOutput is not execution authority.
    Runtime must explicitly construct acquisition intent.

    Important:
    Builder does not check ready_for_next_route.
    Runtime decides when this builder may be called.
    """

    @staticmethod
    def build_dialogue_question_request(
        coordinator_output: CoordinatorOutput,
        *,
        variable_code: str,
        reason: str,
    ) -> RuntimeAcquisitionRequest:
        if not variable_code.strip():
            raise ValueError("variable_code must not be empty")

        if not reason.strip():
            raise ValueError("reason must not be empty")

        return RuntimeAcquisitionRequest(
            runtime_request_id=f"runtime-acq-{uuid4()}",
            action_id=coordinator_output.action_id,
            requested_acquisition_type=(
                RuntimeAcquisitionRequestType.DIALOGUE_QUESTION
            ),
            reason=reason,
            required_fields=[variable_code],
            coordinator_id=coordinator_output.coordinator_id,
            coordination_group_id=(
                coordinator_output.coordination_group_id
            ),
            source_component="runtime",
            status=RuntimeAcquisitionRequestStatus.PREPARED,
            metadata={
                "variable_code": variable_code,
                "source": "runtime_builder",
            },
        )