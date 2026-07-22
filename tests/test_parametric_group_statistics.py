import math
import unittest

from assessment.analysis.runners.independent_t import run_independent_t_test
from assessment.analysis.runners.one_way_anova import run_one_way_anova
from assessment.analysis.statistics.parametric_groups import (
    collect_independent_groups,
    independent_samples_t_test,
    one_way_anova,
)
from assessment.analysis.statistics.p_value import (
    f_distribution_survival_function,
    student_t_two_tailed_p_value,
)


def records(groups):
    result = []
    for index, (group, outcome) in enumerate(groups):
        subject = f"p-{index}"
        result.extend([
            {
                "participant_id": subject,
                "question_code": "outcome",
                "answer_value": outcome,
                "scale_type": "ratio",
            },
            {
                "participant_id": subject,
                "question_code": "group",
                "answer_value": group,
                "scale_type": "nominal",
            },
        ])
    return result


class DistributionTests(unittest.TestCase):
    def test_student_t_uses_t_distribution(self):
        p_value = student_t_two_tailed_p_value(
            t_statistic=3.6742346141747673,
            degrees_of_freedom=4,
        )
        self.assertAlmostEqual(p_value, 0.0213116411, places=9)

    def test_f_survival_uses_f_distribution(self):
        p_value = f_distribution_survival_function(
            f_statistic=13.0,
            numerator_degrees_of_freedom=2,
            denominator_degrees_of_freedom=6,
        )
        self.assertAlmostEqual(p_value, 0.006591796875, places=12)


class ParametricGroupCalculationTests(unittest.TestCase):
    def test_equal_variance_independent_t(self):
        result = independent_samples_t_test(
            groups={"A": [1, 2, 3], "B": [4, 5, 6]},
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["variant"], "student_equal_variance")
        self.assertAlmostEqual(result["test_statistic"], -3.6742346141747673)
        self.assertAlmostEqual(result["degrees_of_freedom"], 4.0)
        self.assertAlmostEqual(result["p_value"], 0.0213116411, places=9)

    def test_one_way_anova_table_and_f_probability(self):
        result = one_way_anova(
            groups={"A": [1, 2, 3], "B": [2, 3, 4], "C": [5, 6, 7]},
        )
        self.assertTrue(result["ok"])
        self.assertAlmostEqual(result["sum_of_squares_between"], 26.0)
        self.assertAlmostEqual(result["sum_of_squares_within"], 6.0)
        self.assertAlmostEqual(result["test_statistic"], 13.0)
        self.assertEqual(result["numerator_degrees_of_freedom"], 2)
        self.assertEqual(result["denominator_degrees_of_freedom"], 6)
        self.assertAlmostEqual(result["p_value"], 0.006591796875, places=12)

    def test_group_direction_comes_from_scale_metadata(self):
        data = records([
            ("A", 1.0), ("A", 2.0), ("A", 3.0),
            ("B", 4.0), ("B", 5.0), ("B", 6.0),
        ])
        collected = collect_independent_groups(
            answer_records=data,
            left_question_code="outcome",
            right_question_code="group",
        )
        self.assertTrue(collected["ok"])
        self.assertEqual(collected["group_question_code"], "group")
        self.assertEqual(collected["outcome_question_code"], "outcome")
        self.assertEqual(collected["groups"], {"A": [1.0, 2.0, 3.0], "B": [4.0, 5.0, 6.0]})

    def test_repeated_unit_is_rejected_not_overwritten(self):
        data = records([("A", 1.0), ("B", 2.0)])
        data.append({
            "participant_id": "p-0",
            "question_code": "outcome",
            "answer_value": 99,
            "scale_type": "ratio",
        })
        collected = collect_independent_groups(
            answer_records=data,
            left_question_code="group",
            right_question_code="outcome",
        )
        self.assertFalse(collected["ok"])
        self.assertEqual(collected["status"], "repeated_observations_require_explicit_selection")

    def test_runner_outputs_full_anova_result(self):
        data = records([
            ("A", 1.0), ("A", 2.0), ("A", 3.0),
            ("B", 2.0), ("B", 3.0), ("B", 4.0),
            ("C", 5.0), ("C", 6.0), ("C", 7.0),
        ])
        result = run_one_way_anova(
            study_id="study",
            left_question_code="outcome",
            right_question_code="group",
            answer_records=data,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["test_statistic_name"], "F")
        self.assertEqual(result["p_value_distribution"], "f")
        self.assertIn("anova_table", result)

    def test_runner_outputs_student_t_probability(self):
        data = records([
            ("A", 1.0), ("A", 2.0), ("A", 3.0),
            ("B", 4.0), ("B", 5.0), ("B", 6.0),
        ])
        result = run_independent_t_test(
            study_id="study",
            left_question_code="group",
            right_question_code="outcome",
            answer_records=data,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["p_value_distribution"], "student_t")
        self.assertAlmostEqual(result["p_value"], 0.0213116411, places=9)


if __name__ == "__main__":
    unittest.main()
