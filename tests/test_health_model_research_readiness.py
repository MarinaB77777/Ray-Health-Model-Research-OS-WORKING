import unittest

from research.analyses.health_model.readiness_analysis import analyze_research_readiness


class HealthModelResearchReadinessTests(unittest.TestCase):
    def test_two_unrelated_sessions_are_not_a_trajectory(self):
        result = analyze_research_readiness([
            {"session_id": "s1", "participant_id": "p1", "study_id": "a"},
            {"session_id": "s2", "participant_id": "p2", "study_id": "a"},
        ])
        self.assertNotIn("trajectory_analysis", result["available_analyses"])
        self.assertIn("NO_COMPARABLE_REPEATED_SERIES_ON_GLOBAL_TIME_AXIS", result["reason_codes"])

    def test_same_variable_subject_and_global_time_enable_trajectory(self):
        records = [
            {
                "session_id": "s1", "participant_id": "p1", "study_id": "a",
                "parameter_code": "pressure", "observation_time": "2026-01-01T00:00:00Z",
                "global_time_reference": "UTC",
            },
            {
                "session_id": "s2", "participant_id": "p1", "study_id": "a",
                "parameter_code": "pressure", "observation_time": "2026-01-02T00:00:00Z",
                "global_time_reference": "UTC",
            },
        ]
        result = analyze_research_readiness(records)
        self.assertIn("trajectory_analysis", result["available_analyses"])
        self.assertEqual(result["trajectory_series_count"], 1)

    def test_multiple_studies_are_only_a_candidate_until_alignment(self):
        result = analyze_research_readiness([
            {"session_id": "s1", "study_id": "a"},
            {"session_id": "s2", "study_id": "b"},
        ])
        self.assertIn("cross_study_analysis_candidate", result["available_analyses"])
        self.assertIn("cross_study_analysis", result["blocked_analyses"])


if __name__ == "__main__":
    unittest.main()
