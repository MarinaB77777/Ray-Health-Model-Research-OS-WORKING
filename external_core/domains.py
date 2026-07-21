from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4
import json
import os
import re
import tempfile


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.:-]{1,127}$")
LANGUAGES = frozenset({"ru", "en", "es"})


class DomainLifecycle(str, Enum):
    PROPOSED = "proposed"
    SANDBOXED = "sandboxed"
    REGISTERED = "registered"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RESTRICTED = "restricted"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"
    ARCHIVED = "archived"


class DomainOperation(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTION = "execution"
    INTERRUPTION = "interruption"
    PREDICTION = "prediction"
    COORDINATION = "coordination"
    GOVERNANCE_INTERACTION = "governance_interaction"


class DomainRisk(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DomainCapability:
    capability_id: str
    operations: tuple[DomainOperation, ...]
    resource_scopes: tuple[str, ...]
    data_classes: tuple[str, ...]
    risk: DomainRisk
    requires_human_confirmation: bool = False

    def validate(self) -> None:
        _identifier(self.capability_id)
        if not self.operations or len(self.operations) != len(set(self.operations)):
            raise ValueError("DOMAIN_CAPABILITY_OPERATIONS_REQUIRED_AND_UNIQUE")
        _identifiers(self.resource_scopes, required=True)
        _identifiers(self.data_classes, required=True)
        if self.risk in {DomainRisk.HIGH, DomainRisk.CRITICAL} and (
            DomainOperation.WRITE in self.operations
            or DomainOperation.EXECUTION in self.operations
        ) and not self.requires_human_confirmation:
            raise ValueError("HIGH_RISK_MUTATION_REQUIRES_HUMAN_CONFIRMATION")


@dataclass(frozen=True)
class DomainDependency:
    domain_id: str
    interaction_types: tuple[str, ...]
    purpose: str
    via_runtime: bool = True

    def validate(self, owner_domain_id: str) -> None:
        _identifier(self.domain_id)
        if self.domain_id == owner_domain_id:
            raise ValueError("DOMAIN_CANNOT_DEPEND_ON_ITSELF")
        _identifiers(self.interaction_types, required=True)
        if not self.purpose.strip():
            raise ValueError("DOMAIN_DEPENDENCY_PURPOSE_REQUIRED")
        if not self.via_runtime:
            raise PermissionError("CROSS_DOMAIN_INTERACTION_MUST_USE_RUNTIME")


@dataclass
class DomainRayRegistration:
    domain_id: str
    names: dict[str, str]
    purpose: dict[str, str]
    owner_id: str
    created_by: str
    allowed_roles: tuple[str, ...]
    capabilities: tuple[DomainCapability, ...]
    allowed_source_types: tuple[str, ...]
    allowed_data_classes: tuple[str, ...]
    memory_scopes: tuple[str, ...]
    learning_scopes: tuple[str, ...]
    communication_channels: tuple[str, ...]
    governance_policy_id: str
    governance_policy_version: str
    evidence_policy_id: str
    uncertainty_policy_id: str
    registration_id: str = field(default_factory=lambda: str(uuid4()))
    registration_version: int = 1
    lifecycle: DomainLifecycle = DomainLifecycle.PROPOSED
    dependencies: tuple[DomainDependency, ...] = ()
    external_ai_allowed: bool = False
    direct_external_execution_allowed: bool = False
    audit_required: bool = True
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    approved_by: str | None = None
    activated_at: str | None = None

    def validate(self, *, for_activation: bool = False) -> None:
        _identifier(self.domain_id)
        if set(self.names) != LANGUAGES or any(
            not self.names[language].strip() for language in LANGUAGES
        ):
            raise ValueError("DOMAIN_NAMES_REQUIRED_IN_RU_EN_ES")
        if set(self.purpose) != LANGUAGES or any(
            not self.purpose[language].strip() for language in LANGUAGES
        ):
            raise ValueError("DOMAIN_PURPOSE_REQUIRED_IN_RU_EN_ES")
        for value in (
            self.owner_id,
            self.created_by,
            self.governance_policy_id,
            self.governance_policy_version,
            self.evidence_policy_id,
            self.uncertainty_policy_id,
        ):
            if not value.strip():
                raise ValueError("DOMAIN_REQUIRED_FIELD_MISSING")
        _identifiers(self.allowed_roles, required=True)
        _identifiers(self.allowed_source_types, required=True)
        _identifiers(self.allowed_data_classes, required=True)
        _identifiers(self.memory_scopes, required=True)
        _identifiers(self.learning_scopes, required=False)
        _identifiers(self.communication_channels, required=True)
        capability_ids = [item.capability_id for item in self.capabilities]
        if not capability_ids or len(capability_ids) != len(set(capability_ids)):
            raise ValueError("DOMAIN_CAPABILITIES_REQUIRED_AND_UNIQUE")
        for capability in self.capabilities:
            capability.validate()
            if not set(capability.data_classes).issubset(self.allowed_data_classes):
                raise PermissionError("CAPABILITY_DATA_CLASS_OUTSIDE_DOMAIN_SCOPE")
        dependency_ids = [item.domain_id for item in self.dependencies]
        if len(dependency_ids) != len(set(dependency_ids)):
            raise ValueError("DOMAIN_DEPENDENCIES_MUST_BE_UNIQUE")
        for dependency in self.dependencies:
            dependency.validate(self.domain_id)
        if self.direct_external_execution_allowed:
            raise PermissionError("DOMAIN_RAY_CANNOT_DIRECTLY_EXECUTE_EXTERNAL_ACTIONS")
        if for_activation:
            if not self.audit_required:
                raise PermissionError("ACTIVE_DOMAIN_REQUIRES_AUDIT")
            if not self.approved_by:
                raise ValueError("ACTIVE_DOMAIN_REQUIRES_APPROVER")


TRANSITIONS = {
    DomainLifecycle.PROPOSED: {DomainLifecycle.SANDBOXED},
    DomainLifecycle.SANDBOXED: {
        DomainLifecycle.REGISTERED,
        DomainLifecycle.REVOKED,
    },
    DomainLifecycle.REGISTERED: {
        DomainLifecycle.ACTIVE,
        DomainLifecycle.RESTRICTED,
        DomainLifecycle.REVOKED,
    },
    DomainLifecycle.ACTIVE: {
        DomainLifecycle.SUSPENDED,
        DomainLifecycle.RESTRICTED,
        DomainLifecycle.DEPRECATED,
        DomainLifecycle.REVOKED,
    },
    DomainLifecycle.SUSPENDED: {
        DomainLifecycle.ACTIVE,
        DomainLifecycle.RESTRICTED,
        DomainLifecycle.REVOKED,
    },
    DomainLifecycle.RESTRICTED: {
        DomainLifecycle.ACTIVE,
        DomainLifecycle.SUSPENDED,
        DomainLifecycle.REVOKED,
    },
    DomainLifecycle.DEPRECATED: {
        DomainLifecycle.ARCHIVED,
        DomainLifecycle.REVOKED,
    },
    DomainLifecycle.REVOKED: {DomainLifecycle.ARCHIVED},
    DomainLifecycle.ARCHIVED: set(),
}


class DomainRayRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def register_proposal(self, domain: DomainRayRegistration) -> dict[str, Any]:
        if domain.lifecycle != DomainLifecycle.PROPOSED:
            raise ValueError("NEW_DOMAIN_MUST_START_AS_PROPOSED")
        domain.validate()
        state = self._load()
        if domain.domain_id in state["domains"]:
            raise ValueError("DOMAIN_ID_ALREADY_REGISTERED")
        if domain.registration_id in {
            item["registration_id"] for item in state["domains"].values()
        }:
            raise ValueError("DOMAIN_REGISTRATION_ID_ALREADY_USED")
        serialized = self._serialize(domain)
        state["domains"][domain.domain_id] = serialized
        self._event(state, serialized, "domain_proposed", domain.created_by)
        self._write(state)
        return serialized.copy()

    def transition(
        self,
        domain_id: str,
        target: DomainLifecycle,
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        if not actor_id.strip():
            raise ValueError("DOMAIN_TRANSITION_ACTOR_REQUIRED")
        state = self._load()
        try:
            item = state["domains"][domain_id]
        except KeyError as exc:
            raise KeyError("DOMAIN_NOT_REGISTERED") from exc
        current = DomainLifecycle(item["lifecycle"])
        if target not in TRANSITIONS[current]:
            raise ValueError("INVALID_DOMAIN_LIFECYCLE_TRANSITION")
        if target == DomainLifecycle.ACTIVE:
            item["approved_by"] = actor_id
            item["activated_at"] = utc_now_iso()
            self._deserialize(item).validate(for_activation=True)
            self._validate_dependencies_for_activation(state, item)
        item["lifecycle"] = target.value
        item["updated_at"] = utc_now_iso()
        self._event(state, item, f"domain_{target.value}", actor_id)
        self._write(state)
        return item.copy()

    def get(self, domain_id: str) -> DomainRayRegistration:
        state = self._load()
        try:
            return self._deserialize(state["domains"][domain_id])
        except KeyError as exc:
            raise KeyError("DOMAIN_NOT_REGISTERED") from exc

    def list_all(self) -> list[dict[str, Any]]:
        state = self._load()
        return [item.copy() for item in state["domains"].values()]

    @staticmethod
    def _validate_dependencies_for_activation(
        state: dict[str, Any], item: dict[str, Any]
    ) -> None:
        acceptable = {
            DomainLifecycle.REGISTERED.value,
            DomainLifecycle.ACTIVE.value,
        }
        for dependency in item.get("dependencies", []):
            target = state["domains"].get(dependency["domain_id"])
            if not target or target["lifecycle"] not in acceptable:
                raise PermissionError("DOMAIN_DEPENDENCY_NOT_READY")

    @staticmethod
    def _serialize(domain: DomainRayRegistration) -> dict[str, Any]:
        data = asdict(domain)
        data["lifecycle"] = domain.lifecycle.value
        data["capabilities"] = [
            {
                **asdict(item),
                "operations": [operation.value for operation in item.operations],
                "risk": item.risk.value,
            }
            for item in domain.capabilities
        ]
        data["dependencies"] = [asdict(item) for item in domain.dependencies]
        for key, value in tuple(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        return data

    @staticmethod
    def _deserialize(data: dict[str, Any]) -> DomainRayRegistration:
        converted = data.copy()
        converted["lifecycle"] = DomainLifecycle(converted["lifecycle"])
        converted["capabilities"] = tuple(
            DomainCapability(
                capability_id=item["capability_id"],
                operations=tuple(DomainOperation(value) for value in item["operations"]),
                resource_scopes=tuple(item["resource_scopes"]),
                data_classes=tuple(item["data_classes"]),
                risk=DomainRisk(item["risk"]),
                requires_human_confirmation=item["requires_human_confirmation"],
            )
            for item in converted["capabilities"]
        )
        converted["dependencies"] = tuple(
            DomainDependency(
                domain_id=item["domain_id"],
                interaction_types=tuple(item["interaction_types"]),
                purpose=item["purpose"],
                via_runtime=item["via_runtime"],
            )
            for item in converted["dependencies"]
        )
        for key in (
            "allowed_roles",
            "allowed_source_types",
            "allowed_data_classes",
            "memory_scopes",
            "learning_scopes",
            "communication_channels",
        ):
            converted[key] = tuple(converted[key])
        return DomainRayRegistration(**converted)

    @staticmethod
    def _event(
        state: dict[str, Any],
        domain: dict[str, Any],
        event_type: str,
        actor_id: str,
    ) -> None:
        state["audit_events"].append(
            {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "domain_id": domain["domain_id"],
                "registration_id": domain["registration_id"],
                "registration_version": domain["registration_version"],
                "actor_id": actor_id,
                "occurred_at": utc_now_iso(),
            }
        )

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "schema_version": "1.0.0",
                "domains": {},
                "audit_events": [],
            }
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not {
            "schema_version",
            "domains",
            "audit_events",
        }.issubset(data):
            raise ValueError("INVALID_DOMAIN_RAY_REGISTRY")
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


def health_model_research_domain(*, owner_id: str, created_by: str) -> DomainRayRegistration:
    common_data = ("internal", "pseudonymized_research", "public")
    read_write = (DomainOperation.READ, DomainOperation.WRITE)
    capabilities = (
        DomainCapability(
            capability_id="measurement_design",
            operations=read_write,
            resource_scopes=("questions", "scales", "markers", "time_contracts"),
            data_classes=common_data,
            risk=DomainRisk.MODERATE,
            requires_human_confirmation=True,
        ),
        DomainCapability(
            capability_id="model_construction",
            operations=read_write,
            resource_scopes=("parameters", "mechanisms", "models"),
            data_classes=common_data,
            risk=DomainRisk.MODERATE,
            requires_human_confirmation=True,
        ),
        DomainCapability(
            capability_id="research_data_analysis",
            operations=(DomainOperation.READ, DomainOperation.EXECUTION),
            resource_scopes=("prepared_datasets", "statistical_methods", "analysis_results"),
            data_classes=common_data,
            risk=DomainRisk.HIGH,
            requires_human_confirmation=True,
        ),
        DomainCapability(
            capability_id="scientific_results",
            operations=(DomainOperation.READ, DomainOperation.WRITE),
            resource_scopes=("evidence", "results", "provenance", "limitations"),
            data_classes=common_data,
            risk=DomainRisk.HIGH,
            requires_human_confirmation=True,
        ),
    )
    return DomainRayRegistration(
        domain_id="health_model_research",
        names={
            "ru": "Исследования Health Model",
            "en": "Health Model Research",
            "es": "Investigación de Health Model",
        },
        purpose={
            "ru": "Проектирование измерений, параметров, механизмов, анализа и проверяемых научных результатов Health Model.",
            "en": "Design of Health Model measurements, parameters, mechanisms, analyses and verifiable scientific results.",
            "es": "Diseño de mediciones, parámetros, mecanismos, análisis y resultados científicos verificables de Health Model.",
        },
        owner_id=owner_id,
        created_by=created_by,
        allowed_roles=("research_colleague", "participant_guide"),
        capabilities=capabilities,
        allowed_source_types=(
            "questionnaire",
            "manual_measurement",
            "registered_dataset",
            "sensor_contract",
            "game_contract",
            "video_contract",
        ),
        allowed_data_classes=common_data,
        memory_scopes=("session", "project", "role_preference"),
        learning_scopes=("confirmed_correction", "validated_domain_rule"),
        communication_channels=("chat", "notification"),
        governance_policy_id="health_model_governance",
        governance_policy_version="1.0.0",
        evidence_policy_id="health_model_scientific_evidence",
        uncertainty_policy_id="explicit_structured_uncertainty",
        external_ai_allowed=False,
        direct_external_execution_allowed=False,
        audit_required=True,
    )


def _identifier(value: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("INVALID_DOMAIN_IDENTIFIER")


def _identifiers(values: tuple[str, ...], *, required: bool) -> None:
    if required and not values:
        raise ValueError("DOMAIN_IDENTIFIER_LIST_REQUIRED")
    if len(values) != len(set(values)):
        raise ValueError("DOMAIN_IDENTIFIERS_MUST_BE_UNIQUE")
    for value in values:
        _identifier(value)
