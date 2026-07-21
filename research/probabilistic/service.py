from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable
from uuid import uuid4

from .bayesian_conjugate import beta_binomial, dirichlet_multinomial, normal_inverse_gamma
from .markov import markov_dirichlet
from .monte_carlo import propagate_uncertainty
from .registry import EXECUTABLE_PROBABILISTIC_METHOD_IDS, METHODS, PROBABILISTIC_METHOD_REGISTRY_VERSION
from .resampling import bootstrap, permutation_two_sample


PROBABILISTIC_RESULT_SCHEMA_VERSION = "probabilistic-analysis-result-1"


class ProbabilisticMethodError(Exception):
    def __init__(self, code: str, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


RUNNERS: dict[str, Callable[[dict], dict]] = {
    "bayesian_beta_binomial": beta_binomial,
    "bayesian_dirichlet_multinomial": dirichlet_multinomial,
    "bayesian_normal_inverse_gamma": normal_inverse_gamma,
    "bootstrap_percentile": bootstrap,
    "permutation_difference_means": permutation_two_sample,
    "bayesian_markov_transition": markov_dirichlet,
    "monte_carlo_uncertainty_propagation": propagate_uncertainty,
}


def run_probabilistic_method(
    *,
    method_id: str,
    payload: dict,
    actor_account_id: str,
    project_id: str | None = None,
    block_id: str | None = None,
) -> dict:
    method = next((item for item in METHODS if item["method_id"] == method_id), None)
    if method is None:
        raise ProbabilisticMethodError("PROBABILISTIC_METHOD_NOT_FOUND", 404)
    if method_id not in EXECUTABLE_PROBABILISTIC_METHOD_IDS or method_id not in RUNNERS:
        raise ProbabilisticMethodError(
            "PROBABILISTIC_METHOD_NOT_EXECUTABLE:" + str(method.get("blocked_reason") or "VALIDATED_RUNNER_REQUIRED"),
            409,
        )
    if not isinstance(payload, dict):
        raise ProbabilisticMethodError("PROBABILISTIC_METHOD_PAYLOAD_MUST_BE_OBJECT")
    started_at = datetime.now(UTC)
    try:
        result = RUNNERS[method_id](payload)
    except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
        raise ProbabilisticMethodError(f"PROBABILISTIC_METHOD_INPUT_INVALID:{exc}") from exc
    finished_at = datetime.now(UTC)
    return {
        "schema_version": PROBABILISTIC_RESULT_SCHEMA_VERSION,
        "analysis_id": str(uuid4()),
        "method_id": method_id,
        "method_family": method["family"],
        "execution_status": "completed",
        "result": result,
        "validation": {
            "runner_registered": True,
            "input_shape_validated": True,
            "measurement_scale_binding": "method_specific_manual_input_contract",
            "warnings": [
                "manual_values_are_not_yet_bound_to_a_registered_project_dataset"
            ] if project_id is None else [],
        },
        "context": {"project_id": project_id, "block_id": block_id},
        "authorship": {"executed_by_account_id": actor_account_id},
        "time_reference": {
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "global_time_reference": "UTC",
            "clock_source": "server_utc",
        },
        "provenance": {
            "registry_version": PROBABILISTIC_METHOD_REGISTRY_VERSION,
            "runner": RUNNERS[method_id].__module__ + "." + RUNNERS[method_id].__name__,
            "input_snapshot": payload,
            "external_statistical_software_used": False,
        },
    }
