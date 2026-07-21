import json
from copy import deepcopy
from pathlib import Path
from uuid import UUID, uuid5

from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
)
from research.analyses.health_model.parameter_calculation_registry import (
    CALCULATION_OPERATIONS,
    validate_calculation_selection,
)
from research.analyses.health_model.observable_marker_registry import (
    AUTHORSHIP_ROLES,
    MARKER_ROLES,
)


MECHANISM_REGISTRY_SCHEMA_VERSION = "mechanism-registry-2"
MECHANISM_DEFINITION_SCHEMA_VERSION = "mechanism-definition-1"
MECHANISM_NAMESPACE = UUID("dfda90c1-916b-4dd4-8458-83163f94ce74")
CUSTOM_MECHANISM_DEFINITIONS_PATH = Path("data/mechanism_definitions.json")
SUPPORTED_DEVELOPMENT_STATUSES = {"draft", "trial", "active"}
SUPPORTED_CALCULATION_OPERATORS = set(CALCULATION_OPERATIONS)

_TITLE_RU = {
    "option_space_collapse": "Схлопывание пространства вариантов",
    "decision_degradation": "Деградация принятия решений",
    "resource_exhaustion": "Истощение ресурсов",
    "recovery_mismatch": "Несоответствие восстановления нагрузке",
    "learning_failure": "Нарушение обучения на обратной связи",
    "commitment_trap": "Ловушка приверженности",
    "dual_failure": "Двойной функциональный сбой",
}

_TITLE_ES = {
    "option_space_collapse": "Colapso del espacio de opciones",
    "decision_degradation": "Degradación de la toma de decisiones",
    "resource_exhaustion": "Agotamiento de recursos",
    "recovery_mismatch": "Desajuste de la recuperación",
    "learning_failure": "Fallo del aprendizaje por retroalimentación",
    "commitment_trap": "Trampa de compromiso",
    "dual_failure": "Fallo funcional dual",
}


def _mechanism(
    mechanism_id: str,
    title: str,
    mechanism_type: str,
    required_functions: list[str],
    supporting_functions: list[str],
    minimum_required: int,
    first_measurement_allowed_statuses: list[str],
    confirmed_requires_repeated_measurement: bool,
    trajectory_contributes_to: list[str],
):
    return {
        "id": mechanism_id,
        "mechanism_id": str(uuid5(MECHANISM_NAMESPACE, mechanism_id)),
        "mechanism_code": mechanism_id,
        "definition_version": 1,
        "definition_source": "built_in",
        "development_status": "active",
        "lifecycle_status": "active",
        # Legacy string stays intact for existing reports and variable catalogues.
        "title": title,
        "title_i18n": {
            "ru": _TITLE_RU[mechanism_id],
            "en": title,
            "es": _TITLE_ES[mechanism_id],
        },
        "type": mechanism_type,
        "required_functions": required_functions,
        "supporting_functions": supporting_functions,
        "minimum_required": minimum_required,
        "first_measurement_allowed_statuses": first_measurement_allowed_statuses,
        "confirmed_requires_repeated_measurement": confirmed_requires_repeated_measurement,
        "trajectory_contributes_to": trajectory_contributes_to,
        "schema_version": MECHANISM_REGISTRY_SCHEMA_VERSION,
        "definition_schema_version": MECHANISM_DEFINITION_SCHEMA_VERSION,
        "input_contract": {
            "required_parameter_codes": [],
            "optional_parameter_codes": [],
            "required_mechanism_codes": [],
            "optional_mechanism_codes": [],
            "required_function_codes": required_functions,
            "supporting_function_codes": supporting_functions,
            "minimum_required_inputs": minimum_required,
        },
        "output_scale": {
            "scale_type": "model_index",
            "scale_reference": build_scale_reference("model_index"),
            "minimum": 0,
            "maximum": 5,
            "value_type": "float",
            "evidence_state_scale": "ordinal",
            "ordered_evidence_states": [
                "NOT_ENOUGH_DATA", "SUSPECTED", "LIKELY", "CONFIRMED"
            ],
        },
        "temporal_design": {
            "time_dependent": confirmed_requires_repeated_measurement,
            "temporal_form": "trajectory" if confirmed_requires_repeated_measurement else "state",
            "observation_time_required": True,
            "global_time_reference_required": True,
            "minimum_observation_count": 2 if confirmed_requires_repeated_measurement else 1,
            "ordering_required": confirmed_requires_repeated_measurement,
            "aggregation": "sequence_pattern" if confirmed_requires_repeated_measurement else "single_observation",
            "time_window": {"type": None, "value": None, "unit": None},
            "global_time_scale": {
                "scale_type": "datetime",
                "scale_reference": build_scale_reference("datetime"),
                "role": "global_time_reference",
                "timezone_required": True,
                "synchronization_reference_required": True,
            },
            "time_scale": {
                "scale_type": "datetime",
                "scale_reference": build_scale_reference("datetime"),
            },
            "missing_time_semantics": "not_enough_data",
        },
        "calculation_design": {
            "operator": "registered_calculator",
            "registered_calculator": "mechanism_layer",
            "components": [],
            "unknown_is_zero": False,
        },
        "feedback": {
            "status": "not_evaluated",
            "human_review_required": True,
            "evidence_result_ids": [],
        },
        "provenance": {
            "creation_mode": "human_ai_collaboration",
            "human_lead": "Marina Boronenko",
            "ai_colleague": "Ray",
        },
    }


