from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4
import json
import os
import re
import tempfile


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


class SettingsStatus(str, Enum):
    DRAFT = "draft"
    TRIAL = "trial"
    ACTIVE = "active"


class SettingsLayer(str, Enum):
    EXTERNAL_CORE_DEFAULT = "external_core_default"
    ROLE = "role"
    DOMAIN = "domain"
    PROJECT = "project"
    SESSION = "session"


LAYER_ORDER = {
    SettingsLayer.EXTERNAL_CORE_DEFAULT: 0,
    SettingsLayer.ROLE: 1,
    SettingsLayer.DOMAIN: 2,
    SettingsLayer.PROJECT: 3,
    SettingsLayer.SESSION: 4,
}


class ExternalAIMode(str, Enum):
    DISABLED_UNTIL_POST_PILOT = "disabled_until_post_pilot"
    SANDBOX = "sandbox"
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"


EXTERNAL_AI_AUTHORITY = {
    ExternalAIMode.DISABLED_UNTIL_POST_PILOT: 0,
    ExternalAIMode.SUSPENDED: 0,
    ExternalAIMode.SANDBOX: 1,
    ExternalAIMode.TRIAL: 2,
    ExternalAIMode.ACTIVE: 3,
}


class ClarificationPolicy(str, Enum):
    ASK_WHEN_BLOCKED = "ask_when_blocked"
    ASK_WHEN_MATERIAL = "ask_when_material"
    ASK_BEFORE_ASSUMPTION = "ask_before_assumption"


class UncertaintyDetail(str, Enum):
    EXPLICIT = "explicit"
    STRUCTURED = "structured"
    DETAILED = "detailed"


UNCERTAINTY_DETAIL_RANK = {
    UncertaintyDetail.EXPLICIT: 0,
    UncertaintyDetail.STRUCTURED: 1,
    UncertaintyDetail.DETAILED: 2,
}


IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.:-]{1,127}$")
SUPPORTED_LANGUAGES = frozenset({"ru", "en", "es"})
FORBIDDEN_SETTING_KEYS = frozenset(
    {
        "api_key",
        "secret",
        "token",
        "password",
        "credential_value",
        "raw_participant_data",
        "inner_core_payload",
    }
)


