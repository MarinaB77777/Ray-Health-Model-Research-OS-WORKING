from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from research.sensor_hypothesis import build_sensor_validation_plan, sensor_hypothesis_contract
from research.qualitative_hypothesis import (
    build_qualitative_hypothesis_plan,
    qualitative_hypothesis_contract,
)


HYPOTHESIS_SCHEMA_VERSION = "health-model-hypothesis-definition-3"
HYPOTHESIS_MODES = {
    "humanities_qualitative": "Humanities / qualitative hypothesis",
    "technical_quantitative": "Technical / quantitative hypothesis",
}
BASIS_TYPES = {
    "scientific_source": "Scientific source",
    "prior_result": "Prior research result",
    "observation": "Observation",
    "theoretical_model": "Theoretical model",
    "existing_parameter": "Registered parameter",
    "existing_mechanism": "Registered mechanism",
    "questionnaire_data": "Questionnaire data",
    "sensor_measurement": "Sensor measurement",
    "game_measurement": "Game measurement",
    "qualitative_material": "Qualitative material",
    "researcher_reasoning": "Researcher reasoning",
    "ray_candidate": "Ray-generated candidate (not evidence)",
}
VARIABLE_ROLES = {
    "predictor": "Predictor / exposure",
    "outcome": "Outcome",
    "mediator": "Mediator",
    "moderator": "Moderator",
    "confounder": "Confounder / control",
    "grouping": "Grouping variable",
    "time": "Time variable",
}
RELATIONSHIPS = {
    "association": "Association",
    "directional_effect": "Directional effect",
    "group_difference": "Group difference",
    "temporal_precedence": "Temporal precedence",
    "mediation": "Mediation",
    "moderation": "Moderation",
    "equivalence": "Equivalence / non-inferiority",
}
DIRECTIONS = ["positive", "negative", "increase", "decrease", "difference", "non_monotonic", "unspecified"]
MODEL_FAMILIES = {
    "unspecified": "Not selected",
    "linear_additive": "Linear additive dependence",
    "generalized_linear": "Generalized linear dependence",
    "nonlinear": "Nonlinear dependence",
    "interaction": "Dependence with interactions",
    "lagged": "Lagged dependence",
    "longitudinal_mixed": "Longitudinal mixed-effects model",
    "time_series": "Time-series dependence",
    "survival_event": "Time-to-event dependence",
}


def hypothesis_contract() -> dict[str, Any]:
    return {
        "schema_version": HYPOTHESIS_SCHEMA_VERSION,
        "hypothesis_modes": HYPOTHESIS_MODES,
        "basis_types": BASIS_TYPES,
        "variable_roles": VARIABLE_ROLES,
        "relationship_types": RELATIONSHIPS,
        "directions": DIRECTIONS,
        "model_families": MODEL_FAMILIES,
        "time_contract": {"axis": "UTC", "required_for_observations": True, "display_timezone_is_not_storage_timezone": True},
        "status_rules": {
            "draft": ["title"],
            "trial": ["title", "formal_statement", "basis_items", "outcome", "falsification_criteria"],
            "active": ["title", "formal_statement", "basis_items", "outcome", "falsification_criteria", "planned_analysis"],
        },
        "technical_contract": {
            "dependent_roles": ["outcome"],
            "independent_roles": ["predictor", "moderator", "confounder", "grouping"],
            "time_role": "time",
            "multiple_predictors_allowed": True,
            "multiple_outcomes_allowed": True,
            "canonical_form": "Y = f(X1, ..., Xn, t | controls) + error",
        },
        "sensor_validation_contract": sensor_hypothesis_contract(),
        "qualitative_inquiry_contract": qualitative_hypothesis_contract(),
        "invariants": ["hypothesis_is_not_fact", "ray_candidate_is_not_evidence", "unknown_is_not_zero", "registered_entity_version_is_preserved", "technical_dependency_requires_outcome_and_predictor", "time_measurements_use_utc"],
    }


