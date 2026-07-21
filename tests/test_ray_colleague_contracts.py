from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ray_colleague.context import RayContextResolver
from ray_colleague.contracts import (
    ClaimKind,
    ConfidenceBand,
    LearningStatus,
    MemoryScope,
    RayClaim,
    RayRole,
)
from ray_colleague.learning import LearningCandidate, LearningRegistry
from ray_colleague.memory import MemoryRecord, RayMemoryStore
from ray_colleague.service import RayColleagueService
from ray_colleague.evidence import EvidenceRecord, EvidenceRegistry


class RayContextContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = RayContextResolver()

    def test_roles_have_separate_page_capabilities(self) -> None:
        researcher = self.resolver.resolve(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="research_workspace",
            language="ru",
        )
        self.assertIn("track_project_decision", researcher.allowed_capabilities)

        with self.assertRaises(PermissionError):
            self.resolver.resolve(
                role=RayRole.PARTICIPANT_GUIDE,
                owner_id="participant-1",
                session_id="session-1",
                page_id="research_workspace",
                language="ru",
            )

    def test_participant_cannot_request_other_participant_data(self) -> None:
        with self.assertRaises(PermissionError):
            self.resolver.resolve(
                role=RayRole.PARTICIPANT_GUIDE,
                owner_id="participant-1",
                session_id="session-1",
                page_id="pilot",
                language="en",
                selection={"raw_other_participant_data": True},
            )

    def test_raw_payload_is_rejected_for_both_roles(self) -> None:
        with self.assertRaises(ValueError):
            self.resolver.resolve(
                role=RayRole.RESEARCH_COLLEAGUE,
                owner_id="researcher-1",
                page_id="data_preparation",
                language="es",
                selection={"raw_answers": [1, 2, 3]},
            )

    def test_nested_raw_payload_is_also_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.resolver.resolve(
                role=RayRole.RESEARCH_COLLEAGUE,
                owner_id="researcher-1",
                page_id="data_preparation",
                language="ru",
                selection={"dataset": {"raw_sensor_stream": [1, 2]}},
            )


class RayEvidenceContractTests(unittest.TestCase):
    def test_scientific_claim_requires_registered_evidence_id(self) -> None:
        claim = RayClaim(
            text="Unsupported scientific statement",
            kind=ClaimKind.SCIENTIFIC_EVIDENCE,
            confidence=ConfidenceBand.HIGH,
        )
        with self.assertRaises(ValueError):
            claim.validate()

    def test_evidence_registry_requires_version_population_and_limitations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = EvidenceRegistry(Path(temp_dir) / "evidence.json")
            record = registry.register(
                EvidenceRecord(
                    title="AI Risk Management Framework",
                    source_type="technical_standard",
                    source_url="https://www.nist.gov/itl/ai-risk-management-framework",
                    citation="NIST AI RMF",
                    publication_date="2023-01-26",
                    source_version="1.0",
                    evidence_level="primary_technical_standard",
                    population="AI systems and affected stakeholders",
                    applicability="Risk management architecture",
                    limitations=("Not a clinical efficacy study",),
                    registered_by="researcher-1",
                )
            )
            self.assertEqual("1.0", record["source_version"])
            self.assertEqual(1, len(registry.list_all()))


class RayServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = RayColleagueService(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_parameter_review_requires_measurement_formula_and_time(self) -> None:
        response = self.service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="model_parameter_constructor",
            language="ru",
            message="Проверь параметр",
            selection={"name": "Pressure"},
        )
        self.assertIn("measurement_binding", response["unresolved"])
        self.assertIn("calculation_rule", response["unresolved"])
        self.assertIn("time_binding", response["unresolved"])

    def test_complete_parameter_context_does_not_invent_missing_items(self) -> None:
        response = self.service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="model_parameter_constructor",
            language="en",
            message="Review this parameter",
            selection={
                "name": "Pressure",
                "preliminary_definition": "Mismatch weighted by significance",
                "question_refs": ["q-1", "q-2"],
                "calculation_rule": "difference_weighted",
                "time_reference": "measurement-time-contract-1",
            },
        )
        self.assertEqual([], response["unresolved"])
        self.assertEqual(2, len(response["next_steps"]))
        self.assertNotIn("review_complete_context", response["next_steps"])
        self.assertEqual("research_colleague", response["role"])
        self.assertEqual("en", response["language"])

    def test_all_supported_languages_produce_questions(self) -> None:
        for language in ("ru", "en", "es"):
            response = self.service.respond(
                role=RayRole.RESEARCH_COLLEAGUE,
                owner_id="researcher-1",
                page_id="scientific_results",
                language=language,
                message="review",
            )
            self.assertTrue(response["clarification_questions"])

    def test_device_help_can_start_before_a_device_is_selected(self) -> None:
        response = self.service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="measurement_setup",
            language="ru",
            message="Помоги подобрать и подключить камеру для регистрации движения",
            selection={
                "measurement_goal": "Регистрация движения",
                "browser_support": {"MediaDevices": True, "WebSerial": False},
            },
        )
        self.assertIn("connector_type", response["unresolved"])
        self.assertIn("device_identity", response["unresolved"])
        self.assertTrue(response["clarification_questions"])

    def test_data_help_uses_profile_without_receiving_raw_records(self) -> None:
        response = self.service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="data_editor",
            language="en",
            message="Explain suitable normalization choices",
            selection={
                "source_type": "sensor_stream",
                "detected_format": "CSV",
                "quality_profile": {"record_count": 40, "missing_count": 2},
                "normalization_candidates": ["robust_z_score"],
                "selected_operations": [],
                "time_reference": "measurement-time-contract-1",
            },
        )
        self.assertNotIn("quality_profile", response["unresolved"])
        self.assertNotIn("time_reference", response["unresolved"])

    def test_qualitative_hypothesis_review_asks_for_real_material_and_method(self) -> None:
        response = self.service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="research_lab",
            language="ru",
            message="Проверь качественную гипотезу",
            project_id="project-1",
            selection={
                "hypothesis_mode": "humanities_qualitative",
                "basis_items": [{"title": "Theory"}],
                "variable_roles": [{"role": "focal_phenomenon"}],
                "formal_statement": "How is recovery described?",
                "falsification_criteria": "Negative cases",
                "time_relation": "not_applicable",
                "planned_analysis": [],
                "qualitative_inquiry": {
                    "research_question": "How is recovery described?",
                    "evidence_sources": [],
                    "selected_method_ids": [],
                    "disconfirming_evidence_rule": "Negative cases",
                    "trustworthiness_strategy_ids": [],
                },
            },
        )
        self.assertIn("qualitative_empirical_material", response["unresolved"])
        self.assertIn("qualitative_method", response["unresolved"])
        self.assertIn("qualitative_trustworthiness", response["unresolved"])

    def test_action_requires_allowed_page_capability(self) -> None:
        with self.assertRaises(PermissionError):
            self.service.respond(
                role=RayRole.RESEARCH_COLLEAGUE,
                owner_id="researcher-1",
                page_id="scientific_results",
                language="ru",
                message="Запиши решение",
                requested_action="track_project_decision",
            )

    def test_allowed_action_is_persisted_and_requires_confirmation(self) -> None:
        response = self.service.respond(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            page_id="research_workspace",
            language="ru",
            message="Сохранить решение использовать единое время",
            project_id="project-1",
            requested_action="track_project_decision",
        )
        proposal = response["action_proposals"][0]
        self.assertEqual("proposed", proposal["status"])
        self.assertEqual("Решение проекта", proposal["label"])
        confirmed = self.service.confirm_action(
            proposal["action_id"],
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
        )
        self.assertEqual("confirmed", confirmed["status"])


class RayMemoryIsolationTests(unittest.TestCase):
    def test_memory_is_isolated_by_role_and_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = RayMemoryStore(Path(temp_dir) / "memory.json")
            store.add(
                MemoryRecord(
                    role=RayRole.RESEARCH_COLLEAGUE,
                    owner_id="researcher-1",
                    scope=MemoryScope.PROJECT,
                    project_id="project-1",
                    summary="Use unified time contract",
                    provenance={"source": "human_confirmation"},
                    retention_reason="project_decision",
                )
            )
            store.add(
                MemoryRecord(
                    role=RayRole.PARTICIPANT_GUIDE,
                    owner_id="participant-1",
                    scope=MemoryScope.SESSION,
                    session_id="session-1",
                    summary="Participant requested clarification",
                    provenance={"source": "participant_confirmation"},
                    retention_reason="session_continuity",
                )
            )
            researcher_records = store.list_for_owner(
                RayRole.RESEARCH_COLLEAGUE,
                "researcher-1",
            )
            participant_records = store.list_for_owner(
                RayRole.PARTICIPANT_GUIDE,
                "participant-1",
            )
            self.assertEqual(1, len(researcher_records))
            self.assertEqual(1, len(participant_records))
            self.assertNotEqual(
                researcher_records[0]["record_id"],
                participant_records[0]["record_id"],
            )

    def test_memory_expiry_requires_timezone(self) -> None:
        record = MemoryRecord(
            role=RayRole.RESEARCH_COLLEAGUE,
            owner_id="researcher-1",
            scope=MemoryScope.PROJECT,
            project_id="project-1",
            summary="Decision",
            provenance={"source": "human_confirmation"},
            retention_reason="project_decision",
            expires_at="2027-01-01T00:00:00",
        )
        with self.assertRaises(ValueError):
            record.validate()


class RayLearningLifecycleTests(unittest.TestCase):
    def test_active_learning_requires_trial_evaluation_and_human_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = LearningRegistry(Path(temp_dir) / "learning.json")
            candidate = registry.add(
                LearningCandidate(
                    role=RayRole.RESEARCH_COLLEAGUE,
                    submitted_by="researcher-1",
                    target_type="response_rule",
                    target_id="rule-1",
                    feedback="Ask about time binding",
                    expected_behavior="Always check unified time",
                    context_scope="model_parameter_constructor",
                )
            )
            registry.transition(
                candidate["candidate_id"],
                LearningStatus.TRIAL,
                evaluation={"cases": 12, "passed": 12},
            )
            with self.assertRaises(ValueError):
                registry.transition(
                    candidate["candidate_id"],
                    LearningStatus.ACTIVE,
                    evaluation={"cases": 30, "passed": 30},
                )
            active = registry.transition(
                candidate["candidate_id"],
                LearningStatus.ACTIVE,
                evaluation={"cases": 30, "passed": 30},
                approved_by="research-lead",
            )
            self.assertEqual("active", active["status"])


if __name__ == "__main__":
    unittest.main()
