FUNCTION_REGISTRY_SCHEMA_VERSION = "function-registry-1"


def _function(
    function_id: str,
    domains: list[str],
    used_by: list[str],
    category: str,
):
    return {
        "id": function_id,
        "domains": domains,
        "used_by": used_by,
        "category": category,
        "schema_version": FUNCTION_REGISTRY_SCHEMA_VERSION,
    }


FUNCTION_REGISTRY = {
    "goal_commitment": _function(
        "goal_commitment",
        ["goal"],
        ["decision_degradation", "commitment_trap", "learning_failure"],
        "goal_regulation",
    ),
    "goal_directed_behavior": _function(
        "goal_directed_behavior",
        ["goal", "psychological"],
        ["decision_degradation", "commitment_trap"],
        "goal_regulation",
    ),
    "prioritization": _function(
        "prioritization",
        ["goal"],
        ["decision_degradation", "option_space_collapse"],
        "goal_regulation",
    ),
    "goal_adjustment_capacity": _function(
        "goal_adjustment_capacity",
        ["goal"],
        ["commitment_trap", "learning_failure"],
        "goal_regulation",
    ),
    "value_consistent_behavior": _function(
        "value_consistent_behavior",
        ["goal"],
        ["commitment_trap"],
        "goal_regulation",
    ),

    "emotion_regulation": _function(
        "emotion_regulation",
        ["psychological"],
        ["decision_degradation", "recovery_mismatch"],
        "psychological_regulation",
    ),
    "distress_tolerance": _function(
        "distress_tolerance",
        ["psychological"],
        ["decision_degradation", "commitment_trap"],
        "psychological_regulation",
    ),
    "psychological_flexibility": _function(
        "psychological_flexibility",
        ["psychological"],
        ["decision_degradation", "learning_failure"],
        "psychological_regulation",
    ),
    "intolerance_of_uncertainty": _function(
        "intolerance_of_uncertainty",
        ["psychological"],
        ["option_space_collapse", "decision_degradation"],
        "uncertainty_processing",
    ),
    "feedback_utilization": _function(
        "feedback_utilization",
        ["psychological", "cognitive"],
        ["learning_failure", "decision_degradation"],
        "feedback_processing",
    ),

    "working_memory": _function(
        "working_memory",
        ["cognitive", "physical"],
        ["decision_degradation"],
        "cognitive_control",
    ),
    "cognitive_flexibility": _function(
        "cognitive_flexibility",
        ["cognitive"],
        ["decision_degradation", "learning_failure"],
        "cognitive_control",
    ),
    "executive_control": _function(
        "executive_control",
        ["cognitive", "physical"],
        ["decision_degradation", "dual_failure"],
        "cognitive_control",
    ),
    "belief_updating": _function(
        "belief_updating",
        ["cognitive"],
        ["learning_failure", "decision_degradation"],
        "cognitive_control",
    ),
    "error_monitoring": _function(
        "error_monitoring",
        ["cognitive", "physical"],
        ["learning_failure", "decision_degradation"],
        "feedback_processing",
    ),
    "metacognitive_monitoring": _function(
        "metacognitive_monitoring",
        ["cognitive"],
        ["decision_degradation", "learning_failure"],
        "cognitive_control",
    ),
    "strategy_switching": _function(
        "strategy_switching",
        ["cognitive"],
        ["learning_failure", "commitment_trap"],
        "adaptive_control",
    ),

    "risk_evaluation": _function(
        "risk_evaluation",
        ["physical", "social"],
        ["decision_degradation"],
        "decision_quality",
    ),
    "judgment": _function(
        "judgment",
        ["physical"],
        ["decision_degradation"],
        "decision_quality",
    ),
    "inhibitory_control": _function(
        "inhibitory_control",
        ["physical", "cognitive"],
        ["decision_degradation"],
        "cognitive_control",
    ),

    "perceived_agency": _function(
        "perceived_agency",
        ["social"],
        ["option_space_collapse", "control_gap"],
        "agency",
    ),
    "autonomous_regulation": _function(
        "autonomous_regulation",
        ["social"],
        ["option_space_collapse", "decision_degradation"],
        "agency",
    ),
    "independent_judgment": _function(
        "independent_judgment",
        ["social"],
        ["decision_degradation"],
        "decision_quality",
    ),
    "perceived_option_availability": _function(
        "perceived_option_availability",
        ["social"],
        ["option_space_collapse"],
        "option_space",
    ),
    "option_generation": _function(
        "option_generation",
        ["social"],
        ["option_space_collapse"],
        "option_space",
    ),

    "future_expectancy": _function(
        "future_expectancy",
        ["pep"],
        ["option_space_collapse"],
        "forecast_expectancy",
    ),
    "threat_appraisal": _function(
        "threat_appraisal",
        ["pep"],
        ["option_space_collapse", "decision_degradation"],
        "forecast_expectancy",
    ),
    "uncertainty_evaluation": _function(
        "uncertainty_evaluation",
        ["pep"],
        ["option_space_collapse"],
        "uncertainty_processing",
    ),
    "perceived_controllability": _function(
        "perceived_controllability",
        ["pep"],
        ["control_gap", "option_space_collapse"],
        "agency",
    ),

    "recovery_efficiency": _function(
        "recovery_efficiency",
        ["recovery"],
        ["recovery_mismatch", "resource_exhaustion"],
        "recovery",
    ),
    "restoration_capacity": _function(
        "restoration_capacity",
        ["recovery"],
        ["resource_exhaustion", "recovery_mismatch"],
        "recovery",
    ),
    "recovery_regulation": _function(
        "recovery_regulation",
        ["recovery"],
        ["resource_exhaustion"],
        "recovery",
    ),
    "resilience": _function(
        "resilience",
        ["recovery"],
        ["resource_exhaustion", "recovery_mismatch"],
        "recovery",
    ),
}


def get_function(function_id: str) -> dict | None:
    return FUNCTION_REGISTRY.get(function_id)


def list_functions() -> list[dict]:
    return list(FUNCTION_REGISTRY.values())


def resolve_functions(function_ids: list[str]) -> list[dict]:
    resolved = []

    for function_id in function_ids:
        function = get_function(function_id)

        if function is not None:
            resolved.append(function)

    return resolved