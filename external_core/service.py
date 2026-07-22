from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

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
    """Configuration facade; Runtime and Governance retain operational authority."""

    CORE_SCOPE_ID = "health_model_external_core"
    DOMAIN_SCOPE_ID = "health_model_research"

    def __init__(self, data_directory: str | Path) -> None:
        root = Path(data_directory) / "external_core"
        self.settings = RaySettingsRegistry(root / "settings.json")
        self.domains = DomainRayRegistry(root / "domains.json")
        self.resolver = EffectiveSettingsResolver()
        self._bootstrap_if_empty()
        self._migrate_external_ai_gateway_permissions()

    def contract(self) -> dict[str, Any]:
        return {
            "schema_version": "external-core-settings-contract-1.1.0",
            "settings_layers": [item.value for item in SettingsLayer],
            "settings_statuses": [item.value for item in SettingsStatus],
            "domain_lifecycle": [item.value for item in DomainLifecycle],
            "supported_languages": ["ru", "en", "es"],
            "roles": ["research_colleague", "participant_guide"],
            "external_ai_mode": self.settings.active_for(
                SettingsLayer.EXTERNAL_CORE_DEFAULT,
                self.CORE_SCOPE_ID,
            ).external_ai_mode.value,
            "external_ai_provider_registered": False,
            "rules": {
                "lower_layers_may_only_restrict": True,
                "secrets_in_settings_forbidden": True,
                "cross_domain_interaction_via_runtime": True,
                "direct_external_execution_forbidden": True,
                "human_confirmation_for_high_risk_mutation": True,
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

    def _bootstrap_if_empty(self) -> None:
        if not self.settings.list_revisions():
            self._activate(self._base_settings())
            self._activate(self._researcher_settings())
            self._activate(self._participant_settings())
            self._activate(self._domain_settings())
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
            maximum_retention_days=365,
            allowed_learning_categories=("confirmed_correction", "validated_domain_rule"),
            external_ai_mode=ExternalAIMode.SANDBOX,
        )

    def _migrate_external_ai_gateway_permissions(self) -> None:
        """Create traceable active revisions for the newly approved sandbox gateway.

        Existing active revisions are never edited in place. The migration is
        idempotent and preserves the Draft -> Trial -> Active lifecycle and audit.
        """
        targets = (
            (SettingsLayer.EXTERNAL_CORE_DEFAULT, self.CORE_SCOPE_ID, True),
            (SettingsLayer.ROLE, "research_colleague", False),
            (SettingsLayer.ROLE, "participant_guide", False),
            (SettingsLayer.DOMAIN, self.DOMAIN_SCOPE_ID, True),
        )
        for layer, scope_id, controls_mode in targets:
            active = self.settings.active_for(layer, scope_id)
            related = [
                item
                for item in self.settings.list_revisions()
                if item.get("settings_id") == active.settings_id
            ]
            if any(
                item.get("status") in {
                    SettingsStatus.DRAFT.value,
                    SettingsStatus.TRIAL.value,
                }
                for item in related
            ):
                continue
            capabilities = tuple(dict.fromkeys((active.allowed_capabilities or ()) + ("external_ai_request",)))
            channels = tuple(dict.fromkeys((active.allowed_channels or ()) + ("external_ai_request",)))
            target_mode = ExternalAIMode.SANDBOX if controls_mode else active.external_ai_mode
            if (
                capabilities == active.allowed_capabilities
                and channels == active.allowed_channels
                and target_mode == active.external_ai_mode
            ):
                continue
            revision = replace(
                active,
                revision=max(
                    int(item.get("revision") or 0)
                    for item in related
                ) + 1,
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
            self._activate(
                revision,
                actor_id="system_migration_external_ai_gateway_v1",
            )
