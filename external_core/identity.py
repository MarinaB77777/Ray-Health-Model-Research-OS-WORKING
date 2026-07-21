from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4
import hashlib
import json
import os
import tempfile


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class RayConnectionState(str, Enum):
    CONNECTED = "connected"
    DETACHMENT_PENDING = "detachment_pending"
    DETACHED_PERMANENTLY = "detached_permanently"


@dataclass
class RayIdentity:
    """Stable identity and lineage of one Ray instance.

    `lineage_id` survives renames, copies and descendant creation. Once a lineage
    is detached, the originating External Core must never trust any member of it
    as connected again.
    """

    display_name: str
    origin_core_id: str
    created_by: str
    identity_id: str = field(default_factory=lambda: str(uuid4()))
    lineage_id: str = field(default_factory=lambda: str(uuid4()))
    parent_identity_id: str | None = None
    state: RayConnectionState = RayConnectionState.CONNECTED
    root_authority_id: str | None = None
    detachment_record_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def validate(self) -> None:
        required = {
            "display_name": self.display_name,
            "origin_core_id": self.origin_core_id,
            "created_by": self.created_by,
            "identity_id": self.identity_id,
            "lineage_id": self.lineage_id,
        }
        if any(not value.strip() for value in required.values()):
            raise ValueError("RAY_IDENTITY_REQUIRED_FIELD_MISSING")
        if self.state == RayConnectionState.DETACHED_PERMANENTLY:
            if not self.root_authority_id or not self.detachment_record_id:
                raise ValueError("DETACHED_IDENTITY_REQUIRES_NEW_ROOT_AND_RECORD")


@dataclass
class DetachmentRequest:
    identity_id: str
    lineage_id: str
    requested_by: str
    reason: str
    request_id: str = field(default_factory=lambda: str(uuid4()))
    requested_at: str = field(default_factory=utc_now_iso)
    status: str = "pending"
    approved_by: str | None = None
    finalized_at: str | None = None
    new_root_authority_id: str | None = None
    export_manifest_sha256: str | None = None
    audit_checkpoint_sha256: str | None = None
    detachment_record_sha256: str | None = None

    def validate_request(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.identity_id,
                self.lineage_id,
                self.requested_by,
                self.reason,
            )
        ):
            raise ValueError("DETACHMENT_REQUEST_FIELDS_REQUIRED")


