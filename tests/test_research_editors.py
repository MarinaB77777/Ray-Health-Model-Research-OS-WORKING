import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from assessment.questionnaire_components import validate_question_measurement_contract
from pilot_session.persistent_store import PilotSessionPersistentStore
from pilot_session.schemas import ParticipantSession
from research.editors.data_lifecycle import assess_empty_session_purge, purge_empty_session
from research.editors.data_pipeline import (
    apply_transformation,
    build_transformation_run_dataset,
    profile_records,
    transform_records,
)
from research.editors.question_registry import (
    active_question_overlays,
    delete_question_draft,
    list_question_versions,
    transition_question_definition,
    upsert_question_draft,
)
from research.editors.question_bank_registry import register_question_bank
from research.editors.model_entity_classification import (
    LOGIC_ENTITY,
    MODEL_PARAMETER,
    enrich_model_entity,
)
from research.editors.model_definition_explainer import explain_model_definition


class ModelEntityEditorTests(unittest.TestCase):
    def base_definition(self, code="state_risk"):
        return {
            "parameter_code": code,
            "parameter_id": "stable-id",
            "definition_version": 3,
            "title": {"ru": "Риск состояния", "en": "State risk", "es": "Riesgo del estado"},
            "parameter_kind": "structured",
            "value_type": "dict",
            "scale_type": "structured",
            "value_schema": {"minimum": None, "maximum": None, "unit": None},
            "meaning": {"construct_definition": {"ru": "", "en": "", "es": ""}},
            "calculation": {
                "calculator_id": "health_model_v6_1",
                "calculation_version": "1",
                "value_path": code,
            },
            "calculation_design": {
                "calculation_mode": "existing_calculator_output",
                "components": [],
                "expression": None,
                "missing_data_rule": {"on_insufficient_data": "not_enough_data"},
            },
            "temporal_design": {
                "observation_time_required": True,
                "global_time_reference_required": True,
                "aggregation": "single_observation",
            },
        }

    def test_classification_overlay_preserves_identity(self):
        source = self.base_definition()
        enriched = enrich_model_entity(source)
        self.assertEqual(enriched["entity_classification"]["entity_class"], MODEL_PARAMETER)
        self.assertEqual(enriched["parameter_id"], source["parameter_id"])
        self.assertEqual(enriched["definition_version"], source["definition_version"])

    def test_registered_control_signal_is_logic_not_model_quantity(self):
        enriched = enrich_model_entity(self.base_definition("forecast_allowed"))
        self.assertEqual(enriched["entity_classification"]["entity_class"], LOGIC_ENTITY)
        self.assertEqual(enriched["entity_classification"]["entity_subtype"], "decision_signal")

    def test_ray_explanation_does_not_invent_missing_formula(self):
        explanation = explain_model_definition(self.base_definition(), "ru")
        self.assertEqual(explanation["completeness"], "trace_only")
        self.assertIn("calculation_design.expression", explanation["missing_fields"])
        self.assertFalse(explanation["contract_evidence"]["formula_registered"])
        self.assertIn("не подменяет их догадкой", explanation["how_it_is_calculated"])

    def test_ray_explanation_is_available_in_all_interface_languages(self):
        source = self.base_definition()
        for lang in ("ru", "en", "es"):
            explanation = explain_model_definition(source, lang)
            self.assertEqual(explanation["language"], lang)
            self.assertTrue(explanation["what_is_calculated"])
            self.assertTrue(explanation["how_it_is_calculated"])


