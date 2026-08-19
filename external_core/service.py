from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from .domains import DomainLifecycle, DomainRayRegistry, health_model_research_domain
from .settings import (
    ClarificationPolicy,
    EffectiveSettingsResolver,
    ExternalAIMode,
    RaySettingsRegistry,
    RaySettingsRevision,
    SettingsLayer,
    SettingsStatus,
    UncertaintyDetail,
)


class ExternalCoreService:
    """Mutable operational-settings facade.

    External Core is not Heart of Ray, Heart of Human, Projection authority,
    Governance, or Runtime execution authority. Settings may restrict operational
    capabilities and memory visibility, but cannot grant raw Inner Core access or
    mutate constitutional identity.
    """

    CORE_SCOPE_ID = "health_model_external_core"
    DOMAIN_SCOPE_ID = "health_model_research"

    def __init__(self, data_directory: str | Path) -> None:
        root = Path(data_directory) / "external_core"
        self.settings = RaySettingsRegistry(root / "settings.json")
        self.domains = DomainRayRegistry(root / "domains.json")
        self.resolver = EffectiveSettingsResolver()
        self._ensure_required_active_settings()
        self._bootstrap_domain_if_empty()
        self._migrate_external_ai_gateway_permissions()
        self._migrate_memory_classes_v2()

    def contract(self) -> dict[str, Any]:
        active = self.settings.active_for(
            SettingsLayer.EXTERNAL_CORE_DEFAULT,
            self.CORE_SCOPE_ID,
        )
        return {
            "schema_version": "external-core-settings-contract-2.0.0",
            "settings_layers": [item.value for item in SettingsLayer],
            "settings_statuses": [item.value for item in SettingsStatus],
            "domain_lifecycle": [item.value for item in DomainLifecycle],
            "supported_languages": ["ru", "en", "es"],
            "roles": ["research_colleague", "participant_guide"],
            "external_ai_mode": active.external_ai_mode.value,
            "external_ai_provider_registered": False,
            "memory_classes": list(active.allowed_memory_classes or ()),
            "rules": {
                "lower_layers_may_only_restrict": True,
                "secrets_in_settings_forbidden": True,
                "cross_domain_interaction_via_runtime": True,
                "direct_external_execution_forbidden": True,
                "human_confirmation_for_high_risk_mutation": True,
                "raw_inner_core_access_forbidden": True,
                "heart_mutation_via_settings_forbidden": True,
                "memory_class_and_scope_are_separate": True,
                "domain_ray_is_not_heart": True,
                "settings_are_not_permission_by_themselves": True,
            },
        }

    def list_settings(self) -> list[dict[str, Any]]:
        return self.settings.list_revisions()

    def create_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload)
        for key, enum_type in (
            ("layer", SettingsLayer),
            ("clarification_policy", ClarificationPolicy),
            ("uncertainty_detail", UncertaintyDetail),
            ("external_ai_mode", ExternalAIMode),
        ):
            if data.get(key) is not None:
                data[key] = enum_type(data[key])
        for key in (
            "allowed_capabilities",
            "allowed_data_classes",
            "allowed_channels",
            "allowed_languages",
            "allowed_memory_scopes",
            "allowed_memory_classes",
            "allowed_learning_categories",
            "human_confirmation_actions",
        ):
            if data.get(key) is not None:
                data[key] = tuple(data[key])
        data["status"] = SettingsStatus.DRAFT
        return self.settings.save_draft(RaySettingsRevision(**data))

    def effective(
        self,
        *,
        role: str,
        domain_id: str | None = None,
        project_id: str | None = None,
        session_id: str | None = None,
        allow_trial: bool = False,
    ) -> dict[str, Any]:
        profiles = [
            self.settings.active_for(
                SettingsLayer.EXTERNAL_CORE_DEFAULT,
                self.CORE_SCOPE_ID,
            ),
            self.settings.active_for(SettingsLayer.ROLE, role),
        ]
        for layer, scope_id in (
            (SettingsLayer.DOMAIN, domain_id),
            (SettingsLayer.PROJECT, project_id),
            (SettingsLayer.SESSION, session_id),
        ):
            if not scope_id:
                continue
            try:
                profiles.append(self.settings.active_for(layer, scope_id))
            except KeyError:
                continue
        return self.resolver.resolve(profiles, allow_trial=allow_trial).to_dict()

    def _ensure_required_active_settings(self) -> None:
        """Complete missing bootstrap settings without overwriting active data."""
        required = (
            self._base_settings(),
            self._researcher_settings(),
            self._participant_settings(),
            self._domain_settings(),
        )
        revisions = self.settings.list_revisions()
        for default in required:
            active = [
                item
                for item in revisions
                if item.get("layer") == default.layer.value
                and item.get("scope_id") == default.scope_id
                and item.get("status") == SettingsStatus.ACTIVE.value
                and item.get("current") is True
            ]
            if len(active) > 1:
                raise KeyError("EXACTLY_ONE_ACTIVE_SETTINGS_REVISION_REQUIRED")
            if not active:
                self._activate(default)
                revisions = self.settings.list_revisions()

    def _bootstrap_domain_if_empty(self) -> None:
        if not self.domains.list_all():
            domain = health_model_research_domain(
                owner_id="health_model_team",
                created_by="system_bootstrap_policy",
            )
            self.domains.register_proposal(domain)
            self.domains.transition(
                domain.domain_id,
                DomainLifecycle.SANDBOXED,
                actor_id="system_bootstrap_policy",
            )

    def _activate(
        self,
        revision: RaySettingsRevision,
        *,
        actor_id: str = "system_bootstrap_policy",
    ) -> None:
        self.settings.save_draft(revision)
        self.settings.transition(
            revision.settings_id,
            revision.revision,
            SettingsStatus.TRIAL,
            actor_id=actor_id,
        )
        self.settings.transition(
            revision.settings_id,
            revision.revision,
            SettingsStatus.ACTIVE,
            actor_id=actor_id,
        )

    def _base_settings(self) -> RaySettingsRevision:
        return RaySettingsRevision(
            layer=SettingsLayer.EXTERNAL_CORE_DEFAULT,
            scope_id=self.CORE_SCOPE_ID,
            created_by="system_bootstrap_policy",
            allowed_capabilities=(
                "navigation",
                "context_review",
                "question_design",
                "parameter_design",
                "mechanism_design",
                "data_preparation",
                "statistical_analysis",
                "scientific_results",
                "participant_guidance",
                "memory_read",
                "memory_write",
                "learning_propose",
                "action_propose",
                "external_ai_request",
            ),
            allowed_data_classes=("internal", "pseudonymized_research", "public"),
            allowed_channels=("chat", "notification", "external_ai_request"),
            allowed_languages=("ru", "en", "es"),
            default_language="ru",
            allowed_memory_scopes=("session", "project", "role_preference"),
            allowed_memory_classes=(
                "working_operational",
                "episodic",
                "semantic",
                "relational",
                "calibration_evidence",
                "decision_provenance",
                "ray_self_health_memory",
            ),
            maximum_retention_days=365,
            learning_enabled=True,
            allowed_learning_categories=("confirmed_correction", "validated_domain_rule"),
            human_confirmation_actions=(
                "memory_write",
                "learning_activation",
                "external_message",
            ),
            clarification_policy=ClarificationPolicy.ASK_WHEN_MATERIAL,
            uncertainty_detail=UncertaintyDetail.STRUCTURED,
            external_ai_mode=ExternalAIMode.SANDBOX,
        )

    @staticmethod
    def _researcher_settings() -> RaySettingsRevision:
        return RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="research_colleague",
            created_by="system_bootstrap_policy",
            allowed_capabilities=(
                "navigation",
                "context_review",
                "question_design",
                "parameter_design",
                "mechanism_design",
                "data_preparation",
                "statistical_analysis",
                "scientific_results",
                "memory_read",
                "memory_write",
                "learning_propose",
                "action_propose",
                "external_ai_request",
            ),
            allowed_data_classes=("internal", "pseudonymized_research", "public"),
            allowed_channels=("chat", "notification", "external_ai_request"),
            allowed_memory_scopes=("project", "role_preference", "session"),
            allowed_memory_classes=(
                "working_operational",
                "semantic",
                "calibration_evidence",
                "decision_provenance",
            ),
            maximum_retention_days=365,
            allowed_learning_categories=("confirmed_correction", "validated_domain_rule"),
        )

    @staticmethod
    def _participant_settings() -> RaySettingsRevision:
        return RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="participant_guide",
            created_by="system_bootstrap_policy",
            allowed_capabilities=(
                "navigation",
                "context_review",
                "participant_guidance",
                "memory_read",
                "memory_write",
                "learning_propose",
                "external_ai_request",
            ),
            allowed_data_classes=("public",),
            allowed_channels=("chat", "notification", "external_ai_request"),
            allowed_memory_scopes=("session", "role_preference"),
            allowed_memory_classes=("working_operational",),
            maximum_retention_days=30,
            allowed_learning_categories=("confirmed_correction",),
            clarification_policy=ClarificationPolicy.ASK_BEFORE_ASSUMPTION,
        )

    def _domain_settings(self) -> RaySettingsRevision:
        return RaySettingsRevision(
            layer=SettingsLayer.DOMAIN,
            scope_id=self.DOMAIN_SCOPE_ID,
            created_by="system_bootstrap_policy",
            allowed_capabilities=(
                "navigation",
                "context_review",
                "question_design",
                "parameter_design",
                "mechanism_design",
                "data_preparation",
                "statistical_analysis",
                "scientific_results",
                "participant_guidance",
                "memory_read",
                "memory_write",
                "learning_propose",
                "action_propose",
                "external_ai_request",
            ),
            allowed_data_classes=("internal", "pseudonymized_research", "public"),
            allowed_channels=("chat", "notification", "external_ai_request"),
            allowed_memory_scopes=("session", "project", "role_preference"),
            allowed_memory_classes=(
                "working_operational",
                "semantic",
                "calibration_evidence",
                "decision_provenance",
            ),
            maximum_retention_days=365,
            allowed_learning_categories=("confirmed_correction", "validated_domain_rule"),
            external_ai_mode=ExternalAIMode.SANDBOX,
        )

    def _migrate_external_ai_gateway_permissions(self) -> None:
        """Create traceable revisions for the approved sandbox gateway."""
        targets = (
            (SettingsLayer.EXTERNAL_CORE_DEFAULT, self.CORE_SCOPE_ID, True),
            (SettingsLayer.ROLE, "research_colleague", False),
            (SettingsLayer.ROLE, "participant_guide", False),
            (SettingsLayer.DOMAIN, self.DOMAIN_SCOPE_ID, True),
        )
        for layer, scope_id, controls_mode in targets:
            active = self.settings.active_for(layer, scope_id)
            related = self._related_revisions(active.settings_id)
            if self._has_open_revision(related):
                continue
            capabilities = tuple(
                dict.fromkeys((active.allowed_capabilities or ()) + ("external_ai_request",))
            )
            channels = tuple(
                dict.fromkeys((active.allowed_channels or ()) + ("external_ai_request",))
            )
            target_mode = ExternalAIMode.SANDBOX if controls_mode else active.external_ai_mode
            if (
                capabilities == active.allowed_capabilities
                and channels == active.allowed_channels
                and target_mode == active.external_ai_mode
            ):
                continue
            revision = replace(
                active,
                revision=self._next_revision(related),
                status=SettingsStatus.DRAFT,
                current=False,
                parent_settings_id=active.settings_id,
                allowed_capabilities=capabilities,
                allowed_channels=channels,
                external_ai_mode=target_mode,
                created_by="system_migration_external_ai_gateway_v1",
                approved_by=None,
                activated_at=None,
                notes="Approved external AI gateway sandbox with separate outbound and inbound channels.",
            )
            self._activate(revision, actor_id="system_migration_external_ai_gateway_v1")

    def _migrate_memory_classes_v2(self) -> None:
        """Migrate old bootstrap profiles to explicit multi-memory classes.

        Old registries deserialize conservatively as Working/Operational only.
        This migration expands only profiles created by known system bootstrap/
        migration code. Human-authored restrictions are never silently broadened.
        """
        targets = (
            (
                SettingsLayer.EXTERNAL_CORE_DEFAULT,
                self.CORE_SCOPE_ID,
                self._base_settings().allowed_memory_classes,
            ),
            (
                SettingsLayer.ROLE,
                "research_colleague",
                self._researcher_settings().allowed_memory_classes,
            ),
            (
                SettingsLayer.ROLE,
                "participant_guide",
                self._participant_settings().allowed_memory_classes,
            ),
            (
                SettingsLayer.DOMAIN,
                self.DOMAIN_SCOPE_ID,
                self._domain_settings().allowed_memory_classes,
            ),
        )
        system_creators = {
            "system_bootstrap_policy",
            "system_migration_external_ai_gateway_v1",
            "system_migration_memory_classes_v2",
        }
        for layer, scope_id, target_classes in targets:
            active = self.settings.active_for(layer, scope_id)
            if active.allowed_memory_classes == target_classes:
                continue
            if active.created_by not in system_creators:
                continue
            related = self._related_revisions(active.settings_id)
            if self._has_open_revision(related):
                continue
            revision = replace(
                active,
                revision=self._next_revision(related),
                status=SettingsStatus.DRAFT,
                current=False,
                parent_settings_id=active.settings_id,
                allowed_memory_classes=target_classes,
                created_by="system_migration_memory_classes_v2",
                approved_by=None,
                activated_at=None,
                notes=(
                    "Architecture v2 migration: explicit governed memory classes; "
                    "raw Inner Core remains forbidden."
                ),
            )
            self._activate(revision, actor_id="system_migration_memory_classes_v2")

    def _related_revisions(self, settings_id: str) -> list[dict[str, Any]]:
        return [
            item
            for item in self.settings.list_revisions()
            if item.get("settings_id") == settings_id
        ]

    @staticmethod
    def _has_open_revision(revisions: list[dict[str, Any]]) -> bool:
        return any(
            item.get("status") in {
                SettingsStatus.DRAFT.value,
                SettingsStatus.TRIAL.value,
            }
            for item in revisions
        )

    @staticmethod
    def _next_revision(revisions: list[dict[str, Any]]) -> int:
        return max((int(item.get("revision") or 0) for item in revisions), default=0) + 1
