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
            active = [item for item in settings if item["status"] == "active"]
            self.assertEqual(4, len(active))
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
            self.assertEqual(
                "sandbox",
                effective["external_ai_mode"],
            )
            self.assertEqual(3, len(effective["applied_revisions"]))

    def test_participant_role_cannot_gain_research_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ExternalCoreService(temp_dir)
            effective = service.effective(
                role="participant_guide",
                domain_id="health_model_research",
            )
            self.assertIn("participant_guidance", effective["allowed_capabilities"])
            self.assertNotIn("statistical_analysis", effective["allowed_capabilities"])
            self.assertEqual(("public",), tuple(effective["allowed_data_classes"]))

    def test_contract_reports_no_external_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract = ExternalCoreService(temp_dir).contract()
            self.assertFalse(contract["external_ai_provider_registered"])
            self.assertTrue(contract["rules"]["lower_layers_may_only_restrict"])

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

            self.assertEqual(
                "sandbox",
                recovered.contract()["external_ai_mode"],
            )
            self.assertEqual(
                "sandbox",
                recovered.effective(
                    role="research_colleague",
                    domain_id="health_model_research",
                )["external_ai_mode"],
            )
            self.assertEqual(
                ("public",),
                tuple(
                    recovered.effective(
                        role="participant_guide",
                        domain_id="health_model_research",
                    )["allowed_data_classes"]
                ),
            )


if __name__ == "__main__":
    unittest.main()
