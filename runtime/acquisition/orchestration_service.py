# runtime/acquisition/orchestration_service.py

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from runtime.acquisition.runtime_bridge import AcquisitionRuntimeBridge
from runtime.acquisition.runtime_request_builder import (
    RuntimeAcquisitionRequestBuilder,
)
from runtime.coordinator.contracts import CoordinatorOutput


class RuntimeAcquisitionOrchestrationStatus(str, Enum):
    CREATED = "created"
    PREPARED = "prepared"
    WAITING = "waiting"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    UNRESOLVED = "unresolved"


class RuntimeAcquisitionOrchestrationState(BaseModel):
    orchestration_id: str
    runtime_request_id: str
    status: RuntimeAcquisitionOrchestrationStatus
    created_at: datetime
    expires_at: datetime

    acquisition_request_id: Optional[str] = None
    retry_count: int = 0
    unresolved: bool = False
    blocked_reason: Optional[str] = None
    last_error: Optional[str] = None

    @field_validator("orchestration_id", "runtime_request_id")
    @classmethod
    def ids_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("ids must not be empty")
        return value

    @field_validator("retry_count")
    @classmethod
    def retry_count_must_not_be_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("retry_count must be >= 0")
        return value

    @model_validator(mode="after")
    def validate_state_consistency(
        self,
    ) -> "RuntimeAcquisitionOrchestrationState":
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be after created_at")

        if self.status == RuntimeAcquisitionOrchestrationStatus.BLOCKED:
            if not self.blocked_reason and not self.last_error:
                raise ValueError(
                    "BLOCKED state requires blocked_reason or last_error"
                )

        if self.status in {
            RuntimeAcquisitionOrchestrationStatus.UNRESOLVED,
            RuntimeAcquisitionOrchestrationStatus.EXPIRED,
        }:
            if not self.unresolved:
                raise ValueError(
                    "UNRESOLVED/EXPIRED state requires unresolved=True"
                )

        return self


class RuntimeAcquisitionOrchestrationResult(BaseModel):
    orchestration_id: str
    runtime_request_id: str
    status: RuntimeAcquisitionOrchestrationStatus

    acquisition_request_id: Optional[str] = None
    blocked_reason: Optional[str] = None
    last_error: Optional[str] = None
    unresolved: bool = False

    invariants: Dict[str, bool] = Field(
        default_factory=lambda: {
            "created_is_not_prepared": True,
            "prepared_is_not_externally_exposed": True,
            "prepared_is_not_sent": True,
            "prepared_is_not_executed": True,
            "waiting_is_not_answered": True,
            "waiting_is_not_acquired": True,
            "acquisition_request_is_not_acquisition_result": True,
            "blocked_is_not_cancelled": True,
            "blocked_is_not_expired": True,
            "unresolved_is_not_solved": True,
            "expired_only_applies_to_open_states": True,
            "inbound_result_is_not_verified_truth": True,
            "orchestration_state_is_not_long_term_truth": True,
            "automatic_routing_is_not_automatic_authority": True,
            "retry_visibility_is_not_retry_authority": True,
            "retry_tracking_is_not_retry_execution": True,
            "retry_execution_is_not_escalation_authority": True,
            "blocked_can_be_unresolved": True,
            "expired_is_not_deleted": True,
            "cleanup_is_not_resolved": True,
            "cleanup_is_not_cancelled": True,
            "cleanup_is_not_memory_deletion": True,
        }
    )


