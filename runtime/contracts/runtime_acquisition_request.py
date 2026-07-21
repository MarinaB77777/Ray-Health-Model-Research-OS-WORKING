from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuntimeAcquisitionRequestType(str, Enum):
    DIALOGUE_QUESTION = "dialogue_question"
    SENSOR_DATA = "sensor_data"
    CALIBRATION_TASK = "calibration_task"
    CONTEXT_LOOKUP = "context_lookup"
    EXTERNAL_SOURCE_LOOKUP = "external_source_lookup"


class RuntimeAcquisitionRequestStatus(str, Enum):
    CREATED = "created"
    PREPARED = "prepared"
    BLOCKED = "blocked"


class RuntimeAcquisitionRequest(BaseModel):
    """
    Explicit Runtime-level acquisition operation intent.

    RuntimeAcquisitionRequest is:
    - Runtime orchestration intent;
    - bounded request contract toward Acquisition layer;
    - explicit conversion point from coordination/readiness state
      into acquisition operation request.

    RuntimeAcquisitionRequest is NOT:
    - permission;
    - acquisition result;
    - CoordinatorOutput;
    - CoordinatorSignal;
    - Core Engine truth;
    - retry decision;
    - execution proof;
    - memory write;
    - forecast authority.

    Core invariant:
    No layer may reinterpret another layer's snapshot
    as execution authority.
    """

    runtime_request_id: str
    action_id: str

    requested_acquisition_type: RuntimeAcquisitionRequestType
    reason: str

    required_fields: list[str] = Field(default_factory=list)

    coordinator_id: Optional[str] = None
    coordination_group_id: Optional[str] = None
    source_component: Optional[str] = None

    status: RuntimeAcquisitionRequestStatus = (
        RuntimeAcquisitionRequestStatus.CREATED
    )

    policy_context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_request(self) -> "RuntimeAcquisitionRequest":
        if not self.runtime_request_id.strip():
            raise ValueError("runtime_request_id must not be empty")

        if not self.action_id.strip():
            raise ValueError("action_id must not be empty")

        if not self.reason.strip():
            raise ValueError("reason must not be empty")

        if not self.required_fields:
            raise ValueError(
                "RuntimeAcquisitionRequest requires at least one required_field"
            )

        if (
            self.requested_acquisition_type
            == RuntimeAcquisitionRequestType.EXTERNAL_SOURCE_LOOKUP
            and not self.policy_context
        ):
            raise ValueError(
                "EXTERNAL_SOURCE_LOOKUP requires policy_context"
            )

        return self


RUNTIME_ACQUISITION_REQUEST_BOUNDARY_RULES = {
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_PERMISSION",
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_ACQUISITION_RESULT",
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_COORDINATOR_OUTPUT",
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_COORDINATOR_SIGNAL",
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_CORE_ENGINE_TRUTH",
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_RETRY_DECISION",
    "RUNTIME_ACQUISITION_REQUEST_IS_NOT_EXECUTION_PROOF",
    "PREPARED_IS_NOT_SENT",
    "NO_LAYER_MAY_REINTERPRET_ANOTHER_LAYER_SNAPSHOT_AS_EXECUTION_AUTHORITY",
    "RUNTIME_MUST_EXPLICITLY_FORM_ACQUISITION_OPERATION_INTENT",
}