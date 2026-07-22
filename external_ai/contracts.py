from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class ConnectionScope(str, Enum):
    PLATFORM = "platform"
    ACCOUNT = "account"


class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    FAILED = "failed"


class ExternalAIError(RuntimeError):
    def __init__(self, code: str, *, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


@dataclass
class ExternalAIConnection:
    scope: ConnectionScope
    owner_id: str
    provider_id: str
    model: str
    credential_ref: str
    status: ConnectionStatus = ConnectionStatus.ACTIVE
    connection_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    tested_at: str = field(default_factory=utc_now_iso)
    last_error_code: str | None = None

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scope"] = self.scope.value
        data["status"] = self.status.value
        data.pop("credential_ref", None)
        data["credential_configured"] = True
        return data


@dataclass
class ExternalAIPolicy:
    scope: ConnectionScope
    owner_id: str
    profile_id: str
    enabled: bool = True
    never_send_categories: tuple[str, ...] = ()
    never_send_terms: tuple[str, ...] = ()
    policy_id: str = field(default_factory=lambda: str(uuid4()))
    policy_version: int = 1
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scope"] = self.scope.value
        data["never_send_categories"] = list(self.never_send_categories)
        data["never_send_terms"] = list(self.never_send_terms)
        return data


@dataclass(frozen=True)
class FilterResult:
    allowed: bool
    text: str | None
    reason_codes: tuple[str, ...] = ()
    matched_categories: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderAnswer:
    text: str
    finish_reason: str
    safety_ratings: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class GatewayResult:
    request_id: str
    status: str
    content: str | None = None
    provider_id: str | None = None
    model: str | None = None
    connection_scope: str | None = None
    error_code: str | None = None
    outbound_reason_codes: tuple[str, ...] = ()
    inbound_reason_codes: tuple[str, ...] = ()
    received_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["outbound_reason_codes"] = list(self.outbound_reason_codes)
        data["inbound_reason_codes"] = list(self.inbound_reason_codes)
        data["source_type"] = "external_information_artifact"
        data["is_ray_truth"] = False
        data["memory_write_allowed"] = False
        data["execution_authority"] = False
        return data
