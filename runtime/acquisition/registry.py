# runtime/acquisition/registry.py

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionStatus,
    SufficiencyStatus,
)
from runtime.acquisition.lifecycle import AcquisitionLifecycle

class AcquisitionRegistry:
    """
    In-memory Acquisition Registry.

    Registry stores acquisition operational state.

    It is NOT:
    - executor;
    - planner;
    - Analyst;
    - Governance;
    - Memory;
    - truth authority;
    - retry engine;
    - external transport;
    - answer builder.

    registry ≠ memory
    registry ≠ truth
    registry ≠ answer

    It only stores and updates AcquisitionRequest lifecycle state.
    """

    def __init__(
        self,
        lifecycle: AcquisitionLifecycle | None = None,
    ) -> None:
        self._requests: dict[str, AcquisitionRequest] = {}
        self.lifecycle = lifecycle or AcquisitionLifecycle()

    def add_request(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionRequest:
        if request.request_id in self._requests:
            raise ValueError(
                f"AcquisitionRequest already exists: {request.request_id}"
            )

        self._requests[request.request_id] = deepcopy(request)
        return deepcopy(self._requests[request.request_id])

    def get_request(
        self,
        request_id: str,
    ) -> Optional[AcquisitionRequest]:
        request = self._requests.get(request_id)

        if request is None:
            return None

        return deepcopy(request)

    def update_status(
        self,
        request_id: str,
        status: AcquisitionStatus,
    ) -> Optional[AcquisitionRequest]:
        request = self._requests.get(request_id)

        if request is None:
            return None

        if request.status == status:
            return deepcopy(request)

        self.lifecycle.validate_transition(
            current_status=request.status,
            next_status=status,
        )

        updated = request.model_copy(
            update={
                "status": status,
            }
        )

        # Re-validate after update.
        updated = AcquisitionRequest(**updated.model_dump())

        self._requests[request_id] = updated
        return deepcopy(updated)

    def update_sufficiency_status(
        self,
        request_id: str,
        sufficiency_status: SufficiencyStatus,
    ) -> Optional[AcquisitionRequest]:
        request = self._requests.get(request_id)

        if request is None:
            return None

        updated = request.model_copy(
            update={
                "sufficiency_status": sufficiency_status,
            }
        )

        # Re-validate after update.
        updated = AcquisitionRequest(**updated.model_dump())

        self._requests[request_id] = updated
        return deepcopy(updated)

    def update_filled_fields(
        self,
        request_id: str,
        filled_fields: dict[str, Any],
        extra_filled_fields_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[AcquisitionRequest]:
        request = self._requests.get(request_id)

        if request is None:
            return None

        merged_fields = {
            **request.filled_fields,
            **filled_fields,
        }

        merged_metadata = {
            **request.extra_filled_fields_metadata,
            **(extra_filled_fields_metadata or {}),
        }

        updated = request.model_copy(
            update={
                "filled_fields": merged_fields,
                "extra_filled_fields_metadata": merged_metadata,
            }
        )

        # Re-validate after update.
        updated = AcquisitionRequest(**updated.model_dump())

        self._requests[request_id] = updated
        return deepcopy(updated)

    def update_outbound_state(
        self,
        request_id: str,
        outbound_sent: bool,
        outbound_source_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[AcquisitionRequest]:
        request = self._requests.get(request_id)

        if request is None:
            return None

        updated = request.model_copy(
            update={
                "outbound_sent": outbound_sent,
                "outbound_source_metadata": (
                    outbound_source_metadata or {}
                ),
            }
        )

        # Re-validate after update.
        updated = AcquisitionRequest(**updated.model_dump())

        self._requests[request_id] = updated
        return deepcopy(updated)

    def remove_request(
        self,
        request_id: str,
    ) -> bool:
        if request_id not in self._requests:
            return False

        del self._requests[request_id]
        return True

    def list_requests(self) -> list[AcquisitionRequest]:
        return [
            deepcopy(request)
            for request in self._requests.values()
        ]
    
    def list_by_status(
        self,
        status: AcquisitionStatus,
    ) -> list[AcquisitionRequest]:
        return [
            deepcopy(request)
            for request in self._requests.values()
            if request.status == status
        ]  

    def clear(self) -> None:
        self._requests.clear()