class RuntimeAcquisitionOrchestrationService:
    """
    Bounded Runtime acquisition orchestration layer.

    Coordinates acquisition intent only.

    Does NOT:
    - grant permission;
    - expose externally by itself;
    - execute tasks;
    - validate truth;
    - complete Runtime lifecycle;
    - infer human approval;
    - create long-term memory;
    - act as retry planner;
    - act as dialogue layer;
    - act as transport layer.

    CREATED ≠ PREPARED
    PREPARED ≠ sent
    WAITING ≠ answered
    BLOCKED ≠ cancelled
    BLOCKED ≠ expired
    UNRESOLVED ≠ solved
    EXPIRED ≠ deleted

    Expiration applies only to open/active orchestration states.
    """

    def __init__(
        self,
        request_builder: RuntimeAcquisitionRequestBuilder,
        acquisition_bridge: AcquisitionRuntimeBridge,
        ttl_minutes: int = 30,
    ) -> None:
        if ttl_minutes <= 0:
            raise ValueError("ttl_minutes must be > 0")

        self.request_builder = request_builder
        self.acquisition_bridge = acquisition_bridge
        self.ttl_minutes = ttl_minutes
        self._states: Dict[str, RuntimeAcquisitionOrchestrationState] = {}

    def orchestrate_dialogue_question(
        self,
        coordinator_output: CoordinatorOutput,
        variable_code: str,
        reason: str,
    ) -> RuntimeAcquisitionOrchestrationResult:
        now = self._now()

        runtime_request = (
            self.request_builder.build_dialogue_question_request(
                coordinator_output=coordinator_output,
                variable_code=variable_code,
                reason=reason,
            )
        )

        orchestration_id = self._make_orchestration_id(
            runtime_request.runtime_request_id
        )

        state = RuntimeAcquisitionOrchestrationState(
            orchestration_id=orchestration_id,
            runtime_request_id=runtime_request.runtime_request_id,
            status=RuntimeAcquisitionOrchestrationStatus.CREATED,
            created_at=now,
            expires_at=now + timedelta(minutes=self.ttl_minutes),
        )

        state = self._revalidate_state(
            state.model_copy(
                update={
                    "status": RuntimeAcquisitionOrchestrationStatus.PREPARED,
                }
            )
        )

        self._states[orchestration_id] = state

        try:
            acquisition_request = (
                self.acquisition_bridge.create_from_runtime_request(
                    runtime_request
                )
            )

            state = self._revalidate_state(
                state.model_copy(
                    update={
                        "status": RuntimeAcquisitionOrchestrationStatus.WAITING,
                        "acquisition_request_id": acquisition_request.request_id,
                    }
                )
            )

        except Exception as exc:
            state = self._revalidate_state(
                state.model_copy(
                    update={
                        "status": RuntimeAcquisitionOrchestrationStatus.BLOCKED,
                        "blocked_reason": "bridge_error",
                        "last_error": str(exc),
                        "unresolved": True,
                    }
                )
            )

        self._states[orchestration_id] = state

        return self._to_result(state)

    def cleanup_expired(self) -> List[str]:
        """
        Marks expired open/active orchestration states as EXPIRED.

        Does NOT:
        - delete orchestration state;
        - resolve orchestration state;
        - cancel orchestration state;
        - remove memory/history;
        - overwrite BLOCKED terminal-ish state.

        expired ≠ deleted
        cleanup ≠ resolved
        cleanup ≠ cancelled
        blocked ≠ expired
        """

        now = self._now()
        expired_ids: List[str] = []

        for orchestration_id, state in list(self._states.items()):
            if (
                state.expires_at <= now
                and state.status
                in {
                    RuntimeAcquisitionOrchestrationStatus.CREATED,
                    RuntimeAcquisitionOrchestrationStatus.PREPARED,
                    RuntimeAcquisitionOrchestrationStatus.WAITING,
                }
            ):
                expired_state = self._revalidate_state(
                    state.model_copy(
                        update={
                            "status": (
                                RuntimeAcquisitionOrchestrationStatus.EXPIRED
                            ),
                            "unresolved": True,
                        }
                    )
                )

                self._states[orchestration_id] = expired_state
                expired_ids.append(orchestration_id)

        return expired_ids

    def mark_retry_attempt(
        self,
        orchestration_id: str,
        *,
        last_error: Optional[str] = None,
        max_retry_count: int = 2,
    ) -> RuntimeAcquisitionOrchestrationResult:
        """
        Records retry visibility only.

        Does NOT:
        - execute retry;
        - schedule retry;
        - change acquisition source;
        - escalate;
        - infer permission;
        - pressure human/user;
        - resolve acquisition.

        retry visibility ≠ retry authority
        retry tracking ≠ retry execution
        retry execution ≠ escalation authority
        """

        if max_retry_count < 0:
            raise ValueError("max_retry_count must be >= 0")

        state = self._states.get(orchestration_id)

        if state is None:
            raise KeyError(
                "RuntimeAcquisitionOrchestrationState not found: "
                f"{orchestration_id}"
            )

        retry_count = state.retry_count + 1

        updates = {
            "retry_count": retry_count,
            "last_error": last_error or state.last_error,
        }

        if retry_count >= max_retry_count:
            updates.update(
                {
                    "status": RuntimeAcquisitionOrchestrationStatus.UNRESOLVED,
                    "unresolved": True,
                }
            )

        updated = self._revalidate_state(
            state.model_copy(update=updates)
        )

        self._states[orchestration_id] = updated

        return self._to_result(updated)

    def list_unresolved(
        self,
    ) -> List[RuntimeAcquisitionOrchestrationState]:
        return [
            state.model_copy(deep=True)
            for state in self._states.values()
            if state.unresolved
            or state.status
            in {
                RuntimeAcquisitionOrchestrationStatus.WAITING,
                RuntimeAcquisitionOrchestrationStatus.BLOCKED,
                RuntimeAcquisitionOrchestrationStatus.UNRESOLVED,
                RuntimeAcquisitionOrchestrationStatus.EXPIRED,
            }
        ]

    def _to_result(
        self,
        state: RuntimeAcquisitionOrchestrationState,
    ) -> RuntimeAcquisitionOrchestrationResult:
        return RuntimeAcquisitionOrchestrationResult(
            orchestration_id=state.orchestration_id,
            runtime_request_id=state.runtime_request_id,
            status=state.status,
            acquisition_request_id=state.acquisition_request_id,
            blocked_reason=state.blocked_reason,
            last_error=state.last_error,
            unresolved=state.unresolved,
        )

    @staticmethod
    def _revalidate_state(
        state: RuntimeAcquisitionOrchestrationState,
    ) -> RuntimeAcquisitionOrchestrationState:
        return RuntimeAcquisitionOrchestrationState(**state.model_dump())

    @staticmethod
    def _make_orchestration_id(runtime_request_id: str) -> str:
        return f"orch_{runtime_request_id}"

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
