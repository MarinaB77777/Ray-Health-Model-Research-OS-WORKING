from __future__ import annotations

import unittest

from research.probabilistic.numerics import beta_quantile, regularized_beta, student_t_cdf, student_t_quantile
from research.probabilistic.registry import EXECUTABLE_PROBABILISTIC_METHOD_IDS, list_probabilistic_methods
from research.probabilistic.service import ProbabilisticMethodError, run_probabilistic_method


class ProbabilisticMethodTests(unittest.TestCase):
    def execute(self, method_id: str, payload: dict):
        return run_probabilistic_method(
            method_id=method_id,
            payload=payload,
            actor_account_id="account-1",
            project_id="project-1",
            block_id="block-1",
        )

    def test_beta_numerics_match_uniform_distribution(self):
        self.assertAlmostEqual(regularized_beta(0.25, 1, 1), 0.25, places=10)
        self.assertAlmostEqual(beta_quantile(0.025, 1, 1), 0.025, places=9)
        self.assertAlmostEqual(beta_quantile(0.975, 1, 1), 0.975, places=9)
        self.assertAlmostEqual(student_t_cdf(0, 10), 0.5, places=12)
        self.assertAlmostEqual(student_t_quantile(0.975, 10), 2.228138852, places=6)

    def test_beta_binomial_has_posterior_and_provenance(self):
        analysis = self.execute(
            "bayesian_beta_binomial",
            {"successes": 5, "trials": 10, "prior_alpha": 1, "prior_beta": 1},
        )
        self.assertAlmostEqual(analysis["result"]["estimate"], 0.5)
        self.assertEqual(analysis["result"]["posterior"]["alpha"], 6)
        self.assertEqual(analysis["time_reference"]["global_time_reference"], "UTC")
        self.assertFalse(analysis["provenance"]["external_statistical_software_used"])
        self.assertEqual(analysis["context"]["project_id"], "project-1")

    def test_dirichlet_probabilities_sum_to_one(self):
        analysis = self.execute(
            "bayesian_dirichlet_multinomial",
            {"counts": [2, 3, 5], "prior_concentration": [1, 1, 1]},
        )
        probabilities = analysis["result"]["posterior_predictive_probabilities"]
        self.assertAlmostEqual(sum(probabilities), 1.0, places=12)
        self.assertEqual(len(analysis["result"]["categories"]), 3)

    def test_normal_inverse_gamma_returns_mean_and_predictive_interval(self):
        analysis = self.execute(
            "bayesian_normal_inverse_gamma",
            {"values": [1, 2, 3, 4, 5], "prior_mean": 0, "prior_mean_strength": 0.1, "prior_shape": 1, "prior_scale": 1},
        )
        result = analysis["result"]
        self.assertLess(result["credible_interval_mean"]["lower"], result["estimate"])
        self.assertGreater(result["credible_interval_mean"]["upper"], result["estimate"])
        self.assertEqual(result["posterior_predictive"]["distribution"], "student_t")

    def test_bootstrap_is_reproducible_and_reports_valid_resamples(self):
        payload = {"values": [1, 2, 3, 4, 5], "statistic": "mean", "resamples": 500, "random_seed": 77}
        first = self.execute("bootstrap_percentile", payload)["result"]
        second = self.execute("bootstrap_percentile", payload)["result"]
        self.assertEqual(first, second)
        self.assertEqual(first["requested_resamples"], 500)
        self.assertEqual(first["valid_resamples"], 500)

    def test_permutation_uses_exact_enumeration_when_feasible(self):
        result = self.execute(
            "permutation_difference_means",
            {"left_values": [1, 2], "right_values": [3, 4], "permutations": 500},
        )["result"]
        self.assertTrue(result["exact"])
        self.assertEqual(result["permutations_evaluated"], 6)
        self.assertTrue(0 <= result["p_value"] <= 1)

    def test_markov_transition_rows_are_probability_distributions(self):
        result = self.execute(
            "bayesian_markov_transition",
            {"states": ["calm", "stress"], "sequences": [["calm", "stress", "stress"], ["stress", "calm"]]},
        )["result"]
        for row in result["transition_rows"]:
            self.assertAlmostEqual(sum(item["estimate"] for item in row["transitions"]), 1.0, places=12)

    def test_monte_carlo_is_seeded_and_propagates_uncertainty(self):
        payload = {
            "inputs": [
                {"name": "a", "distribution": "normal", "mean": 10, "standard_deviation": 1},
                {"name": "b", "distribution": "uniform", "low": 1, "high": 3},
            ],
            "operation": "sum",
            "samples": 1000,
            "random_seed": 13,
        }
        first = self.execute("monte_carlo_uncertainty_propagation", payload)["result"]
        second = self.execute("monte_carlo_uncertainty_propagation", payload)["result"]
        self.assertEqual(first, second)
        self.assertEqual(first["samples_valid"], 1000)
        self.assertAlmostEqual(first["estimate"], 12, delta=0.15)

    def test_unvalidated_methods_are_visible_but_cannot_run(self):
        catalog = list_probabilistic_methods("ru")
        logistic = next(item for item in catalog["methods"] if item["method_id"] == "bayesian_logistic_regression")
        self.assertEqual(logistic["execution_status"], "registered_without_validated_runner")
        self.assertNotIn(logistic["method_id"], EXECUTABLE_PROBABILISTIC_METHOD_IDS)
        with self.assertRaisesRegex(ProbabilisticMethodError, "NOT_EXECUTABLE"):
            self.execute(logistic["method_id"], {"outcome": [0, 1]})


if __name__ == "__main__":
    unittest.main()