MECHANISM_REGISTRY = {
    "option_space_collapse": _mechanism(
        mechanism_id="option_space_collapse",
        title="OptionSpaceCollapse",
        mechanism_type="latent_trajectory_mechanism",
        required_functions=[
            "perceived_option_availability",
            "option_generation",
            "perceived_agency",
            "future_expectancy",
            "perceived_controllability",
        ],
        supporting_functions=[
            "prioritization",
            "intolerance_of_uncertainty",
            "threat_appraisal",
            "uncertainty_evaluation",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "trajectory_risk",
            "decision_degradation",
            "reserve_discovery_failure",
            "future_path_restriction",
        ],
    ),

    "decision_degradation": _mechanism(
        mechanism_id="decision_degradation",
        title="DecisionDegradation",
        mechanism_type="latent_functional_mechanism",
        required_functions=[
            "working_memory",
            "executive_control",
            "belief_updating",
            "feedback_utilization",
            "cognitive_flexibility",
        ],
        supporting_functions=[
            "judgment",
            "risk_evaluation",
            "emotion_regulation",
            "distress_tolerance",
            "inhibitory_control",
            "metacognitive_monitoring",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "dual_failure",
            "learning_failure",
            "trajectory_risk",
        ],
    ),

    "resource_exhaustion": _mechanism(
        mechanism_id="resource_exhaustion",
        title="ResourceExhaustion",
        mechanism_type="latent_depletion_mechanism",
        required_functions=[
            "recovery_efficiency",
            "restoration_capacity",
            "recovery_regulation",
            "resilience",
        ],
        supporting_functions=[
            "working_memory",
            "executive_control",
            "emotion_regulation",
            "goal_commitment",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "dual_failure",
            "trajectory_risk",
            "recovery_mismatch",
        ],
    ),

    "recovery_mismatch": _mechanism(
        mechanism_id="recovery_mismatch",
        title="RecoveryMismatch",
        mechanism_type="latent_recovery_mechanism",
        required_functions=[
            "recovery_efficiency",
            "restoration_capacity",
            "resilience",
        ],
        supporting_functions=[
            "emotion_regulation",
            "feedback_utilization",
            "working_memory",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "resource_exhaustion",
            "trajectory_risk",
        ],
    ),

    "learning_failure": _mechanism(
        mechanism_id="learning_failure",
        title="LearningFailure",
        mechanism_type="latent_learning_mechanism",
        required_functions=[
            "feedback_utilization",
            "belief_updating",
            "error_monitoring",
            "strategy_switching",
        ],
        supporting_functions=[
            "goal_adjustment_capacity",
            "psychological_flexibility",
            "cognitive_flexibility",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "decision_degradation",
            "commitment_trap",
            "trajectory_risk",
        ],
    ),

    "commitment_trap": _mechanism(
        mechanism_id="commitment_trap",
        title="CommitmentTrap",
        mechanism_type="latent_commitment_mechanism",
        required_functions=[
            "goal_commitment",
            "goal_adjustment_capacity",
            "strategy_switching",
            "value_consistent_behavior",
        ],
        supporting_functions=[
            "distress_tolerance",
            "goal_directed_behavior",
            "psychological_flexibility",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "learning_failure",
            "trajectory_risk",
        ],
    ),

    "dual_failure": _mechanism(
        mechanism_id="dual_failure",
        title="DualFailure",
        mechanism_type="composite_trajectory_mechanism",
        required_functions=[],
        supporting_functions=[],
        minimum_required=0,
        first_measurement_allowed_statuses=[
            "NOT_ENOUGH_DATA",
            "SUSPECTED",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "high_risk_trajectory",
        ],
    ),
}


def _mechanism_code(value) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _version(definition: dict) -> int:
    try:
        return int(definition.get("definition_version", 1))
    except (TypeError, ValueError):
        return 1


def _multilingual(value=None) -> dict:
    if isinstance(value, dict):
        return {language: str(value.get(language) or "") for language in ("ru", "en", "es")}
    text = str(value or "")
    return {"ru": text, "en": text, "es": text}


