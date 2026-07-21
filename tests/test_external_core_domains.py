from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from external_core.domains import (
    DomainCapability,
    DomainDependency,
    DomainLifecycle,
    DomainOperation,
    DomainRayRegistry,
    DomainRisk,
    health_model_research_domain,
)


class DomainRayRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = DomainRayRegistry(
            Path(self.temp_dir.name) / "domains.json"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_health_model_domain_has_four_real_capability_packs(self) -> None:
        domain = health_model_research_domain(
            owner_id="health_model_team",
            created_by="research_lead",
        )
        domain.validate()
        self.assertEqual("health_model_research", domain.domain_id)
        self.assertEqual(4, len(domain.capabilities))
        self.assertFalse(domain.external_ai_allowed)
        self.assertFalse(domain.direct_external_execution_allowed)

    def test_domain_follows_proposed_sandboxed_registered_active_path(self) -> None:
        domain = health_model_research_domain(
            owner_id="health_model_team",
            created_by="research_lead",
        )
        self.registry.register_proposal(domain)
        self.registry.transition(
            domain.domain_id,
            DomainLifecycle.SANDBOXED,
            actor_id="research_lead",
        )
        self.registry.transition(
            domain.domain_id,
            DomainLifecycle.REGISTERED,
            actor_id="research_lead",
        )
        active = self.registry.transition(
            domain.domain_id,
            DomainLifecycle.ACTIVE,
            actor_id="research_lead",
        )
        self.assertEqual("active", active["lifecycle"])
        self.assertEqual("research_lead", active["approved_by"])

    def test_domain_cannot_skip_sandbox_and_registration(self) -> None:
        domain = health_model_research_domain(
            owner_id="health_model_team",
            created_by="research_lead",
        )
        self.registry.register_proposal(domain)
        with self.assertRaises(ValueError):
            self.registry.transition(
                domain.domain_id,
                DomainLifecycle.ACTIVE,
                actor_id="research_lead",
            )

    def test_cross_domain_dependency_must_use_runtime(self) -> None:
        dependency = DomainDependency(
            domain_id="sensor_domain",
            interaction_types=("measurement_event",),
            purpose="Receive calibrated observations",
            via_runtime=False,
        )
        with self.assertRaises(PermissionError):
            dependency.validate("health_model_research")

    def test_high_risk_execution_requires_human_confirmation(self) -> None:
        capability = DomainCapability(
            capability_id="statistical_execution",
            operations=(DomainOperation.EXECUTION,),
            resource_scopes=("prepared_datasets",),
            data_classes=("pseudonymized_research",),
            risk=DomainRisk.HIGH,
            requires_human_confirmation=False,
        )
        with self.assertRaises(ValueError):
            capability.validate()

    def test_direct_external_execution_is_forbidden(self) -> None:
        domain = health_model_research_domain(
            owner_id="health_model_team",
            created_by="research_lead",
        )
        domain.direct_external_execution_allowed = True
        with self.assertRaises(PermissionError):
            domain.validate()


if __name__ == "__main__":
    unittest.main()
