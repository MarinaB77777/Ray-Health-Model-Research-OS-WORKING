from __future__ import annotations

from math import sqrt

from .numerics import beta_quantile, mean, sample_variance, student_t_quantile


def _credible_tail(mass: float) -> float:
    if not 0.5 < mass < 1.0:
        raise ValueError("CREDIBLE_MASS_MUST_BE_BETWEEN_0_5_AND_1")
    return (1.0 - mass) / 2.0


def beta_binomial(payload: dict) -> dict:
    successes = int(payload.get("successes", -1))
    trials = int(payload.get("trials", -1))
    alpha = float(payload.get("prior_alpha", 1.0))
    beta = float(payload.get("prior_beta", 1.0))
    mass = float(payload.get("credible_mass", 0.95))
    if trials < 0 or successes < 0 or successes > trials:
        raise ValueError("BINOMIAL_COUNTS_INVALID")
    if alpha <= 0 or beta <= 0:
        raise ValueError("BETA_PRIOR_SHAPES_MUST_BE_POSITIVE")
    tail = _credible_tail(mass)
    posterior_alpha = alpha + successes
    posterior_beta = beta + trials - successes
    total = posterior_alpha + posterior_beta
    return {
        "posterior": {"distribution": "beta", "alpha": posterior_alpha, "beta": posterior_beta},
        "estimate": posterior_alpha / total,
        "posterior_variance": posterior_alpha * posterior_beta / (total * total * (total + 1.0)),
        "credible_interval": {
            "mass": mass,
            "lower": beta_quantile(tail, posterior_alpha, posterior_beta),
            "upper": beta_quantile(1.0 - tail, posterior_alpha, posterior_beta),
        },
        "posterior_predictive_probability_next_success": posterior_alpha / total,
    }


def dirichlet_multinomial(payload: dict) -> dict:
    raw_counts = payload.get("counts")
    if not isinstance(raw_counts, list) or len(raw_counts) < 2:
        raise ValueError("CATEGORY_COUNTS_REQUIRED")
    counts = [int(value) for value in raw_counts]
    if any(value < 0 for value in counts):
        raise ValueError("CATEGORY_COUNTS_MUST_BE_NONNEGATIVE")
    raw_prior = payload.get("prior_concentration")
    prior = [1.0] * len(counts) if raw_prior is None else [float(value) for value in raw_prior]
    if len(prior) != len(counts) or any(value <= 0 for value in prior):
        raise ValueError("DIRICHLET_PRIOR_INVALID")
    mass = float(payload.get("credible_mass", 0.95))
    tail = _credible_tail(mass)
    posterior = [a + n for a, n in zip(prior, counts)]
    total = sum(posterior)
    categories = []
    for index, alpha in enumerate(posterior):
        other = total - alpha
        categories.append({
            "category_index": index,
            "posterior_concentration": alpha,
            "estimate": alpha / total,
            "posterior_variance": alpha * other / (total * total * (total + 1.0)),
            "credible_interval": {
                "mass": mass,
                "lower": beta_quantile(tail, alpha, other),
                "upper": beta_quantile(1.0 - tail, alpha, other),
            },
        })
    return {
        "posterior": {"distribution": "dirichlet", "concentration": posterior},
        "categories": categories,
        "posterior_predictive_probabilities": [value / total for value in posterior],
    }


def normal_inverse_gamma(payload: dict) -> dict:
    raw = payload.get("values")
    if not isinstance(raw, list) or len(raw) < 2:
        raise ValueError("NORMAL_MODEL_REQUIRES_AT_LEAST_TWO_VALUES")
    values = [float(value) for value in raw]
    mu0 = float(payload.get("prior_mean", 0.0))
    kappa0 = float(payload.get("prior_mean_strength", 1e-6))
    alpha0 = float(payload.get("prior_shape", 1e-6))
    beta0 = float(payload.get("prior_scale", 1e-6))
    mass = float(payload.get("credible_mass", 0.95))
    if min(kappa0, alpha0, beta0) <= 0:
        raise ValueError("NORMAL_INVERSE_GAMMA_PRIOR_MUST_BE_POSITIVE")
    tail = _credible_tail(mass)
    n = len(values)
    sample_mean = mean(values)
    centered_sum = sample_variance(values) * (n - 1)
    kappa_n = kappa0 + n
    mu_n = (kappa0 * mu0 + n * sample_mean) / kappa_n
    alpha_n = alpha0 + n / 2.0
    beta_n = beta0 + 0.5 * centered_sum + (kappa0 * n * (sample_mean - mu0) ** 2) / (2.0 * kappa_n)
    degrees = 2.0 * alpha_n
    mean_scale = sqrt(beta_n / (alpha_n * kappa_n))
    predictive_scale = sqrt(beta_n * (kappa_n + 1.0) / (alpha_n * kappa_n))
    t_lower = student_t_quantile(tail, degrees)
    t_upper = student_t_quantile(1.0 - tail, degrees)
    return {
        "posterior": {
            "distribution": "normal_inverse_gamma",
            "mean": mu_n,
            "mean_strength": kappa_n,
            "shape": alpha_n,
            "scale": beta_n,
        },
        "estimate": mu_n,
        "credible_interval_mean": {
            "mass": mass,
            "lower": mu_n + t_lower * mean_scale,
            "upper": mu_n + t_upper * mean_scale,
        },
        "posterior_predictive": {
            "distribution": "student_t",
            "degrees_of_freedom": degrees,
            "location": mu_n,
            "scale": predictive_scale,
            "interval": {
                "mass": mass,
                "lower": mu_n + t_lower * predictive_scale,
                "upper": mu_n + t_upper * predictive_scale,
            },
        },
    }
