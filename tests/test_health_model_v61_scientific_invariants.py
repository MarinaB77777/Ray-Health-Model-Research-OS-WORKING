import unittest

from research.analyses.health_model.v61_calculator import (
    calculate_critical_status,
    calculate_external_pressure_values,
    calculate_load_blocks,
    calculate_load_failure_risk,
    calculate_manifestation_layer,
)


class HealthModelV61ScientificInvariantTests(unittest.TestCase):
    def test_observed_zero_external_pressure_remains_observed_zero(self):
        self.assertEqual(calculate_external_pressure_values({"e5": 0}), [0.0])

    def test_missing_additional_load_is_not_replaced_with_zero(self):
        result = calculate_load_blocks({"d7": 2})
        self.assertIsNone(result["l_additional"])
        self.assertEqual(result["status"], "completed_with_partial_inputs")
        self.assertIn("l_environment_additional", result["missing_components"])

    def test_unknown_load_failure_component_is_not_zero(self):
        result = calculate_load_failure_risk(
            load={"l_external": None, "l_environment": 2},
            resources={
                "r_phys": None,
                "r_psych": 2,
                "r_social": 2,
                "r_spiritual": 2,
                "r_goal": 2,
            },
            answers={},
        )
        self.assertIsNone(result["p1"])
        self.assertIsNone(result["p2"])
        self.assertIsNone(result["p3"])
        self.assertIsNone(result["p4"])
        self.assertEqual(result["p5"], 0.0)
        self.assertEqual(result["status"], "completed_with_partial_inputs")

    def test_missing_critical_markers_produce_unknown_not_false(self):
        result = calculate_critical_status({})
        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["is_critical"])

    def test_any_observed_critical_threshold_still_overrides(self):
        result = calculate_critical_status({"k23": 3})
        self.assertEqual(result["status"], "critical")
        self.assertTrue(result["is_critical"])

    def test_partial_manifestation_is_explicit(self):
        result = calculate_manifestation_layer({"k1": 2})
        self.assertEqual(result["manifestation_score"], 2.0)
        self.assertEqual(result["status"], "completed_with_partial_inputs")
        self.assertEqual(result["observed_marker_count"], 1)
        self.assertEqual(len(result["missing_markers"]), 21)


if __name__ == "__main__":
    unittest.main()