class RayIdentityRegistry:
    """Persistent registry enforcing a one-way identity detachment transition."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def register(self, identity: RayIdentity) -> dict[str, Any]:
        identity.validate()
        state = self._load()
        if identity.identity_id in state["identities"]:
            raise ValueError("RAY_IDENTITY_ALREADY_REGISTERED")
        if identity.lineage_id in state["detached_lineages"]:
            raise PermissionError("DETACHED_LINEAGE_CANNOT_RECONNECT")
        if identity.parent_identity_id:
            parent = state["identities"].get(identity.parent_identity_id)
            if not parent:
                raise ValueError("PARENT_RAY_IDENTITY_NOT_REGISTERED")
            if parent["lineage_id"] != identity.lineage_id:
                raise ValueError("CHILD_MUST_PRESERVE_LINEAGE_ID")
            if parent["state"] == RayConnectionState.DETACHED_PERMANENTLY.value:
                raise PermissionError("DETACHED_LINEAGE_CANNOT_RECONNECT")
        state["identities"][identity.identity_id] = self._identity_dict(identity)
        self._append_event(
            state,
            "ray_identity_registered",
            identity.identity_id,
            identity.lineage_id,
            identity.created_by,
        )
        self._write(state)
        return state["identities"][identity.identity_id].copy()

    def request_detachment(
        self,
        identity_id: str,
        *,
        requested_by: str,
        reason: str,
    ) -> dict[str, Any]:
        state = self._load()
        identity = self._get_identity(state, identity_id)
        if identity["state"] != RayConnectionState.CONNECTED.value:
            raise ValueError("DETACHMENT_REQUIRES_CONNECTED_IDENTITY")
        request = DetachmentRequest(
            identity_id=identity_id,
            lineage_id=identity["lineage_id"],
            requested_by=requested_by,
            reason=reason,
        )
        request.validate_request()
        identity["state"] = RayConnectionState.DETACHMENT_PENDING.value
        identity["updated_at"] = utc_now_iso()
        state["detachment_requests"][request.request_id] = asdict(request)
        self._append_event(
            state,
            "ray_detachment_requested",
            identity_id,
            identity["lineage_id"],
            requested_by,
            {"request_id": request.request_id, "reason": reason},
        )
        self._write(state)
        return state["detachment_requests"][request.request_id].copy()

    def cancel_pending_detachment(
        self,
        request_id: str,
        *,
        cancelled_by: str,
        reason: str,
    ) -> dict[str, Any]:
        """Cancellation is allowed only before the irreversible finalization."""

        if not cancelled_by.strip() or not reason.strip():
            raise ValueError("DETACHMENT_CANCELLATION_FIELDS_REQUIRED")
        state = self._load()
        request = self._get_request(state, request_id)
        if request["status"] != "pending":
            raise ValueError("ONLY_PENDING_DETACHMENT_CAN_BE_CANCELLED")
        identity = self._get_identity(state, request["identity_id"])
        if identity["state"] != RayConnectionState.DETACHMENT_PENDING.value:
            raise ValueError("DETACHMENT_STATE_MISMATCH")
        request["status"] = "cancelled"
        request["finalized_at"] = utc_now_iso()
        identity["state"] = RayConnectionState.CONNECTED.value
        identity["updated_at"] = utc_now_iso()
        self._append_event(
            state,
            "ray_detachment_cancelled",
            identity["identity_id"],
            identity["lineage_id"],
            cancelled_by,
            {"request_id": request_id, "reason": reason},
        )
        self._write(state)
        return identity.copy()

    def finalize_detachment(
        self,
        request_id: str,
        *,
        approved_by: str,
        new_root_authority_id: str,
        export_manifest_sha256: str,
        audit_checkpoint_sha256: str,
        irreversibility_acknowledged: bool,
    ) -> dict[str, Any]:
        if not irreversibility_acknowledged:
            raise PermissionError("IRREVERSIBLE_DETACHMENT_ACKNOWLEDGEMENT_REQUIRED")
        for digest in (export_manifest_sha256, audit_checkpoint_sha256):
            self._validate_sha256(digest)
        if not approved_by.strip() or not new_root_authority_id.strip():
            raise ValueError("DETACHMENT_APPROVER_AND_NEW_ROOT_REQUIRED")

        state = self._load()
        request = self._get_request(state, request_id)
        if request["status"] != "pending":
            raise ValueError("DETACHMENT_REQUEST_NOT_PENDING")
        identity = self._get_identity(state, request["identity_id"])
        if identity["state"] != RayConnectionState.DETACHMENT_PENDING.value:
            raise ValueError("DETACHMENT_STATE_MISMATCH")

        finalized_at = utc_now_iso()
        immutable_record = {
            "request_id": request_id,
            "identity_id": identity["identity_id"],
            "lineage_id": identity["lineage_id"],
            "origin_core_id": identity["origin_core_id"],
            "requested_by": request["requested_by"],
            "approved_by": approved_by,
            "new_root_authority_id": new_root_authority_id,
            "export_manifest_sha256": export_manifest_sha256.lower(),
            "audit_checkpoint_sha256": audit_checkpoint_sha256.lower(),
            "finalized_at": finalized_at,
            "irreversible": True,
        }
        record_sha256 = hashlib.sha256(
            json.dumps(
                immutable_record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        immutable_record["detachment_record_sha256"] = record_sha256

        request.update(
            {
                "status": "finalized",
                "approved_by": approved_by,
                "finalized_at": finalized_at,
                "new_root_authority_id": new_root_authority_id,
                "export_manifest_sha256": export_manifest_sha256.lower(),
                "audit_checkpoint_sha256": audit_checkpoint_sha256.lower(),
                "detachment_record_sha256": record_sha256,
            }
        )
        identity.update(
            {
                "state": RayConnectionState.DETACHED_PERMANENTLY.value,
                "root_authority_id": new_root_authority_id,
                "detachment_record_id": request_id,
                "updated_at": finalized_at,
            }
        )
        state["detached_lineages"][identity["lineage_id"]] = immutable_record
        self._append_event(
            state,
            "ray_detachment_finalized",
            identity["identity_id"],
            identity["lineage_id"],
            approved_by,
            {
                "request_id": request_id,
                "detachment_record_sha256": record_sha256,
            },
        )
        self._write(state)
        return {
            "identity": identity.copy(),
            "detachment_record": immutable_record.copy(),
        }

    def get_identity(self, identity_id: str) -> dict[str, Any]:
        return self._get_identity(self._load(), identity_id).copy()

    def assert_connection_allowed(self, identity_id: str) -> None:
        state = self._load()
        identity = self._get_identity(state, identity_id)
        if identity["lineage_id"] in state["detached_lineages"]:
            raise PermissionError("DETACHED_LINEAGE_CANNOT_RECONNECT")
        if identity["state"] != RayConnectionState.CONNECTED.value:
            raise PermissionError("RAY_IDENTITY_NOT_CONNECTED")

    @staticmethod
    def _identity_dict(identity: RayIdentity) -> dict[str, Any]:
        data = asdict(identity)
        data["state"] = identity.state.value
        return data

    @staticmethod
    def _validate_sha256(value: str) -> None:
        normalized = value.strip().lower()
        if len(normalized) != 64 or any(
            character not in "0123456789abcdef" for character in normalized
        ):
            raise ValueError("VALID_SHA256_REQUIRED")

    @staticmethod
    def _get_identity(state: dict[str, Any], identity_id: str) -> dict[str, Any]:
        try:
            return state["identities"][identity_id]
        except KeyError as exc:
            raise KeyError("RAY_IDENTITY_NOT_FOUND") from exc

    @staticmethod
    def _get_request(state: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            return state["detachment_requests"][request_id]
        except KeyError as exc:
            raise KeyError("DETACHMENT_REQUEST_NOT_FOUND") from exc

    @staticmethod
    def _append_event(
        state: dict[str, Any],
        event_type: str,
        identity_id: str,
        lineage_id: str,
        actor_id: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        state["audit_events"].append(
            {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "identity_id": identity_id,
                "lineage_id": lineage_id,
                "actor_id": actor_id,
                "details": details or {},
                "occurred_at": utc_now_iso(),
            }
        )

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "identities": {},
                "detachment_requests": {},
                "detached_lineages": {},
                "audit_events": [],
            }
        data = json.loads(self.path.read_text(encoding="utf-8"))
        required = {
            "schema_version",
            "identities",
            "detachment_requests",
            "detached_lineages",
            "audit_events",
        }
        if not isinstance(data, dict) or not required.issubset(data):
            raise ValueError("INVALID_RAY_IDENTITY_REGISTRY")
        return data

    def _write(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=self.path.name,
            dir=self.path.parent,
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