@dataclass
class RaySettingsRevision:
    layer: SettingsLayer
    scope_id: str
    created_by: str
    settings_id: str = field(default_factory=lambda: str(uuid4()))
    revision: int = 1
    status: SettingsStatus = SettingsStatus.DRAFT
    current: bool = True
    parent_settings_id: str | None = None
    allowed_capabilities: tuple[str, ...] | None = None
    allowed_data_classes: tuple[str, ...] | None = None
    allowed_channels: tuple[str, ...] | None = None
    allowed_languages: tuple[str, ...] | None = None
    default_language: str | None = None
    allowed_memory_scopes: tuple[str, ...] | None = None
    maximum_retention_days: int | None = None
    learning_enabled: bool | None = None
    allowed_learning_categories: tuple[str, ...] | None = None
    human_confirmation_actions: tuple[str, ...] = ()
    clarification_policy: ClarificationPolicy | None = None
    uncertainty_detail: UncertaintyDetail | None = None
    external_ai_mode: ExternalAIMode | None = None
    notes: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    approved_by: str | None = None
    activated_at: str | None = None

    def validate(self, *, require_complete_default: bool = False) -> None:
        if not self.scope_id.strip() or not self.created_by.strip():
            raise ValueError("SETTINGS_SCOPE_AND_CREATOR_REQUIRED")
        if self.revision < 1:
            raise ValueError("SETTINGS_REVISION_MUST_BE_POSITIVE")
        for values in (
            self.allowed_capabilities,
            self.allowed_data_classes,
            self.allowed_channels,
            self.allowed_memory_scopes,
            self.allowed_learning_categories,
            self.human_confirmation_actions,
        ):
            self._validate_identifiers(values)
        if self.allowed_languages is not None:
            languages = set(self.allowed_languages)
            if not languages or not languages.issubset(SUPPORTED_LANGUAGES):
                raise ValueError("SETTINGS_LANGUAGES_MUST_USE_RU_EN_ES")
        if self.default_language is not None:
            if self.default_language not in SUPPORTED_LANGUAGES:
                raise ValueError("SETTINGS_DEFAULT_LANGUAGE_UNSUPPORTED")
            if (
                self.allowed_languages is not None
                and self.default_language not in self.allowed_languages
            ):
                raise ValueError("DEFAULT_LANGUAGE_MUST_BE_ALLOWED")
        if self.maximum_retention_days is not None:
            if self.maximum_retention_days < 0:
                raise ValueError("RETENTION_DAYS_CANNOT_BE_NEGATIVE")
        if self.status == SettingsStatus.ACTIVE and not self.approved_by:
            raise ValueError("ACTIVE_SETTINGS_REQUIRE_APPROVER")
        if self.layer == SettingsLayer.EXTERNAL_CORE_DEFAULT or require_complete_default:
            required = (
                self.allowed_capabilities,
                self.allowed_data_classes,
                self.allowed_channels,
                self.allowed_languages,
                self.default_language,
                self.allowed_memory_scopes,
                self.maximum_retention_days,
                self.learning_enabled,
                self.allowed_learning_categories,
                self.clarification_policy,
                self.uncertainty_detail,
                self.external_ai_mode,
            )
            if any(value is None for value in required):
                raise ValueError("EXTERNAL_CORE_DEFAULT_SETTINGS_MUST_BE_COMPLETE")
        self._assert_no_forbidden_keys(asdict(self))

    @staticmethod
    def _validate_identifiers(values: Iterable[str] | None) -> None:
        if values is None:
            return
        if len(tuple(values)) != len(set(values)):
            raise ValueError("SETTINGS_IDENTIFIERS_MUST_BE_UNIQUE")
        for value in values:
            if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
                raise ValueError("INVALID_SETTINGS_IDENTIFIER")

    @classmethod
    def _assert_no_forbidden_keys(cls, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if str(key).lower() in FORBIDDEN_SETTING_KEYS and item is not None:
                    raise ValueError("SECRETS_AND_RAW_PAYLOADS_FORBIDDEN_IN_SETTINGS")
                cls._assert_no_forbidden_keys(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                cls._assert_no_forbidden_keys(item)


@dataclass(frozen=True)
class EffectiveRaySettings:
    allowed_capabilities: tuple[str, ...]
    allowed_data_classes: tuple[str, ...]
    allowed_channels: tuple[str, ...]
    allowed_languages: tuple[str, ...]
    default_language: str
    allowed_memory_scopes: tuple[str, ...]
    maximum_retention_days: int
    learning_enabled: bool
    allowed_learning_categories: tuple[str, ...]
    human_confirmation_actions: tuple[str, ...]
    clarification_policy: ClarificationPolicy
    uncertainty_detail: UncertaintyDetail
    external_ai_mode: ExternalAIMode
    applied_revisions: tuple[dict[str, Any], ...]
    provenance: dict[str, tuple[str, ...]]
    resolved_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in (
            "clarification_policy",
            "uncertainty_detail",
            "external_ai_mode",
        ):
            data[key] = getattr(self, key).value
        return data


class EffectiveSettingsResolver:
    SET_FIELDS = (
        "allowed_capabilities",
        "allowed_data_classes",
        "allowed_channels",
        "allowed_languages",
        "allowed_memory_scopes",
        "allowed_learning_categories",
    )

    def resolve(
        self,
        revisions: Iterable[RaySettingsRevision],
        *,
        allow_trial: bool = False,
    ) -> EffectiveRaySettings:
        profiles = sorted(revisions, key=lambda item: LAYER_ORDER[item.layer])
        if not profiles or profiles[0].layer != SettingsLayer.EXTERNAL_CORE_DEFAULT:
            raise ValueError("EFFECTIVE_SETTINGS_REQUIRE_EXTERNAL_CORE_DEFAULT")
        if len({profile.layer for profile in profiles}) != len(profiles):
            raise ValueError("ONLY_ONE_SETTINGS_REVISION_PER_LAYER_CAN_BE_RESOLVED")
        allowed_statuses = {SettingsStatus.ACTIVE}
        if allow_trial:
            allowed_statuses.add(SettingsStatus.TRIAL)
        if any(profile.status not in allowed_statuses for profile in profiles):
            raise ValueError("ONLY_ACTIVE_OR_EXPLICIT_TRIAL_SETTINGS_CAN_BE_RESOLVED")
        for profile in profiles:
            profile.validate()

        base = profiles[0]
        effective: dict[str, Any] = {
            field_name: set(getattr(base, field_name) or ())
            for field_name in self.SET_FIELDS
        }
        effective.update(
            {
                "default_language": base.default_language,
                "maximum_retention_days": base.maximum_retention_days,
                "learning_enabled": bool(base.learning_enabled),
                "human_confirmation_actions": set(
                    base.human_confirmation_actions
                ),
                "clarification_policy": base.clarification_policy,
                "uncertainty_detail": base.uncertainty_detail,
                "external_ai_mode": base.external_ai_mode,
            }
        )
        provenance: dict[str, list[str]] = {
            field_name: [self._revision_ref(base)]
            for field_name in effective
        }

        for profile in profiles[1:]:
            reference = self._revision_ref(profile)
            for field_name in self.SET_FIELDS:
                restriction = getattr(profile, field_name)
                if restriction is not None:
                    effective[field_name].intersection_update(restriction)
                    provenance[field_name].append(reference)
            if profile.maximum_retention_days is not None:
                effective["maximum_retention_days"] = min(
                    effective["maximum_retention_days"],
                    profile.maximum_retention_days,
                )
                provenance["maximum_retention_days"].append(reference)
            if profile.learning_enabled is False:
                effective["learning_enabled"] = False
                provenance["learning_enabled"].append(reference)
            effective["human_confirmation_actions"].update(
                profile.human_confirmation_actions
            )
            if profile.human_confirmation_actions:
                provenance["human_confirmation_actions"].append(reference)
            if profile.external_ai_mode is not None:
                current = effective["external_ai_mode"]
                if EXTERNAL_AI_AUTHORITY[profile.external_ai_mode] > (
                    EXTERNAL_AI_AUTHORITY[current]
                ):
                    raise PermissionError("LOWER_LAYER_CANNOT_ENABLE_MORE_EXTERNAL_AI")
                effective["external_ai_mode"] = profile.external_ai_mode
                provenance["external_ai_mode"].append(reference)
            if profile.uncertainty_detail is not None:
                current = effective["uncertainty_detail"]
                if UNCERTAINTY_DETAIL_RANK[profile.uncertainty_detail] < (
                    UNCERTAINTY_DETAIL_RANK[current]
                ):
                    raise PermissionError("LOWER_LAYER_CANNOT_HIDE_UNCERTAINTY")
                effective["uncertainty_detail"] = profile.uncertainty_detail
                provenance["uncertainty_detail"].append(reference)
            if profile.clarification_policy is not None:
                effective["clarification_policy"] = profile.clarification_policy
                provenance["clarification_policy"].append(reference)
            if profile.default_language is not None:
                effective["default_language"] = profile.default_language
                provenance["default_language"].append(reference)

        if not effective["allowed_languages"]:
            raise PermissionError("SETTINGS_HIERARCHY_REMOVED_ALL_LANGUAGES")
        if effective["default_language"] not in effective["allowed_languages"]:
            effective["default_language"] = sorted(
                effective["allowed_languages"]
            )[0]
            provenance["default_language"].append("effective_fallback")
        if not effective["learning_enabled"]:
            effective["allowed_learning_categories"].clear()

        applied = tuple(
            {
                "settings_id": profile.settings_id,
                "revision": profile.revision,
                "layer": profile.layer.value,
                "scope_id": profile.scope_id,
                "status": profile.status.value,
            }
            for profile in profiles
        )
        return EffectiveRaySettings(
            allowed_capabilities=tuple(sorted(effective["allowed_capabilities"])),
            allowed_data_classes=tuple(sorted(effective["allowed_data_classes"])),
            allowed_channels=tuple(sorted(effective["allowed_channels"])),
            allowed_languages=tuple(sorted(effective["allowed_languages"])),
            default_language=effective["default_language"],
            allowed_memory_scopes=tuple(
                sorted(effective["allowed_memory_scopes"])
            ),
            maximum_retention_days=effective["maximum_retention_days"],
            learning_enabled=effective["learning_enabled"],
            allowed_learning_categories=tuple(
                sorted(effective["allowed_learning_categories"])
            ),
            human_confirmation_actions=tuple(
                sorted(effective["human_confirmation_actions"])
            ),
            clarification_policy=effective["clarification_policy"],
            uncertainty_detail=effective["uncertainty_detail"],
            external_ai_mode=effective["external_ai_mode"],
            applied_revisions=applied,
            provenance={
                key: tuple(values) for key, values in provenance.items()
            },
        )

    @staticmethod
    def _revision_ref(profile: RaySettingsRevision) -> str:
        return f"{profile.layer.value}:{profile.scope_id}:v{profile.revision}"


class RaySettingsRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save_draft(self, revision: RaySettingsRevision) -> dict[str, Any]:
        if revision.status != SettingsStatus.DRAFT:
            raise ValueError("NEW_SETTINGS_REVISION_MUST_BE_DRAFT")
        revision.validate()
        state = self._load()
        existing = state["revisions"].get(revision.settings_id, [])
        if existing:
            latest = max(item["revision"] for item in existing)
            if revision.revision != latest + 1:
                raise ValueError("SETTINGS_REVISION_MUST_FOLLOW_LATEST")
            first = existing[0]
            if (
                first["layer"] != revision.layer.value
                or first["scope_id"] != revision.scope_id
            ):
                raise ValueError("SETTINGS_ID_SCOPE_AND_LAYER_ARE_IMMUTABLE")
        elif revision.revision != 1:
            raise ValueError("FIRST_SETTINGS_REVISION_MUST_BE_ONE")
        data = self._serialize(revision)
        existing.append(data)
        state["revisions"][revision.settings_id] = existing
        self._append_event(state, "settings_draft_saved", data, revision.created_by)
        self._write(state)
        return data.copy()

    def transition(
        self,
        settings_id: str,
        revision: int,
        target: SettingsStatus,
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        if not actor_id.strip():
            raise ValueError("SETTINGS_TRANSITION_ACTOR_REQUIRED")
        state = self._load()
        item = self._find(state, settings_id, revision)
        current = SettingsStatus(item["status"])
        allowed = {
            SettingsStatus.DRAFT: SettingsStatus.TRIAL,
            SettingsStatus.TRIAL: SettingsStatus.ACTIVE,
        }
        if allowed.get(current) != target:
            raise ValueError("INVALID_SETTINGS_STATUS_TRANSITION")
        item["status"] = target.value
        item["updated_at"] = utc_now_iso()
        if target == SettingsStatus.ACTIVE:
            item["approved_by"] = actor_id
            item["activated_at"] = item["updated_at"]
            for candidate in state["revisions"].get(settings_id, []):
                candidate["current"] = candidate is item
        self._validate_serialized(item)
        self._append_event(
            state,
            f"settings_transitioned_to_{target.value}",
            item,
            actor_id,
        )
        self._write(state)
        return item.copy()

    def delete_draft(
        self,
        settings_id: str,
        revision: int,
        *,
        actor_id: str,
    ) -> None:
        state = self._load()
        item = self._find(state, settings_id, revision)
        if item["status"] != SettingsStatus.DRAFT.value:
            raise PermissionError("ONLY_DRAFT_SETTINGS_CAN_BE_DELETED")
        state["revisions"][settings_id].remove(item)
        if not state["revisions"][settings_id]:
            del state["revisions"][settings_id]
        self._append_event(state, "settings_draft_deleted", item, actor_id)
        self._write(state)

    def active_for(self, layer: SettingsLayer, scope_id: str) -> RaySettingsRevision:
        state = self._load()
        candidates = [
            item
            for revisions in state["revisions"].values()
            for item in revisions
            if item["layer"] == layer.value
            and item["scope_id"] == scope_id
            and item["status"] == SettingsStatus.ACTIVE.value
            and item["current"]
        ]
        if len(candidates) != 1:
            raise KeyError("EXACTLY_ONE_ACTIVE_SETTINGS_REVISION_REQUIRED")
        return self._deserialize(candidates[0])

    def list_revisions(
        self,
        *,
        layer: SettingsLayer | None = None,
        scope_id: str | None = None,
    ) -> list[dict[str, Any]]:
        state = self._load()
        return [
            item.copy()
            for revisions in state["revisions"].values()
            for item in revisions
            if (layer is None or item["layer"] == layer.value)
            and (scope_id is None or item["scope_id"] == scope_id)
        ]

    @staticmethod
    def _serialize(revision: RaySettingsRevision) -> dict[str, Any]:
        data = asdict(revision)
        for key in (
            "layer",
            "status",
            "clarification_policy",
            "uncertainty_detail",
            "external_ai_mode",
        ):
            value = getattr(revision, key)
            data[key] = value.value if isinstance(value, Enum) else value
        for key, value in tuple(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        return data

    @staticmethod
    def _deserialize(data: dict[str, Any]) -> RaySettingsRevision:
        converted = data.copy()
        converted["layer"] = SettingsLayer(converted["layer"])
        converted["status"] = SettingsStatus(converted["status"])
        for key, enum_type in (
            ("clarification_policy", ClarificationPolicy),
            ("uncertainty_detail", UncertaintyDetail),
            ("external_ai_mode", ExternalAIMode),
        ):
            if converted.get(key) is not None:
                converted[key] = enum_type(converted[key])
        tuple_fields = (
            "allowed_capabilities",
            "allowed_data_classes",
            "allowed_channels",
            "allowed_languages",
            "allowed_memory_scopes",
            "allowed_learning_categories",
            "human_confirmation_actions",
        )
        for key in tuple_fields:
            if converted.get(key) is not None:
                converted[key] = tuple(converted[key])
        return RaySettingsRevision(**converted)

    def _validate_serialized(self, data: dict[str, Any]) -> None:
        self._deserialize(data).validate()

    @staticmethod
    def _find(
        state: dict[str, Any], settings_id: str, revision: int
    ) -> dict[str, Any]:
        for item in state["revisions"].get(settings_id, []):
            if item["revision"] == revision:
                return item
        raise KeyError("SETTINGS_REVISION_NOT_FOUND")

    @staticmethod
    def _append_event(
        state: dict[str, Any],
        event_type: str,
        item: dict[str, Any],
        actor_id: str,
    ) -> None:
        state["audit_events"].append(
            {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "settings_id": item["settings_id"],
                "revision": item["revision"],
                "layer": item["layer"],
                "scope_id": item["scope_id"],
                "actor_id": actor_id,
                "occurred_at": utc_now_iso(),
            }
        )

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "revisions": {},
                "audit_events": [],
            }
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not {
            "schema_version",
            "revisions",
            "audit_events",
        }.issubset(data):
            raise ValueError("INVALID_RAY_SETTINGS_REGISTRY")
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
