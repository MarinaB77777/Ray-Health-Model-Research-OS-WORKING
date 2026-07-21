from __future__ import annotations

import unittest

from research.qualitative_hypothesis import (
    build_qualitative_hypothesis_plan,
    build_qualitative_hypothesis_result,
    compatible_qualitative_methods,
    qualitative_hypothesis_contract,
)


class QualitativeHypothesisTests(unittest.TestCase):
    def material(self):
        return {
            "origin": "registered", "evidence_role": "empirical_material",
            "entity_ref": "interviews-1", "entity_type": "interview_corpus",
            "version": 2, "title": "Participant interviews",
        }

    def test_question_definition_and_time_axis_are_not_empirical_material_types(self):
        contract = qualitative_hypothesis_contract()
        self.assertNotIn("question", contract["empirical_entity_types"])
        self.assertNotIn("time_variable", contract["empirical_entity_types"])
        self.assertIn("question_definition_is_not_empirical_evidence", contract["invariants"])

    def test_exploratory_question_does_not_require_false_null_hypothesis(self):
        plan = build_qualitative_hypothesis_plan({
            "inquiry_mode": "exploratory_question",
            "objects": [{"role": "focal_phenomenon", "display_name": "Recovery experience", "working_definition": "How recovery is described after illness"}],
            "evidence_sources": [self.material()],
            "research_question": "How do participants describe recovery?",
            "sampling_strategy": "Purposeful maximum-variation sampling",
            "disconfirming_evidence_rule": "Actively examine cases contradicting the dominant interpretation",
            "selected_method_ids": ["reflexive_thematic_analysis"],
            "trustworthiness_strategy_ids": ["negative_case_analysis", "reflexive_audit_trail"],
        })
        self.assertTrue(plan["readiness"]["valid"])
        self.assertEqual("health-model-qualitative-hypothesis-result-1", plan["result_contract"]["schema_version"])

    def test_theory_informed_proposition_requires_theory_source(self):
        plan = build_qualitative_hypothesis_plan({
            "inquiry_mode": "theory_informed_proposition",
            "objects": [{"role": "construct", "display_name": "Trust"}],
            "evidence_sources": [self.material()],
            "research_question": "How is trust negotiated?", "proposition": "Trust is negotiated through repeated repair.",
            "disconfirming_evidence_rule": "Cases with trust and no repair",
            "selected_method_ids": ["framework_analysis"],
            "trustworthiness_strategy_ids": ["triangulation"],
        })
        self.assertIn("THEORY_OR_FRAMEWORK_SOURCE_REQUIRED", plan["readiness"]["issues"])

    def test_method_filter_uses_material_type_and_inquiry_mode(self):
        methods = compatible_qualitative_methods("process_mechanism_proposition", ["interview_corpus"])
        tracing = next(x for x in methods if x["method_id"] == "process_tracing")
        self.assertTrue(tracing["compatible"])
        ipa = next(x for x in methods if x["method_id"] == "interpretative_phenomenological_analysis")
        self.assertFalse(ipa["compatible"])

    def test_result_preserves_evidence_counterevidence_limits_and_uncertainty(self):
        result = build_qualitative_hypothesis_result({
            "hypothesis_ref": "hyp-1", "hypothesis_version": 3,
            "outcome_status": "partially_supported",
            "plain_language_conclusion": "The proposed process appears in some, but not all, cases.",
            "evidence_links": ["interviews-1:v2"], "counterevidence_links": ["case-7"],
            "findings": ["repair sequence"], "context_and_transferability": "Pilot participants only",
            "limitations": ["small purposive sample"], "uncertainty_note": "Transferability remains uncertain",
        })
        self.assertTrue(result["validation"]["valid"])
        self.assertEqual(["case-7"], result["counterevidence_links"])


if __name__ == "__main__":
    unittest.main()
