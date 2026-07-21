from __future__ import annotations

import unittest

from research.sensor_hypothesis import (
    build_sensor_validation_plan,
    compatible_sensor_methods,
    sensor_hypothesis_contract,
)


class SensorHypothesisTests(unittest.TestCase):
    def sources(self):
        return [
            {"source_role": "sensor_candidate", "entity_ref": "sensor-1", "display_name": "Camera feature", "entity_type": "measurement_dataset", "version": 2},
            {"source_role": "questionnaire_anchor", "entity_ref": "physical-score", "display_name": "Physical state score", "entity_type": "questionnaire_result", "version": 1},
            {"source_role": "time_axis", "entity_ref": "utc", "display_name": "UTC observation time", "entity_type": "time_variable", "version": 1},
        ]

    def test_correlation_is_not_registered_as_agreement_method(self):
        contract = sensor_hypothesis_contract()
        self.assertIn("correlation_is_not_agreement", contract["invariants"])
        agreement = next(x for x in contract["methods"] if x["method_id"] == "bland_altman_repeated")
        self.assertEqual("absolute_agreement_bias_and_limits", agreement["purpose"])
        self.assertEqual("registered_without_validated_runner", agreement["execution_status"])
        pearson = next(x for x in contract["methods"] if x["method_id"] == "pearson_association")
        self.assertEqual("linear_association_not_agreement", pearson["purpose"])

    def test_sensor_verification_has_repeatability_and_drift_methods(self):
        methods = compatible_sensor_methods(
            validation_aim="device_verification", outcome_data_kind="continuous_signal",
            repeated_measurements=True, has_reference=False,
        )
        compatible_ids = {x["method_id"] for x in methods if x["compatible"]}
        self.assertIn("repeatability_measurement_error", compatible_ids)
        self.assertIn("sensor_drift_analysis", compatible_ids)

    def test_discrepancy_plan_binds_sensor_questionnaire_and_time(self):
        plan = build_sensor_validation_plan({
            "validation_aim": "sensor_questionnaire_discrepancy",
            "outcome_data_kind": "continuous_signal",
            "repeated_measurements": True,
            "data_sources": self.sources(),
            "pairing_strategy": "window_aggregate", "pairing_tolerance": "PT5M",
            "observation_unit": "participant-session-window", "independence_unit": "participant",
            "discrepancy_metric": "standardized_difference",
            "harmonization_rule": "z-score within registered calibration population",
            "acceptance_threshold": "prespecified clinically meaningful bound",
            "selected_method_ids": ["mixed_effects_regression", "state_space_model"],
        })
        self.assertTrue(plan["readiness"]["valid"])
        self.assertEqual("UTC", plan["pairing"]["axis"])
        self.assertEqual(2, len(plan["selected_methods"]))

    def test_method_comparison_requires_reference_not_questionnaire_anchor(self):
        plan = build_sensor_validation_plan({
            "validation_aim": "analytical_validation", "outcome_data_kind": "continuous_signal",
            "repeated_measurements": True, "data_sources": self.sources(),
            "pairing_strategy": "exact_utc", "observation_unit": "paired measurement",
            "independence_unit": "participant", "selected_method_ids": ["bland_altman_repeated"],
        })
        self.assertFalse(plan["readiness"]["valid"])
        self.assertIn("CRITERION_REFERENCE_REQUIRED_FOR_METHOD_COMPARISON", plan["readiness"]["issues"])

    def test_non_repeated_method_is_blocked_for_repeated_measurements(self):
        methods = compatible_sensor_methods(
            validation_aim="analytical_validation", outcome_data_kind="continuous_signal",
            repeated_measurements=True, has_reference=True,
        )
        deming = next(x for x in methods if x["method_id"] == "deming_regression")
        self.assertFalse(deming["compatible"])
        self.assertIn("REPEATED_MEASUREMENTS_UNSUPPORTED", deming["incompatibility_reasons"])


if __name__ == "__main__":
    unittest.main()