@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class QuestionEditorRegistryTests(unittest.TestCase):
    def definition(self):
        return {
            "bank_id": "bank_a",
            "question_code": "Q1",
            "base_version": 1,
            "translations": {
                "ru": {"prompt": "Вопрос", "answer_options": []},
                "en": {"prompt": "Question", "answer_options": []},
                "es": {"prompt": "Pregunta", "answer_options": []},
            },
            "question_type": "numeric",
            "response_type": "number",
            "scale_type": "ratio",
            "authorship": {"primary_author": "Researcher"},
            "change_reason": "Clarify operational definition",
        }

    def test_versioned_question_lifecycle_and_active_overlay(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            path = Path("registry.json")
            created = upsert_question_draft(self.definition(), actor_id="r-1", path=path)
            self.assertTrue(created["ok"])
            self.assertEqual(created["definition"]["question_version"], 2)
            trial = transition_question_definition(
                "bank_a", "Q1", 2, "trial", actor_id="r-1",
                reason="Ready for trial", path=path,
            )
            self.assertTrue(trial["ok"])
            active = transition_question_definition(
                "bank_a", "Q1", 2, "active", actor_id="r-2",
                reason="Trial approved", path=path,
            )
            self.assertTrue(active["ok"])
            overlay = active_question_overlays("bank_a", "es", path=path)["Q1"]
            self.assertEqual(overlay["prompt"], "Pregunta")
            self.assertEqual(overlay["question_version"], 2)

    def test_non_draft_is_immutable_and_draft_delete_is_audited(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            path = Path("registry.json")
            created = upsert_question_draft(self.definition(), actor_id="r-1", path=path)
            version = created["definition"]["question_version"]
            deleted = delete_question_draft(
                "bank_a", "Q1", version, actor_id="r-1",
                reason="Draft abandoned", path=path,
            )
            self.assertTrue(deleted["ok"])
            self.assertEqual(list_question_versions(path=path), [])
            self.assertTrue(Path("data/research_editor_audit.jsonl").exists())

    def test_question_response_scale_contract_blocks_incompatible_combination(self):
        validation = validate_question_measurement_contract(
            "multiple_choice", "multiple_choice", "ratio", "checkbox"
        )
        self.assertFalse(validation["valid"])
        self.assertIn(
            "RESPONSE_SCALE_INCOMPATIBLE",
            {error["code"] for error in validation["errors"]},
        )

    def test_legacy_slider_response_is_normalized_to_numeric(self):
        validation = validate_question_measurement_contract(
            "slider", "slider", "visual_analog", "slider"
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["normalized"]["response_type"], "numeric")

    def test_new_bank_identity_is_automatic_and_titles_are_language_scoped(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            result = register_question_bank(
                title="Новая научная анкета",
                language="ru",
                actor_id="researcher-1",
                reason="Separate validated instrument",
                path=Path("bank_registry.json"),
            )
            self.assertTrue(result["ok"])
            bank = result["bank"]
            self.assertTrue(bank["bank_id"])
            self.assertTrue(bank["bank_code"].startswith("bank_"))
            self.assertEqual(bank["definition_version"], 1)
            self.assertEqual(bank["development_status"], "draft")
            self.assertEqual(bank["titles"]["ru"], "Новая научная анкета")


class DataTransformationTests(unittest.TestCase):
    def _save_sensor_run(self, records):
        saved = apply_transformation(
            source_type="sensor_observation",
            records=records,
            operations=[],
            context={
                "clock_source": "device_clock",
                "synchronization_reference": "sync-1",
            },
            actor_id="researcher",
            reason="scientific scope test",
            recipe_name="scope-test",
        )
        return saved["run"]["run_id"]

    def test_question_recode_reverse_and_utc_binding(self):
        result = transform_records(
            source_type="question_answer",
            records=[{
                "record_id": "a1", "answer_value": "yes",
                "observation_time": "2026-07-17T12:00:00+02:00",
                "session_id": "s1",
            }],
            operations=[
                {"type": "recode", "mapping": {"yes": 1, "no": 0}},
                {"type": "reverse_score", "minimum": 0, "maximum": 4},
                {"type": "range_check", "minimum": 0, "maximum": 4},
            ],
            context={"clock_source": "server_clock", "synchronization_reference": "study-clock"},
        )
        self.assertEqual(result["records"][0]["value"], 3.0)
        self.assertEqual(result["records"][0]["time_reference"]["global_time_reference"], "UTC")
        self.assertEqual(result["usable_count"], 1)

    def test_sensor_filter_is_real_and_preserves_all_records(self):
        records = [
            {"value": value, "observation_time": f"2026-07-17T12:00:0{i}+00:00"}
            for i, value in enumerate([1, 100, 1])
        ]
        result = transform_records(
            source_type="sensor_observation", records=records,
            operations=[{"type": "median_filter", "window": 3}],
            context={"clock_source": "device_clock", "synchronization_reference": "sync-1"},
        )
        self.assertEqual(len(result["records"]), 3)
        self.assertEqual(result["records"][1]["value"], 1.0)
        self.assertEqual(records[1]["value"], 100)

    def test_quality_profile_recommends_but_never_applies_processing(self):
        records = [
            {"value": value, "observation_time": f"2026-07-17T12:00:0{i}+00:00"}
            for i, value in enumerate([1, None, 3, 100, 5])
        ]
        profile = profile_records(source_type="sensor_observation", records=records)
        self.assertEqual(profile["missing_count"], 1)
        self.assertEqual(records[1]["value"], None)
        self.assertTrue(all(not item["automatic_apply"] for item in profile["recommendations"]))

    def test_interpolation_and_normalization_are_explicit_auditable_operations(self):
        records = [
            {"value": value, "observation_time": f"2026-07-17T12:00:0{i}+00:00"}
            for i, value in enumerate([1, None, 3])
        ]
        result = transform_records(
            source_type="sensor_observation", records=records,
            operations=[
                {"type": "missing_linear_interpolation", "maximum_gap": 1},
                {"type": "min_max_normalize", "target_minimum": -1, "target_maximum": 1},
            ],
            context={"clock_source": "device_clock", "synchronization_reference": "sync-1"},
        )
        self.assertEqual([item["value"] for item in result["records"]], [-1.0, 0.0, 1.0])
        self.assertIn("LINEAR_INTERPOLATION_APPLIED", {flag["code"] for flag in result["records"][1]["quality_flags"]})
        self.assertEqual(records[1]["value"], None)

    def test_sensor_sample_never_treats_repeated_observations_as_independent(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            run_id = self._save_sensor_run([
                {"record_id": "a", "study_id": "study-a", "subject_link_id": "p1", "value": 1, "observation_time": "2026-07-17T12:00:00+00:00"},
                {"record_id": "b", "study_id": "study-a", "subject_link_id": "p1", "value": 2, "observation_time": "2026-07-17T12:01:00+00:00"},
            ])
            rejected = build_transformation_run_dataset(
                run_id=run_id, analysis_scope="sample", repeated_measure_policy="reject_repeated", study_id="study-a",
            )
            self.assertEqual(rejected["selected_observation_count"], 0)
            self.assertEqual(len(rejected["excluded_observations"]), 2)
            latest = build_transformation_run_dataset(
                run_id=run_id, analysis_scope="sample", repeated_measure_policy="latest", study_id="study-a",
            )
            self.assertEqual(latest["selected_observation_count"], 1)
            self.assertEqual(latest["observations"][0]["value"], 2.0)

    def test_sensor_trajectory_is_one_participant_ordered_on_utc(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            run_id = self._save_sensor_run([
                {"study_id": "study-a", "subject_link_id": "p1", "value": 2, "observation_time": "2026-07-17T12:01:00+00:00"},
                {"study_id": "study-a", "subject_link_id": "p2", "value": 9, "observation_time": "2026-07-17T12:00:30+00:00"},
                {"study_id": "study-a", "subject_link_id": "p1", "value": 1, "observation_time": "2026-07-17T12:00:00+00:00"},
            ])
            dataset = build_transformation_run_dataset(
                run_id=run_id, analysis_scope="trajectory", participant_reference="p1", study_id="study-a",
            )
            self.assertTrue(dataset["ok"])
            self.assertEqual([item["value"] for item in dataset["observations"]], [1.0, 2.0])
            self.assertEqual({item["participant_reference"] for item in dataset["observations"]}, {"p1"})

    def test_sensor_groups_and_cross_study_pooling_require_explicit_contracts(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            run_id = self._save_sensor_run([
                {"study_id": "study-a", "subject_link_id": "p1", "value": 1, "observation_time": "2026-07-17T12:00:00+00:00"},
                {"study_id": "study-b", "subject_link_id": "p2", "value": 2, "observation_time": "2026-07-17T12:00:00+00:00"},
            ])
            pooled = build_transformation_run_dataset(run_id=run_id, analysis_scope="sample")
            self.assertEqual(pooled["status"], "study_scope_required")
            grouped = build_transformation_run_dataset(
                run_id=run_id, analysis_scope="groups", study_id="study-a",
            )
            self.assertEqual(grouped["status"], "grouping_contract_required")


class EmptySessionDeletionTests(unittest.TestCase):
    def test_empty_session_requires_exact_confirmation_and_audit_fields(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            store = PilotSessionPersistentStore("data/sessions.json")
            store.save(ParticipantSession(session_id="s-empty", participant_id="p1"))
            assessment = assess_empty_session_purge(store.get("s-empty"), reference_paths=())
            self.assertTrue(assessment["eligible"])
            rejected = purge_empty_session(
                store, "s-empty", actor_id="", reason="", confirmation="DELETE EMPTY SESSION s-empty"
            )
            self.assertFalse(rejected["ok"])
            self.assertIsNotNone(store.get("s-empty"))
            deleted = purge_empty_session(
                store, "s-empty", actor_id="researcher", reason="Participant exited before answering",
                confirmation="DELETE EMPTY SESSION s-empty",
            )
            self.assertTrue(deleted["ok"])
            self.assertIsNone(store.get("s-empty"))
            audit_text = Path("data/research_editor_audit.jsonl").read_text(encoding="utf-8")
            self.assertIn("empty_technical_session_purged", audit_text)
            self.assertNotIn("p1", audit_text)

    def test_session_with_answer_cannot_be_purged(self):
        session = ParticipantSession(session_id="s-data", participant_id="p2", answers={"Q1": 2})
        assessment = assess_empty_session_purge(session, reference_paths=())
        self.assertFalse(assessment["eligible"])
        self.assertIn("SESSION_HAS_ANSWERS", assessment["blockers"])


if __name__ == "__main__":
    unittest.main()
