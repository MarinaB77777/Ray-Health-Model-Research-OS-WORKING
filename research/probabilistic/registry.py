from __future__ import annotations

from copy import deepcopy


PROBABILISTIC_METHOD_REGISTRY_VERSION = "probabilistic-method-registry-1"


METHODS = [
    {
        "method_id": "bayesian_beta_binomial",
        "family": "bayesian_conjugate",
        "title": {"ru": "Байесовская модель доли", "en": "Bayesian proportion model", "es": "Modelo bayesiano de proporción"},
        "purpose": "posterior_probability_for_binary_event_rate",
        "compatible_scales": ["binary", "probability"],
        "required_inputs": ["successes", "trials"],
        "optional_inputs": ["prior_alpha", "prior_beta", "credible_mass"],
        "diagnostics": ["prior_parameters_reported", "posterior_predictive_probability"],
        "scientific_basis": ["beta_binomial_conjugacy"],
    },
    {
        "method_id": "bayesian_dirichlet_multinomial",
        "family": "bayesian_conjugate",
        "title": {"ru": "Байесовская модель категорий", "en": "Bayesian categorical model", "es": "Modelo bayesiano categórico"},
        "purpose": "posterior_probabilities_for_multiple_categories",
        "compatible_scales": ["nominal", "categorical"],
        "required_inputs": ["counts"],
        "optional_inputs": ["prior_concentration", "credible_mass"],
        "diagnostics": ["posterior_concentration_reported"],
        "scientific_basis": ["dirichlet_multinomial_conjugacy"],
    },
    {
        "method_id": "bayesian_normal_inverse_gamma",
        "family": "bayesian_conjugate",
        "title": {"ru": "Байесовская модель среднего и дисперсии", "en": "Bayesian mean and variance model", "es": "Modelo bayesiano de media y varianza"},
        "purpose": "posterior_for_normal_mean_and_variance",
        "compatible_scales": ["interval", "ratio", "continuous"],
        "required_inputs": ["values"],
        "optional_inputs": ["prior_mean", "prior_mean_strength", "prior_shape", "prior_scale", "credible_mass"],
        "diagnostics": ["posterior_predictive_interval", "normal_sampling_model_assumption"],
        "scientific_basis": ["normal_inverse_gamma_conjugacy", "student_t_posterior_predictive"],
    },
    {
        "method_id": "bootstrap_percentile",
        "family": "resampling",
        "title": {"ru": "Bootstrap-интервал", "en": "Bootstrap interval", "es": "Intervalo bootstrap"},
        "purpose": "resampling_uncertainty_for_supported_statistics",
        "compatible_scales": ["ordinal", "interval", "ratio", "continuous"],
        "required_inputs": ["values", "statistic"],
        "optional_inputs": ["second_values", "resamples", "interval_mass", "random_seed"],
        "diagnostics": ["valid_resample_count", "degenerate_resample_detection"],
        "scientific_basis": ["nonparametric_bootstrap", "percentile_interval"],
    },
    {
        "method_id": "permutation_difference_means",
        "family": "randomization_inference",
        "title": {"ru": "Перестановочный тест разности средних", "en": "Permutation test for difference in means", "es": "Prueba de permutación para diferencia de medias"},
        "purpose": "randomization_test_for_two_groups",
        "compatible_scales": ["interval", "ratio", "continuous"],
        "required_inputs": ["left_values", "right_values"],
        "optional_inputs": ["alternative", "permutations", "random_seed"],
        "diagnostics": ["exact_or_monte_carlo_status", "exchangeability_assumption"],
        "scientific_basis": ["permutation_randomization_inference"],
    },
    {
        "method_id": "bayesian_markov_transition",
        "family": "stochastic_process",
        "title": {"ru": "Байесовская модель марковских переходов", "en": "Bayesian Markov transition model", "es": "Modelo bayesiano de transiciones de Markov"},
        "purpose": "posterior_transition_probabilities",
        "compatible_scales": ["state", "nominal", "event_sequence"],
        "required_inputs": ["states", "sequences"],
        "optional_inputs": ["prior_concentration", "credible_mass"],
        "diagnostics": ["row_observation_counts", "first_order_and_time_homogeneity_assumptions"],
        "scientific_basis": ["dirichlet_transition_row_posterior"],
    },
    {
        "method_id": "monte_carlo_uncertainty_propagation",
        "family": "simulation",
        "title": {"ru": "Монте-Карло: распространение неопределённости", "en": "Monte Carlo uncertainty propagation", "es": "Monte Carlo: propagación de incertidumbre"},
        "purpose": "propagate_input_distributions_through_supported_operations",
        "compatible_scales": ["probability", "distribution", "interval", "ratio", "continuous"],
        "required_inputs": ["inputs", "operation"],
        "optional_inputs": ["weights", "samples", "interval_mass", "random_seed"],
        "diagnostics": ["rejected_draw_count", "seed_recorded", "input_output_sensitivity"],
        "scientific_basis": ["monte_carlo_uncertainty_propagation"],
    },
    {
        "method_id": "bayesian_linear_regression",
        "family": "bayesian_regression",
        "title": {"ru": "Байесовская линейная регрессия", "en": "Bayesian linear regression", "es": "Regresión lineal bayesiana"},
        "purpose": "conditional_continuous_outcome_model",
        "execution_status": "registered_without_validated_runner",
        "blocked_reason": "VALIDATED_MATRIX_RUNNER_AND_DIAGNOSTICS_REQUIRED",
    },
    {
        "method_id": "bayesian_logistic_regression",
        "family": "bayesian_regression",
        "title": {"ru": "Байесовская логистическая регрессия", "en": "Bayesian logistic regression", "es": "Regresión logística bayesiana"},
        "purpose": "conditional_binary_outcome_model",
        "execution_status": "registered_without_validated_runner",
        "blocked_reason": "POSTERIOR_SAMPLER_AND_CONVERGENCE_DIAGNOSTICS_REQUIRED",
    },
    {
        "method_id": "bayesian_poisson_regression",
        "family": "bayesian_regression",
        "title": {"ru": "Байесовская пуассоновская регрессия", "en": "Bayesian Poisson regression", "es": "Regresión de Poisson bayesiana"},
        "purpose": "conditional_count_outcome_model",
        "execution_status": "registered_without_validated_runner",
        "blocked_reason": "POSTERIOR_SAMPLER_OVERDISPERSION_AND_ZERO_INFLATION_DIAGNOSTICS_REQUIRED",
    },
    {
        "method_id": "hierarchical_bayesian_model",
        "family": "hierarchical",
        "title": {"ru": "Иерархическая байесовская модель", "en": "Hierarchical Bayesian model", "es": "Modelo bayesiano jerárquico"},
        "purpose": "multilevel_partial_pooling",
        "execution_status": "registered_without_validated_runner",
        "blocked_reason": "MULTILEVEL_POSTERIOR_SAMPLER_AND_DIAGNOSTICS_REQUIRED",
    },
    {
        "method_id": "bayesian_state_space_model",
        "family": "state_space",
        "title": {"ru": "Байесовская модель пространства состояний", "en": "Bayesian state-space model", "es": "Modelo bayesiano de espacio de estados"},
        "purpose": "latent_dynamic_state_estimation",
        "execution_status": "registered_without_validated_runner",
        "blocked_reason": "FILTER_SMOOTHER_AND_IDENTIFIABILITY_DIAGNOSTICS_REQUIRED",
    },
    {
        "method_id": "bayesian_survival_model",
        "family": "time_to_event",
        "title": {"ru": "Байесовская модель времени до события", "en": "Bayesian time-to-event model", "es": "Modelo bayesiano de tiempo hasta evento"},
        "purpose": "censored_time_to_event_inference",
        "execution_status": "registered_without_validated_runner",
        "blocked_reason": "CENSORING_AWARE_POSTERIOR_RUNNER_AND_DIAGNOSTICS_REQUIRED",
    },
]


EXECUTABLE_PROBABILISTIC_METHOD_IDS = {
    "bayesian_beta_binomial",
    "bayesian_dirichlet_multinomial",
    "bayesian_normal_inverse_gamma",
    "bootstrap_percentile",
    "permutation_difference_means",
    "bayesian_markov_transition",
    "monte_carlo_uncertainty_propagation",
}

for method in METHODS:
    method.setdefault(
        "execution_status",
        "implemented" if method["method_id"] in EXECUTABLE_PROBABILISTIC_METHOD_IDS else "registered_without_validated_runner",
    )


def list_probabilistic_methods(language: str = "ru") -> dict:
    if language not in {"ru", "en", "es"}:
        raise ValueError("UNSUPPORTED_LANGUAGE")
    methods = deepcopy(METHODS)
    for method in methods:
        title = method.get("title")
        if isinstance(title, dict):
            method["title"] = title[language]
    return {
        "registry_version": PROBABILISTIC_METHOD_REGISTRY_VERSION,
        "language": language,
        "methods": methods,
        "execution_policy": "only_methods_with_validated_runner_are_executable",
        "external_statistical_software_required": False,
    }
