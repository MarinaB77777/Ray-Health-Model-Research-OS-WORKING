import unittest

from research.analyses.health_model.constellation_layer import build_constellation_layer
from research.analyses.health_model.mechanism_layer import (
    _mechanism_score,
    _status_for_score,
)


class MechanismEvidenceStateTests(unittest.TestCase):
    def test_missing_required_functions_do_not_create_penalized_evidence(self):
        score = _mechanism_score(
            functions={"a": {"strength": 4.0}},
            required_functions=["a", "b"],
            supporting_functions=[],
            minimum_required=2,
        )
        self.assertIsNone(score)

    def test_observed_zero_is_not_confused_with_missing_data(self):
        self.assertEqual(_status_for_score(None), "NOT_ENOUGH_DATA")
        self.assertEqual(_status_for_score(0.0), "NOT_SUPPORTED")

    def test_below_threshold_constellation_is_not_suspected(self):
        result = build_constellation_layer({
            "mechanisms": {
                "resource_exhaustion": {"score": 1.0},
                "decision_degradation": {"score": 1.0},
            },
        })
        item = result["constellations"]["self_worsening_trajectory"]
        self.assertEqual(item["status"], "NOT_SUPPORTED")
        self.assertNotIn("self_worsening_trajectory", result["suspected_constellations"])


if __name__ == "__main__":
    unittest.main()