def _load_custom_raw() -> list[dict]:
    if not CUSTOM_MECHANISM_DEFINITIONS_PATH.exists():
        return []
    payload = json.loads(CUSTOM_MECHANISM_DEFINITIONS_PATH.read_text(encoding="utf-8"))
    definitions = payload if isinstance(payload, list) else payload.get("definitions", [])
    if not isinstance(definitions, list):
        raise ValueError("Mechanism definition store must contain a definitions list")
    return [item for item in definitions if isinstance(item, dict)]


def _save_custom_raw(definitions: list[dict]) -> None:
    CUSTOM_MECHANISM_DEFINITIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = CUSTOM_MECHANISM_DEFINITIONS_PATH.with_suffix(
        CUSTOM_MECHANISM_DEFINITIONS_PATH.suffix + ".tmp"
    )
    temporary_path.write_text(
        json.dumps(
            {
                "schema_version": MECHANISM_REGISTRY_SCHEMA_VERSION,
                "definitions": definitions,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    temporary_path.replace(CUSTOM_MECHANISM_DEFINITIONS_PATH)


def normalize_mechanism_definition(
    definition: dict,
    *,
    definition_source: str = "constructor",
) -> dict:
    normalized = deepcopy(definition)
    code = _mechanism_code(
        normalized.get("mechanism_code") or normalized.get("id")
    )
    normalized["id"] = code
    normalized["mechanism_code"] = code
    normalized["mechanism_id"] = str(uuid5(MECHANISM_NAMESPACE, code))
    normalized["schema_version"] = MECHANISM_REGISTRY_SCHEMA_VERSION
    normalized["definition_schema_version"] = MECHANISM_DEFINITION_SCHEMA_VERSION
    normalized["definition_source"] = definition_source
    normalized["definition_version"] = _version(normalized)
    development_status = str(normalized.get("development_status") or "draft").lower()
    normalized["development_status"] = development_status
    normalized["lifecycle_status"] = "draft" if development_status == "draft" else "active"

    title_i18n = normalized.get("title_i18n")
    if title_i18n is None:
        title_i18n = normalized.get("title")
    normalized["title_i18n"] = _multilingual(title_i18n)
    normalized["title"] = (
        normalized["title_i18n"].get("en")
        or normalized["title_i18n"].get("ru")
        or normalized["title_i18n"].get("es")
        or code
    )
    normalized["type"] = str(normalized.get("type") or "research_mechanism")

    meaning = normalized.get("meaning") if isinstance(normalized.get("meaning"), dict) else {}
    meaning["construct_definition"] = _multilingual(
        meaning.get("construct_definition") or normalized.get("measurement_meaning")
    )
    meaning["activation_conditions"] = list(meaning.get("activation_conditions") or [])
    meaning["change_indicators"] = list(meaning.get("change_indicators") or [])
    normalized["meaning"] = meaning

    inputs = normalized.get("input_contract") if isinstance(normalized.get("input_contract"), dict) else {}
    inputs.setdefault("required_parameter_codes", [])
    inputs.setdefault("optional_parameter_codes", [])
    inputs.setdefault("required_mechanism_codes", [])
    inputs.setdefault("optional_mechanism_codes", [])
    inputs.setdefault("required_function_codes", list(normalized.get("required_functions") or []))
    inputs.setdefault("supporting_function_codes", list(normalized.get("supporting_functions") or []))
    inputs.setdefault("minimum_required_inputs", normalized.get("minimum_required", 0))
    normalized["input_contract"] = inputs
    normalized["required_functions"] = list(inputs["required_function_codes"])
    normalized["supporting_functions"] = list(inputs["supporting_function_codes"])
    normalized["minimum_required"] = int(inputs.get("minimum_required_inputs") or 0)

    output = normalized.get("output_scale") if isinstance(normalized.get("output_scale"), dict) else {}
    scale_type = output.get("scale_type") or normalized.get("scale_type")
    if scale_type is None and definition_source != "constructor":
        scale_type = "model_index"
    output["scale_type"] = scale_type
    output["scale_reference"] = (
        build_scale_reference(scale_type) if scale_type else None
    )
    output["binding_status"] = (
        "registered" if output["scale_reference"] is not None else "unbound"
    )
    output.setdefault("minimum", None)
    output.setdefault("maximum", None)
    output.setdefault("value_type", "float")
    normalized["output_scale"] = output

    temporal = normalized.get("temporal_design") if isinstance(normalized.get("temporal_design"), dict) else {}
    temporal.setdefault("time_dependent", True)
    temporal.setdefault("temporal_form", "trajectory")
    temporal["observation_time_required"] = True
    temporal["global_time_reference_required"] = True
    temporal.setdefault("minimum_observation_count", 2 if temporal["time_dependent"] else 1)
    temporal.setdefault("ordering_required", bool(temporal["time_dependent"]))
    temporal.setdefault("aggregation", "sequence_pattern" if temporal["time_dependent"] else "single_observation")
    temporal.setdefault("time_window", {"type": None, "value": None, "unit": None})
    temporal["global_time_scale"] = {
        "scale_type": "datetime",
        "scale_reference": build_scale_reference("datetime"),
        "role": "global_time_reference",
        "timezone_required": True,
        "synchronization_reference_required": True,
    }
    time_scale = temporal.get("time_scale") if isinstance(temporal.get("time_scale"), dict) else {}
    time_scale_code = time_scale.get("scale_type")
    if time_scale_code is None and definition_source != "constructor":
        time_scale_code = "datetime"
    time_scale["scale_type"] = time_scale_code
    time_scale["scale_reference"] = (
        build_scale_reference(time_scale_code) if time_scale_code else None
    )
    time_scale["binding_status"] = (
        "registered" if time_scale["scale_reference"] is not None else "unbound"
    )
    temporal["time_scale"] = time_scale
    temporal.setdefault("missing_time_semantics", "not_enough_data")
    normalized["temporal_design"] = temporal

    calculation = normalized.get("calculation_design") if isinstance(normalized.get("calculation_design"), dict) else {}
    calculation.setdefault("operator", "mean")
    calculation.setdefault("components", [])
    calculation.setdefault("weights", [])
    calculation["unknown_is_zero"] = False
    normalized["calculation_design"] = calculation
    normalized.setdefault("first_measurement_allowed_statuses", ["NOT_ENOUGH_DATA", "SUSPECTED", "LIKELY"])
    normalized.setdefault("confirmed_requires_repeated_measurement", True)
    normalized.setdefault("trajectory_contributes_to", [])
    normalized.setdefault("feedback", {"status": "not_evaluated", "human_review_required": True, "evidence_result_ids": []})
    provenance = (
        deepcopy(normalized.get("provenance"))
        if isinstance(normalized.get("provenance"), dict)
        else {}
    )
    if definition_source == "built_in":
        provenance.setdefault("creation_mode", "human_ai_collaboration")
        provenance.setdefault("human_lead", "Marina Boronenko")
        provenance.setdefault("ai_colleague", "Ray")
    else:
        provenance.setdefault("creation_mode", "constructor")
    normalized["provenance"] = provenance
    return normalized


def validate_mechanism_definition(definition: dict) -> dict:
    errors = []
    warnings = []
    if not isinstance(definition, dict):
        return {"valid": False, "errors": [{"field": None, "code": "DEFINITION_NOT_OBJECT"}], "warnings": []}
    code = _mechanism_code(definition.get("mechanism_code") or definition.get("id"))
    if not code:
        errors.append({"field": "mechanism_code", "code": "MECHANISM_CODE_REQUIRED"})
    if definition.get("development_status") not in SUPPORTED_DEVELOPMENT_STATUSES:
        errors.append({"field": "development_status", "code": "UNSUPPORTED_DEVELOPMENT_STATUS"})
    output = definition.get("output_scale") or {}
    output_scale_type = output.get("scale_type")
    registered_scale = get_scale_definition(output_scale_type)
    is_constructor_definition = definition.get("definition_source") == "constructor"
    if output_scale_type is None and is_constructor_definition:
        warnings.append({"field": "output_scale.scale_type", "code": "SCALE_NOT_BOUND", "analysis_compatibility": "requires_explicit_value_schema_or_later_scale_binding"})
    elif registered_scale is None:
        errors.append({"field": "output_scale.scale_type", "code": "REGISTERED_SCALE_REQUIRED_WHEN_BOUND"})
    elif output.get("scale_reference") != build_scale_reference(output_scale_type):
        errors.append({"field": "output_scale.scale_reference", "code": "SCALE_REFERENCE_MISMATCH"})
    temporal = definition.get("temporal_design") or {}
    if temporal.get("global_time_reference_required") is not True:
        errors.append({"field": "temporal_design.global_time_reference_required", "code": "GLOBAL_TIME_REFERENCE_REQUIRED"})
    global_time_scale = temporal.get("global_time_scale") or {}
    if global_time_scale.get("scale_type") != "datetime":
        errors.append({"field": "temporal_design.global_time_scale.scale_type", "code": "GLOBAL_TIME_SCALE_MUST_BE_DATETIME"})
    elif global_time_scale.get("scale_reference") != build_scale_reference("datetime"):
        errors.append({"field": "temporal_design.global_time_scale.scale_reference", "code": "GLOBAL_TIME_SCALE_REFERENCE_MISMATCH"})
    time_scale = temporal.get("time_scale") or {}
    time_scale_type = time_scale.get("scale_type")
    registered_time_scale = get_scale_definition(time_scale_type)
    if time_scale_type is None and is_constructor_definition:
        warnings.append({"field": "temporal_design.time_scale.scale_type", "code": "CONSTRUCT_TIME_SCALE_NOT_BOUND", "global_time_binding": "datetime_utc_remains_required"})
    elif registered_time_scale is None:
        errors.append({"field": "temporal_design.time_scale.scale_type", "code": "REGISTERED_TIME_SCALE_REQUIRED_WHEN_BOUND"})
    elif not registered_time_scale.get("temporal_roles"):
        errors.append({"field": "temporal_design.time_scale.scale_type", "code": "TEMPORAL_ROLE_CAPABLE_SCALE_REQUIRED"})
    else:
        if time_scale.get("scale_reference") != build_scale_reference(time_scale.get("scale_type")):
            errors.append({"field": "temporal_design.time_scale.scale_reference", "code": "TIME_SCALE_REFERENCE_MISMATCH"})
        role_aliases = {"recency": "duration", "persistence": "duration"}
        unsupported_roles = [
            role for role in temporal.get("time_roles", [])
            if role_aliases.get(role, role) not in registered_time_scale.get("temporal_roles", [])
        ]
        if unsupported_roles:
            errors.append({"field": "temporal_design.time_scale.scale_type", "code": "TIME_SCALE_ROLE_MISMATCH", "time_roles": unsupported_roles})
    if int(temporal.get("minimum_observation_count") or 0) < 1:
        errors.append({"field": "temporal_design.minimum_observation_count", "code": "MINIMUM_OBSERVATION_COUNT_REQUIRED"})
    calculation = definition.get("calculation_design") or {}
    if calculation.get("operator") not in SUPPORTED_CALCULATION_OPERATORS:
        errors.append({"field": "calculation_design.operator", "code": "UNSUPPORTED_CALCULATION_OPERATOR"})
    if (
        definition.get("definition_source") == "constructor"
        and definition.get("development_status") in {"trial", "active"}
    ):
        semantic_contract = definition.get("semantic_contract") or {}
        current_constructor_contract = (
            (definition.get("provenance") or {}).get(
                "constructor_schema_version"
            ) == "parameter-mechanism-constructor-3"
        )
        if current_constructor_contract and not str(
            semantic_contract.get("parameter_category")
            or semantic_contract.get("phenomenon_category")
            or ""
        ).strip():
            errors.append({
                "field": "semantic_contract.parameter_category",
                "code": "MECHANISM_CATEGORY_REQUIRED",
            })
        if current_constructor_contract and semantic_contract.get("working_definition_status") not in {
            "working", "trial", "validated",
        }:
            errors.append({
                "field": "semantic_contract.working_definition_status",
                "code": "WORKING_DEFINITION_STATUS_REQUIRED",
            })
        authorship = definition.get("authorship") or []
        if current_constructor_contract and (
            not isinstance(authorship, list) or not authorship
        ):
            errors.append({"field": "authorship", "code": "AUTHORSHIP_REQUIRED"})
            authorship = []
        for author_index, author in enumerate(
            authorship if current_constructor_contract else []
        ):
            if not isinstance(author, dict) or not str(
                author.get("display_name") or ""
            ).strip():
                errors.append({
                    "field": f"authorship.{author_index}.display_name",
                    "code": "AUTHOR_DISPLAY_NAME_REQUIRED",
                })
            elif author.get("role") not in AUTHORSHIP_ROLES:
                errors.append({
                    "field": f"authorship.{author_index}.role",
                    "code": "AUTHORSHIP_ROLE_INVALID",
                })

        measurement_nodes = (
            []
            if current_constructor_contract
            else (
                (definition.get("measurement_design") or {}).get(
                    "measurement_nodes"
                )
                or []
            )
        )
        dependencies = (
            (
                (definition.get("measurement_design") or {}).get(
                    "parameter_input_nodes"
                )
                or (definition.get("dependency_design") or {}).get(
                    "dependencies"
                )
                or []
            )
            if current_constructor_contract
            else (
                (definition.get("dependency_design") or {}).get(
                    "dependencies"
                )
                or []
            )
        )
        if current_constructor_contract and len(dependencies) < 2:
            errors.append({
                "field": "measurement_design.parameter_input_nodes",
                "code": "MECHANISM_REQUIRES_PARAMETER_COMBINATION",
                "minimum": 2,
            })
        node_codes = [] if current_constructor_contract else list(
            (definition.get("input_contract") or {}).get(
                "required_parameter_codes"
            )
            or []
        ) + list(
            (definition.get("input_contract") or {}).get(
                "optional_parameter_codes"
            )
            or []
        )
        for index, node in enumerate(measurement_nodes):
            if not isinstance(node, dict):
                errors.append({
                    "field": f"measurement_design.measurement_nodes.{index}",
                    "code": "MEASUREMENT_NODE_MUST_BE_OBJECT",
                })
                continue
            node_code = str(node.get("node_code") or "").strip()
            if node_code:
                node_codes.append(node_code)
            node_scale = node.get("scale_type")
            if node_scale and get_scale_definition(node_scale) is None:
                errors.append({
                    "field": f"measurement_design.measurement_nodes.{index}.scale_type",
                    "code": "REGISTERED_MEASUREMENT_SCALE_REQUIRED_WHEN_BOUND",
                })
        for index, node in enumerate(dependencies):
            if not isinstance(node, dict):
                errors.append({
                    "field": f"dependency_design.dependencies.{index}",
                    "code": "DEPENDENCY_NODE_MUST_BE_OBJECT",
                })
                continue
            dependency_code = str(node.get("node_code") or "").strip()
            if dependency_code:
                node_codes.append(dependency_code)
            if not str(node.get("target") or "").strip():
                errors.append({
                    "field": f"dependency_design.dependencies.{index}.target",
                    "code": "DEPENDENCY_TARGET_REQUIRED",
                })
            reference = node.get("parameter_reference")
            if current_constructor_contract and not isinstance(reference, dict):
                errors.append({
                    "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference",
                    "code": "REGISTERED_PARAMETER_REFERENCE_REQUIRED",
                })
            elif current_constructor_contract:
                for reference_field in (
                    "parameter_code", "definition_version",
                ):
                    if reference.get(reference_field) in (None, ""):
                        errors.append({
                            "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference.{reference_field}",
                            "code": "PARAMETER_REFERENCE_FIELD_REQUIRED",
                        })
                if reference.get("parameter_code") != node.get("target"):
                    errors.append({
                        "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference.parameter_code",
                        "code": "PARAMETER_REFERENCE_TARGET_MISMATCH",
                    })
                if reference.get("scale_type") != node.get("scale_type"):
                    errors.append({
                        "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference.scale_type",
                        "code": "PARAMETER_REFERENCE_SCALE_MISMATCH",
                    })
                if reference.get("scale_type") and get_scale_definition(
                    reference.get("scale_type")
                ) is None:
                    errors.append({
                        "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference.scale_type",
                        "code": "REGISTERED_PARAMETER_SCALE_REQUIRED_WHEN_BOUND",
                    })
                parameter_status = reference.get("development_status")
                if parameter_status not in {"trial", "active"}:
                    errors.append({
                        "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference.development_status",
                        "code": "MECHANISM_INPUT_PARAMETER_MUST_REACH_TRIAL",
                    })
                if (
                    definition.get("development_status") == "active"
                    and parameter_status != "active"
                ):
                    errors.append({
                        "field": f"measurement_design.parameter_input_nodes.{index}.parameter_reference.development_status",
                        "code": "ACTIVE_MECHANISM_REQUIRES_ACTIVE_PARAMETERS",
                    })

        components = calculation.get("components") or []
        unknown_components = [code for code in components if code not in set(node_codes)]
        if unknown_components:
            errors.append({
                "field": "calculation_design.components",
                "code": "UNKNOWN_FORMULA_NODE_REFERENCE",
                "values": unknown_components,
            })
        if len(node_codes) != len(set(node_codes)):
            errors.append({
                "field": "calculation_design.components",
                "code": "DUPLICATE_NODE_CODE",
            })
        weights = calculation.get("weights") or []
        if weights and len(weights) != len(components):
            errors.append({
                "field": "calculation_design.weights",
                "code": "FORMULA_WEIGHT_COUNT_MISMATCH",
            })
        calculation_bindings = []
        for node in measurement_nodes:
            if not isinstance(node, dict) or node.get("node_code") not in components:
                continue
            question_reference = node.get("question_reference") or {}
            calculation_bindings.append({
                "question_code": question_reference.get("question_code") or node.get("node_code"),
                "scale_type": question_reference.get("scale_type") or node.get("scale_type"),
                "response_type": question_reference.get("response_type"),
            })
        for node in dependencies:
            if isinstance(node, dict) and node.get("node_code") in components:
                calculation_bindings.append({
                    "question_code": node.get("node_code"),
                    "scale_type": node.get("scale_type"),
                })
        if current_constructor_contract:
            calculation_validation = validate_calculation_selection(
                operation_id=str(calculation.get("operator") or ""),
                question_bindings=calculation_bindings,
                configuration=calculation.get("configuration") or {},
                repeated_measurements=int(temporal.get("minimum_observation_count") or 1) > 1,
                ordered_measurements=bool(temporal.get("ordering_required")),
                output_scale_type=(definition.get("output_scale") or {}).get("scale_type"),
            )
            for calculation_error in calculation_validation.get("errors", []):
                errors.append({
                    "field": "calculation_design",
                    **calculation_error,
                })
        marker_codes = {
            str(marker.get("node_code") or "").strip()
            for marker in ((definition.get("marker_validation") or {}).get("markers") or [])
            if isinstance(marker, dict)
        }
        if marker_codes.intersection(components):
            errors.append({
                "field": "marker_validation.markers",
                "code": "MARKER_MUST_NOT_ENTER_MECHANISM_FORMULA",
            })
        markers = (
            (definition.get("marker_validation") or {}).get("markers")
            or []
        )
        for marker_index, marker in enumerate(
            markers if current_constructor_contract else []
        ):
            if not isinstance(marker, dict):
                errors.append({
                    "field": f"marker_validation.markers.{marker_index}",
                    "code": "MARKER_NODE_MUST_BE_OBJECT",
                })
                continue
            reference = marker.get("marker_reference")
            if not isinstance(reference, dict):
                errors.append({
                    "field": f"marker_validation.markers.{marker_index}.marker_reference",
                    "code": "REGISTERED_MARKER_REFERENCE_REQUIRED",
                })
                continue
            for reference_field in (
                "marker_code", "marker_id", "definition_version",
                "scale_type", "source_type", "observable_field",
            ):
                if reference.get(reference_field) in (None, ""):
                    errors.append({
                        "field": f"marker_validation.markers.{marker_index}.marker_reference.{reference_field}",
                        "code": "MARKER_REFERENCE_FIELD_REQUIRED",
                    })
            if marker.get("marker_role") not in MARKER_ROLES:
                errors.append({
                    "field": f"marker_validation.markers.{marker_index}.marker_role",
                    "code": "MARKER_ROLE_INVALID",
                })
            marker_status = reference.get("development_status")
            if marker_status not in {"trial", "active"}:
                errors.append({
                    "field": f"marker_validation.markers.{marker_index}.marker_reference.development_status",
                    "code": "MARKER_MUST_REACH_TRIAL",
                })
            if definition.get("development_status") == "active" and marker_status != "active":
                errors.append({
                    "field": f"marker_validation.markers.{marker_index}.marker_reference.development_status",
                    "code": "ACTIVE_MECHANISM_REQUIRES_ACTIVE_MARKER",
                })

        if not str(temporal.get("temporal_meaning") or "").strip():
            errors.append({"field": "temporal_design.temporal_meaning", "code": "TEMPORAL_MEANING_REQUIRED"})
        content_language = str(definition.get("content_language") or "").strip().lower()
        if content_language and content_language not in {"ru", "en", "es"}:
            errors.append({
                "field": "content_language",
                "code": "UNSUPPORTED_CONTENT_LANGUAGE",
                "value": content_language,
            })
        required_languages = (
            {content_language}
            if content_language in {"ru", "en", "es"}
            else {"ru", "en", "es"}
        )
        for language in required_languages:
            if not str((definition.get("title_i18n") or {}).get(language) or "").strip():
                errors.append({"field": f"title_i18n.{language}", "code": "TITLE_LANGUAGE_REQUIRED"})
            if not str(((definition.get("meaning") or {}).get("construct_definition") or {}).get(language) or "").strip():
                errors.append({"field": f"meaning.construct_definition.{language}", "code": "CONSTRUCT_DEFINITION_LANGUAGE_REQUIRED"})
        inputs = definition.get("input_contract") or {}
        total_inputs = sum(len(inputs.get(key) or []) for key in (
            "required_parameter_codes", "optional_parameter_codes",
            "required_mechanism_codes", "optional_mechanism_codes",
            "required_function_codes", "supporting_function_codes",
        ))
        if total_inputs == 0:
            errors.append({"field": "input_contract", "code": "MECHANISM_INPUT_REQUIRED"})
        if definition.get("confirmed_requires_repeated_measurement") and int(temporal.get("minimum_observation_count") or 0) < 2:
            errors.append({"field": "temporal_design.minimum_observation_count", "code": "CONFIRMATION_REQUIRES_REPEATED_MEASUREMENT"})
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def list_mechanism_definitions(
    *, include_inactive: bool = False, include_all_versions: bool = False,
) -> list[dict]:
    by_identity = {
        (code, _version(definition)): deepcopy(definition)
        for code, definition in MECHANISM_REGISTRY.items()
    }
    for raw in _load_custom_raw():
        normalized = normalize_mechanism_definition(raw)
        normalized["definition_validation"] = validate_mechanism_definition(normalized)
        by_identity[(normalized["mechanism_code"], _version(normalized))] = normalized
    definitions = list(by_identity.values())
    if not include_inactive:
        definitions = [item for item in definitions if item.get("lifecycle_status") == "active"]
    if not include_all_versions:
        latest = {}
        for item in definitions:
            code = item["mechanism_code"]
            if code not in latest or _version(item) > _version(latest[code]):
                latest[code] = item
        definitions = list(latest.values())
    return sorted(definitions, key=lambda item: (item["mechanism_code"], _version(item)))


def get_mechanism(
    mechanism_id: str,
    *, definition_version: int | None = None, include_inactive: bool = False,
) -> dict | None:
    code = _mechanism_code(mechanism_id)
    matching = [
        item for item in list_mechanism_definitions(
            include_inactive=include_inactive, include_all_versions=True
        )
        if item["mechanism_code"] == code
        and (definition_version is None or _version(item) == int(definition_version))
    ]
    return max(matching, key=_version) if matching else None


def list_mechanisms() -> list[dict]:
    """Compatibility view used by the current mechanism calculation layer."""
    return list_mechanism_definitions()


def upsert_custom_mechanism_draft(definition: dict) -> dict:
    incoming = deepcopy(definition)
    code = _mechanism_code(incoming.get("mechanism_code") or incoming.get("id"))
    if not code:
        return {"ok": False, "status": "mechanism_code_required"}
    existing = list_mechanism_definitions(include_inactive=True, include_all_versions=True)
    matching = [item for item in existing if item["mechanism_code"] == code]
    requested_version = incoming.get("definition_version")
    if requested_version is None:
        drafts = [item for item in matching if item.get("definition_source") == "constructor" and item.get("development_status") == "draft"]
        requested_version = max((_version(item) for item in drafts), default=max((_version(item) for item in matching), default=0) + 1)
    incoming["definition_version"] = int(requested_version)
    incoming["development_status"] = "draft"
    normalized = normalize_mechanism_definition(incoming)
    validation = validate_mechanism_definition(normalized)
    if not validation["valid"]:
        return {"ok": False, "status": "definition_invalid", "definition": normalized, "validation": validation}
    raw_definitions = _load_custom_raw()
    replaced = False
    updated = []
    for raw in raw_definitions:
        if _mechanism_code(raw.get("mechanism_code") or raw.get("id")) == code and _version(raw) == int(requested_version):
            if str(raw.get("development_status") or "draft") != "draft":
                return {"ok": False, "status": "immutable_non_draft_version"}
            updated.append(normalized)
            replaced = True
        else:
            updated.append(raw)
    if not replaced:
        if any(_version(item) == int(requested_version) for item in matching):
            return {"ok": False, "status": "definition_version_already_exists"}
        updated.append(normalized)
    _save_custom_raw(updated)
    return {"ok": True, "status": "draft_updated" if replaced else "draft_created", "definition": normalized, "validation": validation}


def transition_custom_mechanism_definition(
    mechanism_code: str, definition_version: int, target_status: str,
) -> dict:
    transitions = {"draft": {"trial"}, "trial": {"active"}}
    raw_definitions = _load_custom_raw()
    updated = []
    selected = None
    for raw in raw_definitions:
        if _mechanism_code(raw.get("mechanism_code") or raw.get("id")) == _mechanism_code(mechanism_code) and _version(raw) == int(definition_version):
            selected = normalize_mechanism_definition(raw)
            current = selected["development_status"]
            if target_status not in transitions.get(current, set()):
                return {"ok": False, "status": "invalid_status_transition", "current_status": current, "target_status": target_status}
            selected["development_status"] = target_status
            selected["lifecycle_status"] = "active"
            validation = validate_mechanism_definition(selected)
            if not validation["valid"]:
                return {"ok": False, "status": "transition_validation_failed", "definition": selected, "validation": validation}
            updated.append(selected)
        else:
            updated.append(raw)
    if selected is None:
        return {"ok": False, "status": "definition_not_found"}
    _save_custom_raw(updated)
    return {"ok": True, "status": f"transitioned_to_{target_status}", "definition": selected}


def delete_custom_mechanism_draft(mechanism_code: str, definition_version: int) -> dict:
    kept = []
    deleted = None
    for raw in _load_custom_raw():
        matches = _mechanism_code(raw.get("mechanism_code") or raw.get("id")) == _mechanism_code(mechanism_code) and _version(raw) == int(definition_version)
        if not matches:
            kept.append(raw)
            continue
        normalized = normalize_mechanism_definition(raw)
        if normalized["development_status"] != "draft":
            return {"ok": False, "status": "only_draft_can_be_deleted"}
        deleted = normalized
    if deleted is None:
        return {"ok": False, "status": "definition_not_found"}
    _save_custom_raw(kept)
    return {
        "ok": True,
        "status": "draft_deleted",
        "definition": deleted,
        "calculation_cleanup": {
            "performed": False,
            "reason": "no mechanism definition-version link exists in legacy calculation runs",
        },
    }
