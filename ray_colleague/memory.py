from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4
import json
import os
import tempfile

from .contracts import (
    MemoryClass,
    MemoryScope,
    MemoryTruthType,
    RayRole,
)


PROTECTED_MEMORY_CLASSES = {
    "heart_of_ray",
    "heart_of_human",
    "inner_core",
    "ray_self_health_authority",
    "ray_self_health_raw",
}


@dataclass
class MemoryRecord:
    role: RayRole
    owner_id: str
    scope: MemoryScope
    summary: str
    provenance: dict[str, Any]
    retention_reason: str
    project_id: str | None = None
    session_id: str | None = None
    expires_at: str | None = None
    memory_class: MemoryClass = MemoryClass.WORKING_OPERATIONAL
    truth_type: MemoryTruthType = MemoryTruthType.OPERATIONAL_STATE
    subject: str = "human"
    purpose: str = "ray_colleague_continuity"
    freshness_status: str = "current"
    record_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def validate(self) -> None:
        if not self.owner_id.strip() or not self.summary.strip():
            raise ValueError("MEMORY_OWNER_AND_SUMMARY_REQUIRED")
        if not self.provenance or not self.retention_reason.strip():
            raise ValueError("MEMORY_PROVENANCE_AND_RETENTION_REQUIRED")
        if not self.subject.strip() or not self.purpose.strip():
            raise ValueError("MEMORY_SUBJECT_AND_PURPOSE_REQUIRED")
        if self.memory_class.value in PROTECTED_MEMORY_CLASSES:
            raise PermissionError("PROTECTED_MEMORY_REQUIRES_SPECIALIZED_PATHWAY")
        if self.scope == MemoryScope.PROJECT and not self.project_id:
            raise ValueError("PROJECT_MEMORY_REQUIRES_PROJECT_ID")
        if self.scope == MemoryScope.SESSION and not self.session_id:
            raise ValueError("SESSION_MEMORY_REQUIRES_SESSION_ID")
        if self.role == RayRole.PARTICIPANT_GUIDE and self.scope in {
            MemoryScope.PROJECT,
            MemoryScope.RESEARCHER_PREFERENCE,
        }:
            raise PermissionError("PARTICIPANT_MEMORY_SCOPE_FORBIDDEN")
        if self.role == RayRole.RESEARCH_COLLEAGUE and self.scope == (
            MemoryScope.PARTICIPANT_PREFERENCE
        ):
            raise PermissionError("RESEARCHER_MEMORY_SCOPE_FORBIDDEN")
        if self.expires_at:
            expiry = datetime.fromisoformat(
                self.expires_at.replace("Z", "+00:00")
            )
            if expiry.tzinfo is None:
                raise ValueError("MEMORY_EXPIRY_REQUIRES_TIMEZONE")


class RayMemoryStore:
    """Compatibility store governed as bounded Ray memory, never Inner Core."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def add(self, record: MemoryRecord) -> dict[str, Any]:
        record.validate()
        records = self._load()
        records.append(self._serialize(record))
        self._write(records)
        return self._serialize(record)

    def list_for_owner(
        self,
        role: RayRole,
        owner_id: str,
        *,
        project_id: str | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, Any]]:
        self.expire()
        return [
            item
            for item in self._load()
            if item.get("status", "active") == "active"
            and item.get("freshness_status", "current") == "current"
            and item["role"] == role.value
            and item["owner_id"] == owner_id
            and (project_id is None or item.get("project_id") == project_id)
            and (session_id is None or item.get("session_id") == session_id)
        ]

    def do_not_use(self, role: RayRole, owner_id: str, record_id: str) -> dict[str, Any]:
        return self._set_status(role, owner_id, record_id, "do_not_use")

    def invalidate(self, role: RayRole, owner_id: str, record_id: str) -> dict[str, Any]:
        return self._set_status(role, owner_id, record_id, "invalidated")

    def delete(self, role: RayRole, owner_id: str, record_id: str) -> dict[str, Any]:
        return self._set_status(role, owner_id, record_id, "deleted")

    def _set_status(
        self,
        role: RayRole,
        owner_id: str,
        record_id: str,
        status: str,
    ) -> dict[str, Any]:
        records = self._load()
        for item in records:
            if item["record_id"] != record_id:
                continue
            if item["role"] != role.value or item["owner_id"] != owner_id:
                raise PermissionError("MEMORY_RECORD_OWNERSHIP_MISMATCH")
            item["status"] = status
            item["updated_at"] = datetime.now(UTC).isoformat()
            self._write(records)
            return item
        raise KeyError("MEMORY_RECORD_NOT_FOUND")

    def expire(self) -> int:
        now = datetime.now(UTC)
        records = self._load()
        changed = 0
        for item in records:
            expires_at = item.get("expires_at")
            if item.get("status", "active") != "active" or not expires_at:
                continue
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expiry <= now:
                item["status"] = "expired"
                item["freshness_status"] = "expired"
                item["updated_at"] = now.isoformat()
                changed += 1
        if changed:
            self._write(records)
        return changed

    @staticmethod
    def _serialize(record: MemoryRecord) -> dict[str, Any]:
        data = asdict(record)
        data["role"] = record.role.value
        data["scope"] = record.scope.value
        data["memory_class"] = record.memory_class.value
        data["truth_type"] = record.truth_type.value
        return data

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("INVALID_RAY_MEMORY_STORE")
        # Conservative migration for pre-v2 records. Existing content is not
        # promoted; it remains bounded operational memory with unknown/current
        # compatibility metadata until explicitly corrected.
        for item in data:
            item.setdefault("memory_class", MemoryClass.WORKING_OPERATIONAL.value)
            item.setdefault("truth_type", MemoryTruthType.OPERATIONAL_STATE.value)
            item.setdefault("subject", "human")
            item.setdefault("purpose", "ray_colleague_continuity")
            item.setdefault("freshness_status", "current")
            item.setdefault("status", "active")
        return data

    def _write(self, records: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=self.path.name,
            dir=self.path.parent,
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(records, handle, ensure_ascii=False, indent=2)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