def build_hypothesis_definition(raw: dict[str, Any]) -> dict[str, Any]:
    mode = str(raw.get("hypothesis_mode") or "humanities_qualitative")
    if mode not in HYPOTHESIS_MODES:
        raise ValueError("HYPOTHESIS_MODE_UNSUPPORTED")
    status = str(raw.get("status") or "draft").lower()
    if status not in {"draft", "trial", "active"}:
        raise ValueError("HYPOTHESIS_STATUS_UNSUPPORTED")
    basis_items = []
    for item in raw.get("basis_items") or []:
        basis_type = str(item.get("type") or "")
        if basis_type not in BASIS_TYPES:
            raise ValueError("HYPOTHESIS_BASIS_TYPE_UNSUPPORTED")
        normalized = {
            "type": basis_type,
            "registered_ref": str(item.get("registered_ref") or "").strip(),
            "title": str(item.get("title") or "").strip(),
            "notes": str(item.get("notes") or "").strip(),
            "evidence_status": "candidate_not_evidence" if basis_type == "ray_candidate" else "researcher_supplied_basis",
        }
        if normalized["title"] or normalized["registered_ref"] or normalized["notes"]:
            basis_items.append(normalized)
    variables = []
    for item in raw.get("variables") or []:
        role = str(item.get("role") or "")
        if role not in VARIABLE_ROLES:
            raise ValueError("HYPOTHESIS_VARIABLE_ROLE_UNSUPPORTED")
        variable_direction = str(item.get("expected_direction") or "unspecified")
        if variable_direction not in DIRECTIONS:
            raise ValueError("HYPOTHESIS_VARIABLE_DIRECTION_UNSUPPORTED")
        variables.append({
            "role": role,
            "entity_ref": str(item.get("entity_ref") or "").strip(),
            "display_name": str(item.get("display_name") or "").strip(),
            "entity_type": str(item.get("entity_type") or "").strip(),
            "version": item.get("version"),
            "measurement_scale_ref": str(item.get("measurement_scale_ref") or "").strip(),
            "unit": str(item.get("unit") or "").strip(),
            "expected_direction": variable_direction,
            "transformation": str(item.get("transformation") or "identity").strip(),
            "lag": str(item.get("lag") or "").strip(),
            "time_contract": item.get("time_contract") or {},
        })
    relationship = str(raw.get("relationship_type") or "association")
    if relationship not in RELATIONSHIPS:
        raise ValueError("HYPOTHESIS_RELATIONSHIP_UNSUPPORTED")
    direction = str(raw.get("expected_direction") or "unspecified")
    if direction not in DIRECTIONS:
        raise ValueError("HYPOTHESIS_DIRECTION_UNSUPPORTED")
    model_family = str(raw.get("model_family") or "unspecified")
    if model_family not in MODEL_FAMILIES:
        raise ValueError("HYPOTHESIS_MODEL_FAMILY_UNSUPPORTED")
    time_axis_included = bool(raw.get("time_axis_included", mode == "technical_quantitative"))
    outcomes = [item["display_name"] or item["entity_ref"] for item in variables if item["role"] == "outcome"]
    predictors = [item["display_name"] or item["entity_ref"] for item in variables if item["role"] in {"predictor", "mediator", "moderator"}]
    controls = [item["display_name"] or item["entity_ref"] for item in variables if item["role"] in {"confounder", "grouping"}]
    times = [item["display_name"] or item["entity_ref"] for item in variables if item["role"] == "time"]
    # The shared UTC axis is infrastructure, not a user-authored scientific
    # object.  It participates in the model automatically when requested.
    if time_axis_included and not times:
        times = ["UTC time"]
    left = ", ".join(outcomes) or "Y"
    arguments = predictors + (times if time_axis_included else [])
    canonical_model = f"{left} = f({', '.join(arguments) or 'X'})"
    if controls:
        canonical_model += f" | controls: {', '.join(controls)}"
    canonical_model += " + error"
    sensor_raw = raw.get("sensor_validation") or {}
    sensor_plan = None
    if mode == "technical_quantitative" and sensor_raw.get("validation_aim") and sensor_raw.get("outcome_data_kind"):
        sensor_plan = build_sensor_validation_plan(sensor_raw)
    qualitative_raw = raw.get("qualitative_inquiry") or {}
    qualitative_plan = None
    if mode == "humanities_qualitative" and qualitative_raw.get("inquiry_mode"):
        qualitative_plan = build_qualitative_hypothesis_plan(qualitative_raw)
    definition = {
        "schema_version": HYPOTHESIS_SCHEMA_VERSION,
        "hypothesis_mode": mode,
        "status": status,
        "title": str(raw.get("title") or "").strip(),
        "basis_items": basis_items,
        "variables": variables,
        "relationship_type": relationship,
        "expected_direction": direction,
        "technical_model": {
            "model_family": model_family,
            "time_axis_included": time_axis_included,
            "canonical_model": canonical_model,
            "researcher_mathematical_form": str(raw.get("mathematical_form") or "").strip(),
            "outcome_count": len(outcomes),
            "predictor_count": len(predictors),
            "control_count": len(controls),
            "time_variable_count": len(times),
            "time_axis": "UTC" if time_axis_included else None,
        },
        "sensor_validation": sensor_plan or {
            "schema_version": sensor_hypothesis_contract()["schema_version"],
            "readiness": {"valid": False, "issues": ["SENSOR_VALIDATION_PLAN_NOT_CONFIGURED"]},
        },
        "qualitative_inquiry": qualitative_plan or {
            "schema_version": qualitative_hypothesis_contract()["schema_version"],
            "readiness": {"valid": False, "issues": ["QUALITATIVE_INQUIRY_PLAN_NOT_CONFIGURED"]},
        },
        "formal_statement": str(raw.get("formal_statement") or "").strip(),
        "null_hypothesis": str(raw.get("null_hypothesis") or "").strip(),
        "alternative_hypothesis": str(raw.get("alternative_hypothesis") or "").strip(),
        "population": str(raw.get("population") or "").strip(),
        "observation_unit": str(raw.get("observation_unit") or "").strip(),
        "conditions": str(raw.get("conditions") or "").strip(),
        "time_relation": str(raw.get("time_relation") or "").strip(),
        "falsification_criteria": str(raw.get("falsification_criteria") or "").strip(),
        "planned_analysis": list(raw.get("planned_analysis") or []),
        "analysis_compatibility_status": "not_checked_requires_data_and_method_assumption_review",
        "updated_at": datetime.now(UTC).isoformat(),
    }
    required = hypothesis_contract()["status_rules"][status]
    outcome = any(item["role"] == "outcome" for item in variables)
    missing = []
    for field in required:
        if field == "outcome" and mode == "humanities_qualitative":
            present = bool((definition.get("qualitative_inquiry") or {}).get("objects"))
        else:
            present = outcome if field == "outcome" else bool(definition.get(field))
        if not present:
            missing.append(field)
    if mode == "technical_quantitative" and status in {"trial", "active"}:
        if not predictors:
            missing.append("predictor")
        if model_family == "unspecified":
            missing.append("model_family")
        if time_axis_included and not definition["time_relation"]:
            missing.append("time_relation")
        if not definition["sensor_validation"]["readiness"]["valid"]:
            missing.extend(definition["sensor_validation"]["readiness"]["issues"])
    if mode == "humanities_qualitative" and status in {"trial", "active"}:
        if not definition["qualitative_inquiry"]["readiness"]["valid"]:
            missing.extend(definition["qualitative_inquiry"]["readiness"]["issues"])
    definition["readiness"] = {"valid_for_status": not missing, "missing": missing, "status": status}
    return definition
