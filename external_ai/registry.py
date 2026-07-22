from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from threading import RLock
from typing import Any
import json
import os
import tempfile

from .contracts import (
    ConnectionScope,
    ConnectionStatus,
    ExternalAIConnection,
    ExternalAIPolicy,
    ExternalAIError,
    utc_now_iso,
)
from .filters import validate_policy


class ExternalAIRegistry:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.connections_path = self.root / "connections.json"
        self.policies_path = self.root / "policies.json"
        self.audit_path = self.root / "audit.jsonl"
        self._lock = RLock()

    def save_connection(self, connection: ExternalAIConnection) -> dict[str, Any]:
        with self._lock:
            rows = self._load_list(self.connections_path)
            for item in rows:
                if item.get("scope") == connection.scope.value and item.get("owner_id") == connection.owner_id and item.get("status") == ConnectionStatus.ACTIVE.value:
                    item["status"] = ConnectionStatus.DISABLED.value
                    item["updated_at"] = utc_now_iso()
            rows.append(self._serialize_connection(connection))
            self._write_list(self.connections_path, rows)
        self.audit("connection_activated", connection.owner_id, connection.connection_id, {"scope": connection.scope.value, "provider_id": connection.provider_id, "model": connection.model})
        return connection.public_dict()

    def list_visible(self, account_id: str) -> list[dict[str, Any]]:
        return [
            self._deserialize_connection(item).public_dict()
            for item in self._load_list(self.connections_path)
            if item.get("scope") == ConnectionScope.PLATFORM.value or item.get("owner_id") == account_id
        ]

    def effective_connection(self, account_id: str | None) -> ExternalAIConnection | None:
        rows = [self._deserialize_connection(item) for item in self._load_list(self.connections_path)]
        if account_id:
            personal = [item for item in rows if item.scope == ConnectionScope.ACCOUNT and item.owner_id == account_id and item.status == ConnectionStatus.ACTIVE]
            if personal:
                return max(personal, key=lambda item: item.updated_at)
        platform = [item for item in rows if item.scope == ConnectionScope.PLATFORM and item.status == ConnectionStatus.ACTIVE]
        return max(platform, key=lambda item: item.updated_at) if platform else None

    def delete_connection(self, connection_id: str, *, actor_account_id: str, platform_admin: bool) -> str:
        with self._lock:
            rows = self._load_list(self.connections_path)
            target = next((item for item in rows if item.get("connection_id") == connection_id), None)
            if target is None:
                raise ExternalAIError("EXTERNAL_AI_CONNECTION_NOT_FOUND", status_code=404)
            if target.get("scope") == ConnectionScope.PLATFORM.value:
                if not platform_admin:
                    raise ExternalAIError("PLATFORM_EXTERNAL_AI_ADMIN_REQUIRED", status_code=403)
            elif target.get("owner_id") != actor_account_id:
                raise ExternalAIError("EXTERNAL_AI_CONNECTION_OWNERSHIP_MISMATCH", status_code=403)
            rows = [item for item in rows if item.get("connection_id") != connection_id]
            self._write_list(self.connections_path, rows)
        self.audit("connection_deleted", actor_account_id, connection_id, {"scope": target["scope"], "provider_id": target["provider_id"]})
        return str(target["credential_ref"])

    def save_policy(self, policy: ExternalAIPolicy) -> dict[str, Any]:
        validate_policy(policy)
        with self._lock:
            rows = self._load_list(self.policies_path)
            existing = [item for item in rows if item.get("scope") == policy.scope.value and item.get("owner_id") == policy.owner_id]
            if existing:
                latest = max(existing, key=lambda item: int(item.get("policy_version") or 0))
                policy = replace(
                    policy,
                    policy_id=str(latest["policy_id"]),
                    policy_version=int(latest.get("policy_version") or 0) + 1,
                    created_at=str(latest.get("created_at") or policy.created_at),
                    updated_at=utc_now_iso(),
                )
            rows.append(policy.to_dict())
            self._write_list(self.policies_path, rows)
        self.audit("filter_policy_saved", policy.owner_id, policy.policy_id, {"scope": policy.scope.value, "profile_id": policy.profile_id, "enabled": policy.enabled, "policy_version": policy.policy_version, "never_send_category_count": len(policy.never_send_categories), "never_send_term_count": len(policy.never_send_terms)})
        return policy.to_dict()

    def latest_policy(self, scope: ConnectionScope, owner_id: str) -> ExternalAIPolicy | None:
        candidates = [self._deserialize_policy(item) for item in self._load_list(self.policies_path) if item.get("scope") == scope.value and item.get("owner_id") == owner_id]
        return max(candidates, key=lambda item: item.policy_version) if candidates else None

    def audit(self, event_type: str, owner_id: str, object_id: str, details: dict[str, Any]) -> None:
        forbidden = {"message", "content", "response", "credential", "api_key", "never_send_terms"}
        safe = {key: value for key, value in details.items() if key not in forbidden}
        event = {"event_type": event_type, "owner_id": owner_id, "object_id": object_id, "details": safe, "occurred_at": utc_now_iso()}
        self.root.mkdir(parents=True, exist_ok=True)
        with self._lock:
            fd = os.open(
                self.audit_path,
                os.O_WRONLY | os.O_APPEND | os.O_CREAT,
                0o600,
            )
            with os.fdopen(fd, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(self.audit_path, 0o600)

    @staticmethod
    def _serialize_connection(connection: ExternalAIConnection) -> dict[str, Any]:
        data = connection.__dict__.copy()
        data["scope"] = connection.scope.value
        data["status"] = connection.status.value
        return data

    @staticmethod
    def _deserialize_connection(data: dict[str, Any]) -> ExternalAIConnection:
        converted = dict(data)
        converted["scope"] = ConnectionScope(converted["scope"])
        converted["status"] = ConnectionStatus(converted["status"])
        return ExternalAIConnection(**converted)

    @staticmethod
    def _deserialize_policy(data: dict[str, Any]) -> ExternalAIPolicy:
        converted = dict(data)
        converted["scope"] = ConnectionScope(converted["scope"])
        converted["never_send_categories"] = tuple(converted.get("never_send_categories") or ())
        converted["never_send_terms"] = tuple(converted.get("never_send_terms") or ())
        return ExternalAIPolicy(**converted)

    @staticmethod
    def _load_list(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExternalAIError("EXTERNAL_AI_REGISTRY_CORRUPTED", status_code=500) from exc
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ExternalAIError("EXTERNAL_AI_REGISTRY_CORRUPTED", status_code=500)
        return data

    @staticmethod
    def _write_list(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
        try:
            os.chmod(temp_name, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(rows, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
            os.chmod(path, 0o600)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
