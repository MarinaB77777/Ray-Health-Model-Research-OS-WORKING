from __future__ import annotations

import tempfile
import unittest

from external_core.service import ExternalCoreService
from external_core.settings import SettingsLayer


class ExternalCoreServiceTests(unittest.TestCase):
    def test_bootstrap_creates_real_active_settings_and_sandboxed_domain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ExternalCoreService(temp_dir)
            settings = service.list_settings()
            active_current = [
                item
                for item in settings
                if item["status"] == "active" and item["current"]
            ]
            self.assertEqual(4, len(active_current))
            domains = service.domains.list_all()
            self.assertEqual(1, len(domains))
            self.assertEqual("sandboxed", domains[0]["lifecycle"])

    def test_researcher_effective_settings_include_sandbox_external_ai_gateway(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ExternalCoreService(temp_dir)
            effective = service.effective(
                role="research_colleague",
                domain_id="health_model_research",
            )
            self.assertIn("parameter_design", effective["allowed_capabilities"])
            self.assertEqual("sandbox", effective["external_ai_mode"])
            self.assertEqual(3, len(effective["applied_revisions"]))
            self.assertEqual(
                (
                    "calibration_evidence",
                    "decision_provenance",
                    "semantic",
                    "working_operational",
                ),
                tuple(effective["allowed_memory_classes"]),
            )
            self.assertNotIn("heart_of_human", effective["allowed_memory_classes"])
            self.assertNotIn("heart_of_ray", effective["allowed_memory_classes"])

    def test_participant_role_cannot_gain_research_or_deep_memory_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ExternalCoreService(temp_dir)
            effective = service.effective(
                role="participant_guide",
                domain_id="health_model_research",
            )
            self.assertIn("participant_guidance", effective["allowed_capabilities"])
            self.assertNotIn("statistical_analysis", effective["allowed_capabilities"])
            self.assertEqual(("public",), tuple(effective["allowed_data_classes"]))
            self.assertEqual(
                ("working_operational",),
                tuple(effective["allowed_memory_classes"]),
            )

    def test_contract_reports_v2_inner_core_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = ExternalCoreService(temp_dir).contract()
            self.assertEqual("external-core-settings-contract-2.0.0", contract["schema_version"])
            self.assertFalse(contract["external_ai_provider_registered"])
            self.assertTrue(contract["rules"]["lower_layers_may_only_restrict"])
            self.assertTrue(contract["rules"]["raw_inner_core_access_forbidden"])
            self.assertTrue(contract["rules"]["heart_mutation_via_settings_forbidden"])
            self.assertTrue(contract["rules"]["memory_class_and_scope_are_separate"])
            self.assertTrue(contract["rules"]["domain_ray_is_not_heart"])

    def test_startup_completes_partial_settings_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = ExternalCoreService(temp_dir)
            state = first.settings._load()
            retained = {
                settings_id: revisions
                for settings_id, revisions in state["revisions"].items()
                if revisions[0]["layer"] == SettingsLayer.DOMAIN.value
            }
            state["revisions"] = retained
            first.settings._write(state)

            recovered = ExternalCoreService(temp_dir)

            self.assertEqual("sandbox", recovered.contract()["external_ai_mode"])
            researcher = recovered.effective(
                role="research_colleague",
                domain_id="health_model_research",
            )
            self.assertEqual("sandbox", researcher["external_ai_mode"])
            self.assertIn("semantic", researcher["allowed_memory_classes"])
            participant = recovered.effective(
                role="participant_guide",
                domain_id="health_model_research",
            )
            self.assertEqual(("public",), tuple(participant["allowed_data_classes"]))
            self.assertEqual(
                ("working_operational",),
                tuple(participant["allowed_memory_classes"]),
            )

    def test_human_authored_old_profile_is_not_silently_expanded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ExternalCoreService(temp_dir)
            role = service.settings.active_for(SettingsLayer.ROLE, "research_colleague")
            related = service._related_revisions(role.settings_id)
            revision = role.__class__(
                **{
                    **role.__dict__,
                    "revision": max(item["revision"] for item in related) + 1,
                    "status": role.status.__class__.DRAFT,
                    "current": False,
                    "created_by": "human_admin",
                    "allowed_memory_classes": ("working_operational",),
                    "approved_by": None,
                    "activated_at": None,
                }
            )
            service._activate(revision, actor_id="human_admin")

            restarted = ExternalCoreService(temp_dir)
            current = restarted.settings.active_for(SettingsLayer.ROLE, "research_colleague")
            self.assertEqual("human_admin", current.created_by)
            self.assertEqual(("working_operational",), current.allowed_memory_classes)


if __name__ == "__main__":
    unittest.main()
