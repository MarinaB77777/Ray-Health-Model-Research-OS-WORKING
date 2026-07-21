from __future__ import annotations

import unittest

from research.hypothesis_builder import build_hypothesis_definition, hypothesis_contract


class HypothesisBuilderTests(unittest.TestCase):
    def test_draft_requires_only_title_and_keeps_structured_roles(self):
        result = build_hypothesis_definition({
            "title": "Recovery and decision quality", "status": "draft",
            "basis_items": [{"type": "observation", "title": "Pilot pattern"}],
            "variables": [{"role": "outcome", "entity_ref": "quality-v2",
                           "display_name": "Decision quality", "entity_type": "model_parameter", "version": 2}],
        })
        self.assertTrue(result["readiness"]["valid_for_status"])
        self.assertEqual("outcome", result["variables"][0]["role"])
        self.assertEqual(2, result["variables"][0]["version"])

    def test_trial_reports_missing_elements_and_ray_candidate_is_not_evidence(self):
        result = build_hypothesis_definition({
            "title": "Candidate", "status": "trial",
            "basis_items": [{"type": "ray_candidate", "title": "Candidate relation"}],
            "variables": [],
        })
        self.assertFalse(result["readiness"]["valid_for_status"])
        self.assertIn("outcome", result["readiness"]["missing"])
        self.assertEqual("candidate_not_evidence", result["basis_items"][0]["evidence_status"])
        self.assertIn("hypothesis_is_not_fact", hypothesis_contract()["invariants"])

    def test_technical_hypothesis_supports_multiple_predictors_and_utc_time(self):
        result = build_hypothesis_definition({
            "hypothesis_mode": "technical_quantitative", "title": "Dynamic pressure", "status": "trial",
            "basis_items": [{"type": "prior_result", "title": "Pilot result"}],
            "variables": [
                {"role": "outcome", "entity_ref": "pressure-v1", "display_name": "Pressure", "entity_type": "parameter_result", "version": 1},
                {"role": "predictor", "entity_ref": "importance-v2", "display_name": "Importance", "entity_type": "questionnaire_result", "version": 2, "expected_direction": "positive"},
                {"role": "predictor", "entity_ref": "discrepancy-v1", "display_name": "Discrepancy", "entity_type": "parameter_result", "version": 1, "expected_direction": "positive", "lag": "PT5M"},
                {"role": "time", "entity_ref": "utc-time", "display_name": "Observation time", "entity_type": "time_variable", "version": 1},
            ],
            "model_family": "longitudinal_mixed", "time_axis_included": True,
            "time_relation": "Predictors at t0 precede pressure at t1",
            "formal_statement": "Pressure depends on importance and discrepancy over time.",
            "falsification_criteria": "Neither predictor improves the prespecified model.",
            "sensor_validation": {
                "validation_aim": "clinical_construct_validation", "outcome_data_kind": "continuous_signal",
                "repeated_measurements": True,
                "data_sources": [
                    {"source_role": "sensor_candidate", "entity_ref": "sensor", "display_name": "Sensor signal", "entity_type": "measurement_dataset", "version": 1, "measurement_scale_ref": "ratio", "unit": "signal_unit", "time_contract": {"axis": "UTC"}},
                    {"source_role": "physical_state_anchor", "entity_ref": "state", "display_name": "Physical state", "entity_type": "measurement_dataset", "version": 1, "measurement_scale_ref": "ratio", "unit": "state_unit", "time_contract": {"axis": "UTC"}},
                    {"source_role": "time_axis", "entity_ref": "time", "display_name": "UTC time", "entity_type": "time_variable", "version": 1, "measurement_scale_ref": "datetime", "unit": "UTC", "time_contract": {"axis": "UTC"}},
                ],
                "pairing_strategy": "nearest_within_tolerance", "pairing_tolerance": "PT1M",
                "observation_unit": "participant-time", "independence_unit": "participant",
                "selected_method_ids": ["mixed_effects_regression"],
            },
        })
        self.assertTrue(result["readiness"]["valid_for_status"])
        self.assertEqual(2, result["technical_model"]["predictor_count"])
        self.assertEqual("UTC", result["technical_model"]["time_axis"])
        self.assertIn("Importance", result["technical_model"]["canonical_model"])

    def test_complete_qualitative_inquiry_uses_objects_not_fake_outcome_variable(self):
        result = build_hypothesis_definition({
            "hypothesis_mode": "humanities_qualitative", "title": "Recovery narratives", "status": "trial",
            "basis_items": [{"type": "qualitative_material", "title": "Interview corpus", "registered_ref": "corpus-1"}],
            "variables": [], "formal_statement": "How do participants describe recovery?",
            "falsification_criteria": "Search for cases contradicting the proposed interpretation",
            "planned_analysis": ["reflexive_thematic_analysis"],
            "qualitative_inquiry": {
                "inquiry_mode": "exploratory_question",
                "objects": [{"role": "focal_phenomenon", "display_name": "Recovery experience", "working_definition": "Participant descriptions of recovery"}],
                "evidence_sources": [{"origin": "registered", "evidence_role": "empirical_material", "entity_ref": "corpus-1", "entity_type": "interview_corpus", "version": 1, "title": "Interview corpus"}],
                "research_question": "How do participants describe recovery?",
                "disconfirming_evidence_rule": "Search for negative cases",
                "selected_method_ids": ["reflexive_thematic_analysis"],
                "trustworthiness_strategy_ids": ["negative_case_analysis"],
            },
        })
        self.assertTrue(result["readiness"]["valid_for_status"])
        self.assertTrue(result["qualitative_inquiry"]["readiness"]["valid"])

    def test_technical_trial_reports_missing_predictor_model_and_time(self):
        result = build_hypothesis_definition({
            "hypothesis_mode": "technical_quantitative", "title": "Incomplete", "status": "trial",
            "basis_items": [{"type": "observation", "title": "Observation"}],
            "variables": [{"role": "outcome", "entity_ref": "y", "display_name": "Y"}],
            "formal_statement": "Y changes.", "falsification_criteria": "No change.",
            "time_axis_included": True,
        })
        self.assertFalse(result["readiness"]["valid_for_status"])
        self.assertTrue({"predictor", "model_family", "time_relation", "SENSOR_VALIDATION_PLAN_NOT_CONFIGURED"}.issubset(result["readiness"]["missing"]))
        self.assertNotIn("time_variable", result["readiness"]["missing"])
        self.assertEqual("UTC", result["technical_model"]["time_axis"])


if __name__ == "__main__":
    unittest.main()
