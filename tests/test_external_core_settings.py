from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from external_core.settings import (
    ClarificationPolicy,
    EffectiveSettingsResolver,
    ExternalAIMode,
    RaySettingsRegistry,
    RaySettingsRevision,
    SettingsLayer,
    SettingsStatus,
    UncertaintyDetail,
)


def active_default() -> RaySettingsRevision:
    return RaySettingsRevision(
        layer=SettingsLayer.EXTERNAL_CORE_DEFAULT,
        scope_id="health_model_external_core",
        created_by="system_registry",
        status=SettingsStatus.ACTIVE,
        approved_by="research_lead",
        allowed_capabilities=(
            "navigation",
            "parameter_design",
            "mechanism_design",
            "statistical_analysis",
            "participant_guidance",
            "external_ai_request",
        ),
        allowed_data_classes=("internal", "pseudonymized_research", "public"),
        allowed_channels=("chat", "notification", "external_ai_request"),
        allowed_languages=("ru", "en", "es"),
        default_language="ru",
        allowed_memory_scopes=("session", "project", "role_preference"),
        maximum_retention_days=365,
        learning_enabled=True,
        allowed_learning_categories=("confirmed_correction", "response_rule"),
        human_confirmation_actions=("memory_write", "external_message"),
        clarification_policy=ClarificationPolicy.ASK_WHEN_MATERIAL,
        uncertainty_detail=UncertaintyDetail.STRUCTURED,
        external_ai_mode=ExternalAIMode.DISABLED_UNTIL_POST_PILOT,
    )


class EffectiveSettingsTests(unittest.TestCase):
    def test_lower_layers_intersect_permissions_and_reduce_retention(self) -> None:
        role = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="participant_guide",
            created_by="research_lead",
            status=SettingsStatus.ACTIVE,
            approved_by="research_lead",
            allowed_capabilities=("navigation", "participant_guidance"),
            allowed_data_classes=("public",),
            allowed_channels=("chat",),
            allowed_memory_scopes=("session",),
            maximum_retention_days=30,
            allowed_learning_categories=("confirmed_correction",),
            human_confirmation_actions=("learning_activation",),
        )
        effective = EffectiveSettingsResolver().resolve([active_default(), role])
        self.assertEqual(("navigation", "participant_guidance"), effective.allowed_capabilities)
        self.assertEqual(("public",), effective.allowed_data_classes)
        self.assertEqual(30, effective.maximum_retention_days)
        self.assertIn("learning_activation", effective.human_confirmation_actions)
        self.assertEqual(
            ExternalAIMode.DISABLED_UNTIL_POST_PILOT,
            effective.external_ai_mode,
        )

    def test_lower_layer_cannot_enable_external_ai_before_pilot(self) -> None:
        domain = RaySettingsRevision(
            layer=SettingsLayer.DOMAIN,
            scope_id="health_model_research",
            created_by="research_lead",
            status=SettingsStatus.ACTIVE,
            approved_by="research_lead",
            external_ai_mode=ExternalAIMode.SANDBOX,
        )
        with self.assertRaises(PermissionError):
            EffectiveSettingsResolver().resolve([active_default(), domain])

    def test_lower_layer_cannot_hide_uncertainty(self) -> None:
        domain = RaySettingsRevision(
            layer=SettingsLayer.DOMAIN,
            scope_id="health_model_research",
            created_by="research_lead",
            status=SettingsStatus.ACTIVE,
            approved_by="research_lead",
            uncertainty_detail=UncertaintyDetail.EXPLICIT,
        )
        with self.assertRaises(PermissionError):
            EffectiveSettingsResolver().resolve([active_default(), domain])

    def test_disabling_learning_removes_learning_categories(self) -> None:
        session = RaySettingsRevision(
            layer=SettingsLayer.SESSION,
            scope_id="session_1",
            created_by="participant_1",
            status=SettingsStatus.ACTIVE,
            approved_by="participant_1",
            learning_enabled=False,
        )
        effective = EffectiveSettingsResolver().resolve([active_default(), session])
        self.assertFalse(effective.learning_enabled)
        self.assertEqual((), effective.allowed_learning_categories)

    def test_draft_is_not_used_as_effective_settings(self) -> None:
        role = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="research_colleague",
            created_by="research_lead",
        )
        with self.assertRaises(ValueError):
            EffectiveSettingsResolver().resolve([active_default(), role])


class SettingsRegistryLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = RaySettingsRegistry(
            Path(self.temp_dir.name) / "settings.json"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_draft_trial_active_lifecycle_requires_approval(self) -> None:
        draft = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="research_colleague",
            created_by="research_lead",
            allowed_capabilities=("navigation", "parameter_design"),
        )
        self.registry.save_draft(draft)
        trial = self.registry.transition(
            draft.settings_id,
            1,
            SettingsStatus.TRIAL,
            actor_id="research_lead",
        )
        self.assertEqual("trial", trial["status"])
        active = self.registry.transition(
            draft.settings_id,
            1,
            SettingsStatus.ACTIVE,
            actor_id="research_lead",
        )
        self.assertEqual("active", active["status"])
        self.assertEqual("research_lead", active["approved_by"])

    def test_only_draft_can_be_deleted(self) -> None:
        draft = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="participant_guide",
            created_by="research_lead",
        )
        self.registry.save_draft(draft)
        self.registry.transition(
            draft.settings_id,
            1,
            SettingsStatus.TRIAL,
            actor_id="research_lead",
        )
        with self.assertRaises(PermissionError):
            self.registry.delete_draft(
                draft.settings_id,
                1,
                actor_id="research_lead",
            )

    def test_activating_replacement_deactivates_other_id_for_same_scope(self) -> None:
        first = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="research_colleague",
            created_by="research_lead",
        )
        second = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="research_colleague",
            created_by="research_lead",
        )
        for revision in (first, second):
            self.registry.save_draft(revision)
            self.registry.transition(
                revision.settings_id,
                1,
                SettingsStatus.TRIAL,
                actor_id="research_lead",
            )
            self.registry.transition(
                revision.settings_id,
                1,
                SettingsStatus.ACTIVE,
                actor_id="research_lead",
            )

        active = self.registry.active_for(
            SettingsLayer.ROLE,
            "research_colleague",
        )
        self.assertEqual(second.settings_id, active.settings_id)
        current = [
            item
            for item in self.registry.list_revisions(
                layer=SettingsLayer.ROLE,
                scope_id="research_colleague",
            )
            if item["status"] == "active" and item["current"]
        ]
        self.assertEqual(1, len(current))

    def test_setting_identifiers_are_strict_and_unique(self) -> None:
        revision = RaySettingsRevision(
            layer=SettingsLayer.ROLE,
            scope_id="research_colleague",
            created_by="research_lead",
            allowed_capabilities=("navigation", "navigation"),
        )
        with self.assertRaises(ValueError):
            revision.validate()


if __name__ == "__main__":
    unittest.main()
