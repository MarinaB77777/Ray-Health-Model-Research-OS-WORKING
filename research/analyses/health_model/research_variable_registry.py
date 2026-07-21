from research.analyses.health_model.function_registry import (
    list_functions,
)
from research.analyses.health_model.mechanism_registry import (
    list_mechanisms,
)
from research.analyses.health_model.constellation_registry import (
    list_constellations,
)


RESEARCH_VARIABLE_REGISTRY_SCHEMA_VERSION = (
    "health-model-research-variable-registry-1"
)


def _function_to_research_variable(function: dict) -> dict:
    return {
        "id": f"function:{function['id']}",
        "source_id": function["id"],
        "type": "function",
        "title": function["id"],
        "category": function.get("category"),
        "domains": function.get("domains", []),
        "used_by": function.get("used_by", []),
        "value_type": "registry_entity",
        "scale_type": None,
        "calculation_status": "registry_only",
        "schema_version": RESEARCH_VARIABLE_REGISTRY_SCHEMA_VERSION,
    }


def _mechanism_to_research_variable(mechanism: dict) -> dict:
    return {
        "id": f"mechanism:{mechanism['id']}",
        "source_id": mechanism["id"],
        "type": "mechanism",
        "title": mechanism.get("title") or mechanism["id"],
        "category": mechanism.get("type"),
        "required_functions": mechanism.get("required_functions", []),
        "supporting_functions": mechanism.get("supporting_functions", []),
        "trajectory_contributes_to": mechanism.get(
            "trajectory_contributes_to",
            [],
        ),
        "value_type": "registry_entity",
        "scale_type": None,
        "calculation_status": "registry_only",
        "schema_version": RESEARCH_VARIABLE_REGISTRY_SCHEMA_VERSION,
    }


def _constellation_to_research_variable(constellation: dict) -> dict:
    return {
        "id": f"constellation:{constellation['id']}",
        "source_id": constellation["id"],
        "type": "constellation",
        "title": constellation.get("title") or constellation["id"],
        "category": constellation.get("type"),
        "required_mechanisms": constellation.get("required_mechanisms", []),
        "optional_amplifiers": constellation.get("optional_amplifiers", []),
        "protective_signals": constellation.get("protective_signals", []),
        "priority": constellation.get("priority"),
        "status": constellation.get("status"),
        "value_type": "registry_entity",
        "scale_type": None,
        "calculation_status": "registry_only",
        "schema_version": RESEARCH_VARIABLE_REGISTRY_SCHEMA_VERSION,
    }


def list_health_model_research_variables() -> list[dict]:
    variables = []

    variables.extend(
        _function_to_research_variable(function)
        for function in list_functions()
    )

    variables.extend(
        _mechanism_to_research_variable(mechanism)
        for mechanism in list_mechanisms()
    )

    variables.extend(
        _constellation_to_research_variable(constellation)
        for constellation in list_constellations()
    )

    return variables