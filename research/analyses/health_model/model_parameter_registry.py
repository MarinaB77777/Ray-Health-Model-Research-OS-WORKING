import json
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
    list_scale_definitions,
    normalize_scale_id,
)
from research.analyses.health_model.parameter_calculation_registry import (
    validate_calculation_selection,
)
from research.analyses.health_model.observable_marker_registry import (
    AUTHORSHIP_ROLES,
    MARKER_ROLES,
)


MODEL_PARAMETER_REGISTRY_SCHEMA_VERSION = (
    "calculated-model-parameter-registry-1"
)

MODEL_PARAMETER_DEFINITION_SCHEMA_VERSION = (
    "calculated-model-parameter-definition-1"
)

MODEL_PARAMETER_NAMESPACE = UUID(
    "5ad3ca20-3c6c-4e66-8fc7-1a348ee1f63c"
)

CUSTOM_PARAMETER_DEFINITIONS_PATH = Path(
    "data/model_parameter_definitions.json"
)


SUPPORTED_PARAMETER_KINDS = {
    "scalar",
    "binary",
    "categorical",
    "ordinal",
    "vector",
    "time_series",
    "distribution",
    "interval",
    "structured",
}

SUPPORTED_VALUE_TYPES = {
    "bool",
    "int",
    "float",
    "str",
    "list",
    "dict",
}

SUPPORTED_SCALE_TYPES = {
    definition["scale_code"]
    for definition in list_scale_definitions(
        include_non_active=True
    )
} | {None}

SUPPORTED_LIFECYCLE_STATUSES = {
    "draft",
    "active",
    "deprecated",
    "disabled",
    "archived",
}

SUPPORTED_SCIENTIFIC_STATUSES = {
    "proposed",
    "scientifically_reviewed",
    "empirically_validated",
    "rejected",
}

SUPPORTED_DEVELOPMENT_STATUSES = {
    "draft",
    "trial",
    "active",
}

SUPPORTED_INTERFACE_LANGUAGES = {
    "ru",
    "en",
    "es",
}

SUPPORTED_MEASUREMENT_TYPES = {
    "direct_observation",
    "single_indicator",
    "composite",
    "derived",
    "latent_estimate",
    "structured",
    "time_series",
}

SUPPORTED_TIME_ROLES = {
    "observation_time",
    "duration",
    "latency",
    "frequency",
    "recency",
    "sequence_position",
    "change_rate",
    "persistence",
    "time_window",
    "none",
}

SUPPORTED_TEMPORAL_AGGREGATIONS = {
    "single_observation",
    "latest",
    "earliest",
    "mean_over_window",
    "maximum_over_window",
    "minimum_over_window",
    "sum_over_window",
    "change_between_observations",
    "slope_over_time",
    "persistence_over_time",
    "sequence_pattern",
}

SUPPORTED_TRANSFORMATION_TYPES = {
    "identity",
    "linear",
    "reverse_linear",
    "threshold",
    "categorical_mapping",
}

SUPPORTED_FEEDBACK_STATUSES = {
    "not_evaluated",
    "insufficient_data",
    "preliminary",
    "supported",
    "weakly_supported",
    "not_supported",
    "contradicted",
}

# Временная совместимость со старым именем.
SUPPORTED_DEFINITION_STATUSES = (
    SUPPORTED_LIFECYCLE_STATUSES
)

SUPPORTED_CALCULATION_STATUSES = {
    "calculated",
    "not_enough_data",
    "not_applicable",
    "blocked",
    "invalid",
    "error",
    "unknown",
}


_BUILT_IN_TITLE_ES = {
    "load_blocks.l_environment": "Carga ambiental",
    "load_blocks.l_requirements": "Carga de exigencias",
    "load_blocks.l_external": "Carga externa",
    "load_blocks.l_additional": "Carga adicional",
    "load_blocks.l_total": "Carga total",
    "resource_deficit_domains.r_phys": "Déficit de recursos físicos",
    "resource_deficit_domains.r_psych": "Déficit de recursos psicológicos",
    "resource_deficit_domains.r_goal": "Déficit de recursos para objetivos",
    "resource_deficit_domains.r_social": "Déficit de recursos sociales",
    "resource_deficit_domains.r_fin": "Déficit de recursos financieros",
    "resource_deficit_domains.r_spiritual": "Déficit de recursos de sentido",
    "resource_deficit_domains.resource_deficit_global": "Déficit global de recursos",
    **{
        f"load_failure_risk.p{index}": f"Riesgo de fallo ante la carga P{index}"
        for index in range(1, 6)
    },
    "load_failure_risk.p_total": "Riesgo total de fallo ante la carga",
    "manifestation_layer.manifestation_score": "Puntuación de manifestación",
    "manifestation_layer.manifestation_score_norm": "Puntuación normalizada de manifestación",
    "stress_burden.stress_burden_raw": "Carga de estrés bruta",
    "stress_burden.stress_burden_norm": "Carga de estrés normalizada",
    "stress_burden.stress_burden_final": "Carga de estrés final",
    "stress_burden.critical_override_applied": "Anulación crítica aplicada",
    "modeled_burden.pressure_proxy": "Indicador sustituto de presión",
    "modeled_burden.resource_deficit": "Déficit de recursos modelado",
    "modeled_burden.modeled_burden": "Carga modelada",
    "current_state.current_state_final": "Estado actual",
    "current_state.burden_manifestation_delta": "Diferencia entre carga y manifestación",
    "current_state.mode": "Modo de interpretación del estado actual",
    "critical_status.is_critical": "Estado crítico",
    "forecast_allowed": "Pronóstico permitido",
    "readiness_status": "Estado de preparación",
    "state_risk": "Riesgo del estado",
    "trajectory_risk": "Riesgo de la trayectoria",
}


def _stable_parameter_id(
    parameter_code: str,
) -> str:
    return str(
        uuid5(
            MODEL_PARAMETER_NAMESPACE,
            parameter_code,
        )
    )


def _definition(
    *,
    parameter_code: str,
    title_ru: str,
    title_en: str,
    parameter_kind: str,
    value_type: str,
    scale_type: str | None,
    value_path: str,
    status_path: str | None = None,
    minimum: float | int | None = None,
    maximum: float | int | None = None,
    unit: str | None = None,
    allowed_values: list[Any] | None = None,
    ordered_values: list[Any] | None = None,
    components: list[dict] | None = None,
    score_direction: str | None = None,
    research_available: bool = True,
    allowed_analysis_roles: list[str] | None = None,
    parameter_role: str = "model_output",
    definition_version: int = 1,
    model_id: str = "health_model_v6_1",
    calculation_version: str = "1",
    lifecycle_status: str = "active",
    scientific_status: str = "proposed",
    development_status: str = "active",
) -> dict:
    scale_reference = (
        build_scale_reference(scale_type)
        if scale_type is not None
        else None
    )

    return {
        "schema_version": (
            MODEL_PARAMETER_DEFINITION_SCHEMA_VERSION
        ),
        "registry_schema_version": (
            MODEL_PARAMETER_REGISTRY_SCHEMA_VERSION
        ),
        "parameter_id": _stable_parameter_id(
            parameter_code
        ),
        "parameter_code": parameter_code,
        "definition_version": definition_version,
        "title": {
            "ru": title_ru,
            "en": title_en,
            "es": _BUILT_IN_TITLE_ES[parameter_code],
        },
        "parameter_role": parameter_role,
        "parameter_kind": parameter_kind,
        "value_type": value_type,
        "scale_type": scale_type,
        "scale_reference": scale_reference,
        "value_schema": {
            "minimum": minimum,
            "maximum": maximum,
            "unit": unit,
            "allowed_values": (
                list(allowed_values)
                if allowed_values is not None
                else None
            ),
            "ordered_values": (
                list(ordered_values)
                if ordered_values is not None
                else None
            ),
            "components": (
                deepcopy(components)
                if components is not None
                else None
            ),
        },
        "missing_semantics": {
            "unknown_is_zero": False,
            "not_enough_data_allowed": True,
            "not_applicable_allowed": True,
            "missing_value": None,
        },
        "score_direction": score_direction,
        "calculation": {
            "calculator_id": model_id,
            "model_id": model_id,
            "calculation_version": calculation_version,
            "value_path": value_path,
            "status_path": status_path,
        },
        "research": {
            "available": research_available,
            "allowed_analysis_roles": (
                list(allowed_analysis_roles)
                if allowed_analysis_roles is not None
                else [
                    "predictor",
                    "outcome",
                    "covariate",
                ]
            ),
        },
        "definition_source": "built_in",

        "lifecycle_status": (
            lifecycle_status
        ),

        "scientific_status": (
            scientific_status
        ),
        
        "development_status": (
            development_status
        ),
        # Временное совместимое поле.
        # Новая логика должна читать lifecycle_status.
        "status": lifecycle_status,
    }


BUILT_IN_MODEL_PARAMETER_DEFINITIONS = {
    # Load blocks
    definition["parameter_code"]: definition
    for definition in [
        _definition(
            parameter_code=(
                "load_blocks.l_environment"
            ),
            title_ru="Нагрузка среды",
            title_en="Environmental Load",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "load_blocks.l_environment"
            ),
            minimum=0,
            maximum=5.25,
            score_direction="higher_is_more_load",
        ),
        _definition(
            parameter_code=(
                "load_blocks.l_requirements"
            ),
            title_ru="Нагрузка требований",
            title_en="Requirements Load",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "load_blocks.l_requirements"
            ),
            minimum=0,
            maximum=5,
            score_direction="higher_is_more_load",
        ),
        _definition(
            parameter_code="load_blocks.l_external",
            title_ru="Внешняя нагрузка",
            title_en="External Load",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path="load_blocks.l_external",
            minimum=0,
            score_direction="higher_is_more_load",
        ),
        _definition(
            parameter_code=(
                "load_blocks.l_additional"
            ),
            title_ru="Дополнительная нагрузка",
            title_en="Additional Load",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "load_blocks.l_additional"
            ),
            minimum=0,
            score_direction="higher_is_more_load",
        ),
        _definition(
            parameter_code="load_blocks.l_total",
            title_ru="Общая нагрузка",
            title_en="Total Load",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path="load_blocks.l_total",
            minimum=0,
            score_direction="higher_is_more_load",
        ),

        # Resource deficit domains
        _definition(
            parameter_code=(
                "resource_deficit_domains.r_phys"
            ),
            title_ru="Физический дефицит ресурса",
            title_en="Physical Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains.r_phys"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "resource_deficit_domains.r_psych"
            ),
            title_ru="Психологический дефицит ресурса",
            title_en=(
                "Psychological Resource Deficit"
            ),
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains.r_psych"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "resource_deficit_domains.r_goal"
            ),
            title_ru="Целевой дефицит ресурса",
            title_en="Goal Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains.r_goal"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "resource_deficit_domains.r_social"
            ),
            title_ru="Социальный дефицит ресурса",
            title_en="Social Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains.r_social"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "resource_deficit_domains.r_fin"
            ),
            title_ru="Финансовый дефицит ресурса",
            title_en="Financial Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains.r_fin"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "resource_deficit_domains.r_spiritual"
            ),
            title_ru="Смысловой дефицит ресурса",
            title_en="Meaning Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains.r_spiritual"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "resource_deficit_domains."
                "resource_deficit_global"
            ),
            title_ru="Глобальный дефицит ресурса",
            title_en="Global Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "resource_deficit_domains."
                "resource_deficit_global"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),

        # Load failure risk
        *[
            _definition(
                parameter_code=(
                    f"load_failure_risk.p{index}"
                ),
                title_ru=(
                    f"Риск срыва нагрузки P{index}"
                ),
                title_en=(
                    f"Load Failure Risk P{index}"
                ),
                parameter_kind="scalar",
                value_type="float",
                scale_type="continuous",
                value_path=(
                    f"load_failure_risk.p{index}"
                ),
                minimum=0,
                maximum=5,
                score_direction="higher_is_more_risk",
            )
            for index in range(1, 6)
        ],
        _definition(
            parameter_code=(
                "load_failure_risk.p_total"
            ),
            title_ru="Суммарный риск срыва нагрузки",
            title_en="Total Load Failure Risk",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "load_failure_risk.p_total"
            ),
            minimum=0,
            maximum=25,
            score_direction="higher_is_more_risk",
        ),

        # Manifestation layer
        _definition(
            parameter_code=(
                "manifestation_layer."
                "manifestation_score"
            ),
            title_ru="Проявленность состояния",
            title_en="Manifestation Score",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "manifestation_layer."
                "manifestation_score"
            ),
            status_path=(
                "manifestation_layer.status"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_manifestation"
            ),
        ),
        _definition(
            parameter_code=(
                "manifestation_layer."
                "manifestation_score_norm"
            ),
            title_ru=(
                "Нормированная проявленность состояния"
            ),
            title_en=(
                "Normalized Manifestation Score"
            ),
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "manifestation_layer."
                "manifestation_score_norm"
            ),
            status_path=(
                "manifestation_layer.status"
            ),
            minimum=0,
            maximum=10,
            score_direction=(
                "higher_is_more_manifestation"
            ),
        ),

        # Stress burden
        _definition(
            parameter_code=(
                "stress_burden.stress_burden_raw"
            ),
            title_ru="Сырая стрессовая нагрузка",
            title_en="Raw Stress Burden",
            parameter_kind="scalar",
            value_type="float",
            scale_type="ratio",
            value_path=(
                "stress_burden.stress_burden_raw"
            ),
            status_path="stress_burden.status",
            minimum=0,
            score_direction="higher_is_more_burden",
        ),
        _definition(
            parameter_code=(
                "stress_burden.stress_burden_norm"
            ),
            title_ru=(
                "Нормированная стрессовая нагрузка"
            ),
            title_en="Normalized Stress Burden",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "stress_burden.stress_burden_norm"
            ),
            status_path="stress_burden.status",
            minimum=0,
            maximum=10,
            score_direction="higher_is_more_burden",
        ),
        _definition(
            parameter_code=(
                "stress_burden.stress_burden_final"
            ),
            title_ru=(
                "Итоговая стрессовая нагрузка"
            ),
            title_en="Final Stress Burden",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "stress_burden.stress_burden_final"
            ),
            status_path="stress_burden.status",
            minimum=0,
            maximum=10,
            score_direction="higher_is_more_burden",
        ),
        _definition(
            parameter_code=(
                "stress_burden."
                "critical_override_applied"
            ),
            title_ru=(
                "Применён критический override"
            ),
            title_en="Critical Override Applied",
            parameter_kind="binary",
            value_type="bool",
            scale_type="binary",
            value_path=(
                "stress_burden."
                "critical_override_applied"
            ),
            status_path="stress_burden.status",
            allowed_values=[False, True],
            score_direction=None,
            allowed_analysis_roles=[
                "predictor",
                "outcome",
                "grouping",
                "covariate",
            ],
        ),

        # Modeled burden
        _definition(
            parameter_code=(
                "modeled_burden.pressure_proxy"
            ),
            title_ru="Прокси давления",
            title_en="Pressure Proxy",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "modeled_burden.pressure_proxy"
            ),
            minimum=0,
            score_direction="higher_is_more_pressure",
        ),
        _definition(
            parameter_code=(
                "modeled_burden.resource_deficit"
            ),
            title_ru="Дефицит ресурса модели",
            title_en="Modeled Resource Deficit",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "modeled_burden.resource_deficit"
            ),
            minimum=0,
            maximum=5,
            score_direction=(
                "higher_is_more_resource_deficit"
            ),
        ),
        _definition(
            parameter_code=(
                "modeled_burden.modeled_burden"
            ),
            title_ru="Моделируемая нагрузка",
            title_en="Modeled Burden",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "modeled_burden.modeled_burden"
            ),
            minimum=0,
            score_direction="higher_is_more_burden",
        ),

        # Current state
        _definition(
            parameter_code=(
                "current_state.current_state_final"
            ),
            title_ru="Текущее состояние",
            title_en="Current State",
            parameter_kind="scalar",
            value_type="float",
            scale_type="continuous",
            value_path=(
                "current_state.current_state_final"
            ),
            status_path="current_state.status",
            minimum=0,
            maximum=5,
            score_direction="higher_is_more_burden",
        ),
        _definition(
            parameter_code=(
                "current_state."
                "burden_manifestation_delta"
            ),
            title_ru=(
                "Дельта нагрузки и проявленности"
            ),
            title_en=(
                "Burden Manifestation Delta"
            ),
            parameter_kind="scalar",
            value_type="float",
            scale_type="interval",
            value_path=(
                "current_state."
                "burden_manifestation_delta"
            ),
            status_path="current_state.status",
            minimum=-5,
            maximum=5,
            score_direction=(
                "signed_model_manifestation_difference"
            ),
        ),
        _definition(
            parameter_code="current_state.mode",
            title_ru="Режим интерпретации состояния",
            title_en="Current State Interpretation Mode",
            parameter_kind="categorical",
            value_type="str",
            scale_type="nominal",
            value_path="current_state.mode",
            status_path="current_state.status",
            allowed_values=[
                "PREVENTIVE_WINDOW",
                "HIDDEN_FACTOR_MODE",
                "DIAGNOSTIC_MODE",
            ],
            score_direction=None,
            allowed_analysis_roles=[
                "outcome",
                "predictor",
                "grouping",
            ],
        ),

        # Critical status
        _definition(
            parameter_code=(
                "critical_status.is_critical"
            ),
            title_ru="Критический статус",
            title_en="Critical Status",
            parameter_kind="binary",
            value_type="bool",
            scale_type="binary",
            value_path=(
                "critical_status.is_critical"
            ),
            allowed_values=[False, True],
            score_direction="true_is_critical",
            allowed_analysis_roles=[
                "outcome",
                "predictor",
                "grouping",
                "covariate",
            ],
        ),

        # Readiness and forecast
        _definition(
            parameter_code="forecast_allowed",
            title_ru="Прогноз разрешён",
            title_en="Forecast Allowed",
            parameter_kind="binary",
            value_type="bool",
            scale_type="binary",
            value_path="forecast_allowed",
            allowed_values=[False, True],
            score_direction=None,
            allowed_analysis_roles=[
                "outcome",
                "grouping",
            ],
        ),
        _definition(
            parameter_code="readiness_status",
            title_ru="Статус готовности",
            title_en="Readiness Status",
            parameter_kind="categorical",
            value_type="str",
            scale_type="nominal",
            value_path="readiness_status",
            allowed_values=[
                "ORIENTING",
                "NOT_ENOUGH_DATA",
                "READY",
                "BLOCKED",
            ],
            score_direction=None,
            allowed_analysis_roles=[
                "outcome",
                "grouping",
            ],
        ),

        # Structured future outputs.
        _definition(
            parameter_code="state_risk",
            title_ru="Риск состояния",
            title_en="State Risk",
            parameter_kind="structured",
            value_type="dict",
            scale_type="structured",
            value_path="state_risk",
            status_path="state_risk.status",
            research_available=True,
            allowed_analysis_roles=[],
        ),
        _definition(
            parameter_code="trajectory_risk",
            title_ru="Траекторный риск",
            title_en="Trajectory Risk",
            parameter_kind="structured",
            value_type="dict",
            scale_type="structured",
            value_path="trajectory_risk",
            status_path="trajectory_risk.status",
            research_available=True,
            allowed_analysis_roles=[],
        ),
    ]
}


def _clean_parameter_code(
    parameter_code: Any,
) -> str:
    return str(parameter_code or "").strip()


def _load_custom_definitions_raw() -> list[dict]:
    if not CUSTOM_PARAMETER_DEFINITIONS_PATH.exists():
        return []

    raw = CUSTOM_PARAMETER_DEFINITIONS_PATH.read_text(
        encoding="utf-8"
    ).strip()

    if not raw:
        return []

    data = json.loads(raw)

    if not isinstance(data, list):
        raise ValueError(
            "Custom model parameter definitions "
            "must be stored as a JSON list"
        )

    return data


def _save_custom_definitions_raw(
    definitions: list[dict],
) -> None:
    CUSTOM_PARAMETER_DEFINITIONS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CUSTOM_PARAMETER_DEFINITIONS_PATH.write_text(
        json.dumps(
            definitions,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

def _definition_lifecycle_status(
    definition: dict,
) -> str:
    return str(
        definition.get(
            "lifecycle_status"
        )
        or definition.get("status")
        or "draft"
    )


def _definition_scientific_status(
    definition: dict,
) -> str:
    return str(
        definition.get(
            "scientific_status"
        )
        or "proposed"
    )

def _definition_development_status(
    definition: dict,
) -> str:
    explicit_status = definition.get(
        "development_status"
    )

    if explicit_status:
        status = str(explicit_status)
        return "draft" if status == "developing" else status

    lifecycle_status = (
        _definition_lifecycle_status(
            definition
        )
    )

    if lifecycle_status == "draft":
        return "draft"

    if lifecycle_status == "active":
        return "active"

    return "draft"

def _definition_version(
    definition: dict,
) -> int:
    try:
        return int(
            definition.get(
                "definition_version",
                1,
            )
        )
    except (TypeError, ValueError):
        return 1

def validate_model_parameter_definition(
    definition: dict,
) -> dict:
    errors = []
    warnings = []

    if not isinstance(definition, dict):
        return {
            "valid": False,
            "errors": [
                {
                    "field": None,
                    "code": "DEFINITION_NOT_OBJECT",
                }
            ],
            "warnings": [],
        }

    parameter_code = _clean_parameter_code(
        definition.get("parameter_code")
    )

    parameter_id = definition.get("parameter_id")
    parameter_kind = definition.get(
        "parameter_kind"
    )
    value_type = definition.get("value_type")
    scale_type = definition.get("scale_type")
    definition_source = definition.get("definition_source")
    scale_binding_is_optional = definition_source == "constructor"
    lifecycle_status = (
        _definition_lifecycle_status(
            definition
        )
    )
    scientific_status = (
        _definition_scientific_status(
            definition
        )
    )

    development_status = (
        _definition_development_status(
            definition
        )
    )

    if not parameter_code:
        errors.append({
            "field": "parameter_code",
            "code": "PARAMETER_CODE_REQUIRED",
        })

    if not parameter_id:
        errors.append({
            "field": "parameter_id",
            "code": "PARAMETER_ID_REQUIRED",
        })
    else:
        try:
            UUID(str(parameter_id))
        except (TypeError, ValueError):
            errors.append({
                "field": "parameter_id",
                "code": "PARAMETER_ID_INVALID_UUID",
            })

    if parameter_kind not in SUPPORTED_PARAMETER_KINDS:
        errors.append({
            "field": "parameter_kind",
            "code": "UNSUPPORTED_PARAMETER_KIND",
            "value": parameter_kind,
        })

    if value_type not in SUPPORTED_VALUE_TYPES:
        errors.append({
            "field": "value_type",
            "code": "UNSUPPORTED_VALUE_TYPE",
            "value": value_type,
        })

    if scale_type is None and scale_binding_is_optional:
        warnings.append({
            "field": "scale_type",
            "code": "SCALE_NOT_BOUND",
            "analysis_compatibility": "requires_explicit_value_schema_or_later_scale_binding",
        })
    elif scale_type not in SUPPORTED_SCALE_TYPES:
        errors.append({
            "field": "scale_type",
            "code": "UNSUPPORTED_SCALE_TYPE",
            "value": scale_type,
        })
    elif scale_type is not None:
        scale_reference = definition.get(
            "scale_reference"
        )
        registered_scale = get_scale_definition(
            scale_type
        )
        if registered_scale is None:
            errors.append({
                "field": "scale_reference",
                "code": "REGISTERED_SCALE_REQUIRED",
            })
        elif not isinstance(scale_reference, dict):
            errors.append({
                "field": "scale_reference",
                "code": "SCALE_REFERENCE_REQUIRED",
            })
        elif (
            scale_reference.get("scale_id")
            != registered_scale["scale_id"]
            or scale_reference.get(
                "scale_definition_version"
            )
            != registered_scale["definition_version"]
        ):
            errors.append({
                "field": "scale_reference",
                "code": "SCALE_REFERENCE_MISMATCH",
            })

    if lifecycle_status not in (
        SUPPORTED_LIFECYCLE_STATUSES
    ):
        errors.append({
            "field": "lifecycle_status",
            "code": (
                "UNSUPPORTED_LIFECYCLE_STATUS"
            ),
            "value": lifecycle_status,
        })

    if scientific_status not in (
        SUPPORTED_SCIENTIFIC_STATUSES
    ):
        errors.append({
            "field": "scientific_status",
            "code": (
                "UNSUPPORTED_SCIENTIFIC_STATUS"
            ),
            "value": scientific_status,
        })
    if development_status not in (
        SUPPORTED_DEVELOPMENT_STATUSES
    ):
        errors.append({
            "field": "development_status",
            "code": (
                "UNSUPPORTED_DEVELOPMENT_STATUS"
            ),
            "value": development_status,
        })

    title = definition.get("title")
    if not isinstance(title, dict):
        errors.append({
            "field": "title",
            "code": "MULTILINGUAL_TITLE_REQUIRED",
        })
        title = {}

    content_language = str(
        definition.get("content_language") or ""
    ).strip().lower()

    if (
        content_language
        and content_language
        not in SUPPORTED_INTERFACE_LANGUAGES
    ):
        errors.append({
            "field": "content_language",
            "code": "UNSUPPORTED_CONTENT_LANGUAGE",
            "value": content_language,
        })

    if development_status in {"trial", "active"}:
        required_languages = (
            {content_language}
            if content_language
            in SUPPORTED_INTERFACE_LANGUAGES
            else SUPPORTED_INTERFACE_LANGUAGES
        )
        for language in required_languages:
            if not str(title.get(language) or "").strip():
                errors.append({
                    "field": f"title.{language}",
                    "code": "TITLE_LANGUAGE_REQUIRED",
                    "language": language,
                })
     
    calculation = definition.get("calculation")

    if not isinstance(calculation, dict):
        errors.append({
            "field": "calculation",
            "code": "CALCULATION_OBJECT_REQUIRED",
        })
    else:
        if not calculation.get("value_path"):
            errors.append({
                "field": "calculation.value_path",
                "code": "VALUE_PATH_REQUIRED",
            })

        if not calculation.get("model_id"):
            errors.append({
                "field": "calculation.model_id",
                "code": "MODEL_ID_REQUIRED",
            })

        if not calculation.get(
            "calculation_version"
        ):
            errors.append({
                "field": (
                    "calculation.calculation_version"
                ),
                "code": (
                    "CALCULATION_VERSION_REQUIRED"
                ),
            })

    value_schema = definition.get("value_schema")

    if not isinstance(value_schema, dict):
        errors.append({
            "field": "value_schema",
            "code": "VALUE_SCHEMA_REQUIRED",
        })
        value_schema = {}

    minimum = value_schema.get("minimum")
    maximum = value_schema.get("maximum")

    if (
        minimum is not None
        and maximum is not None
        and minimum > maximum
    ):
        errors.append({
            "field": "value_schema",
            "code": "INVALID_NUMERIC_RANGE",
        })

    allowed_values = value_schema.get(
        "allowed_values"
    )
    ordered_values = value_schema.get(
        "ordered_values"
    )
    components = value_schema.get("components")

    if parameter_kind == "binary":
        if value_type != "bool":
            errors.append({
                "field": "value_type",
                "code": (
                    "BINARY_PARAMETER_REQUIRES_BOOL"
                ),
            })

    if parameter_kind == "categorical":
        if not isinstance(allowed_values, list):
            errors.append({
                "field": (
                    "value_schema.allowed_values"
                ),
                "code": (
                    "CATEGORICAL_VALUES_REQUIRED"
                ),
            })

    if parameter_kind == "ordinal":
        if not isinstance(ordered_values, list):
            errors.append({
                "field": (
                    "value_schema.ordered_values"
                ),
                "code": (
                    "ORDINAL_VALUES_REQUIRED"
                ),
            })

    if parameter_kind == "vector":
        if not isinstance(components, list):
            errors.append({
                "field": (
                    "value_schema.components"
                ),
                "code": (
                    "VECTOR_COMPONENTS_REQUIRED"
                ),
            })

    if (
        parameter_kind in {
            "structured",
            "distribution",
            "interval",
            "time_series",
            "vector",
        }
        and scale_type != "structured"
    ):
        warnings.append({
            "field": "scale_type",
            "code": (
                "COMPLEX_PARAMETER_SCALE_REVIEW"
            ),
        })

    research = definition.get("research")

    if not isinstance(research, dict):
        errors.append({
            "field": "research",
            "code": "RESEARCH_CONFIGURATION_REQUIRED",
        })

    is_constructor_definition = (
        definition_source
        == "constructor"
    )

    meaning = definition.get(
        "meaning"
    )

    if not isinstance(meaning, dict):
        errors.append({
            "field": "meaning",
            "code": "MEANING_OBJECT_REQUIRED",
        })
        meaning = {}

    if (
        is_constructor_definition
        and development_status in {
            "trial",
            "active",
        }
    ):
        construct_definition = (
            meaning.get(
                "construct_definition"
            )
            or {}
        )

        required_languages = (
            {content_language}
            if content_language
            in SUPPORTED_INTERFACE_LANGUAGES
            else SUPPORTED_INTERFACE_LANGUAGES
        )
        for language in required_languages:
            if not str(
                construct_definition.get(
                    language
                )
                or ""
            ).strip():
                errors.append({
                    "field": (
                        "meaning."
                        "construct_definition."
                        f"{language}"
                    ),
                    "code": (
                        "CONSTRUCT_DEFINITION_"
                        "LANGUAGE_REQUIRED"
                    ),
                    "language": language,
                })

    measurement_design = (
        definition.get(
            "measurement_design"
        )
    )

    if not isinstance(
        measurement_design,
        dict,
    ):
        errors.append({
            "field": "measurement_design",
            "code": (
                "MEASUREMENT_DESIGN_REQUIRED"
            ),
        })
    else:
        measurement_type = (
            measurement_design.get(
                "measurement_type"
            )
        )

        if (
            is_constructor_definition
            and development_status in {
                "trial",
                "active",
            }
            and measurement_type
            not in SUPPORTED_MEASUREMENT_TYPES
        ):
            errors.append({
                "field": (
                    "measurement_design."
                    "measurement_type"
                ),
                "code": (
                    "SUPPORTED_MEASUREMENT_TYPE_REQUIRED"
                ),
                "value": measurement_type,
            })

        if (
            is_constructor_definition
            and development_status in {"trial", "active"}
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
                    "code": "PARAMETER_CATEGORY_REQUIRED",
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
                errors.append({
                    "field": "authorship",
                    "code": "AUTHORSHIP_REQUIRED",
                })
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

            measurement_nodes = measurement_design.get("measurement_nodes")
            if current_constructor_contract and (
                not isinstance(measurement_nodes, list) or not measurement_nodes
            ):
                errors.append({
                    "field": "measurement_design.measurement_nodes",
                    "code": "MEASUREMENT_NODE_REQUIRED",
                })
                measurement_nodes = []
            elif not isinstance(measurement_nodes, list):
                measurement_nodes = []

            node_codes = (
                []
                if current_constructor_contract
                else list(measurement_design.get("required_input_roles") or [])
                + list(measurement_design.get("optional_input_roles") or [])
            )
            for index, node in enumerate(measurement_nodes):
                if not isinstance(node, dict):
                    errors.append({
                        "field": f"measurement_design.measurement_nodes.{index}",
                        "code": "MEASUREMENT_NODE_MUST_BE_OBJECT",
                    })
                    continue
                node_code = str(node.get("node_code") or "").strip()
                if not node_code:
                    errors.append({
                        "field": f"measurement_design.measurement_nodes.{index}.node_code",
                        "code": "MEASUREMENT_NODE_CODE_REQUIRED",
                    })
                else:
                    node_codes.append(node_code)
                for field_name in ("question_or_variable", "source_type", "instrument"):
                    if not str(node.get(field_name) or "").strip():
                        errors.append({
                            "field": f"measurement_design.measurement_nodes.{index}.{field_name}",
                            "code": "MEASUREMENT_NODE_FIELD_REQUIRED",
                        })
                if node.get("source_type") == "questionnaire":
                    question_reference = node.get("question_reference")
                    if not isinstance(question_reference, dict):
                        errors.append({
                            "field": f"measurement_design.measurement_nodes.{index}.question_reference",
                            "code": "REGISTERED_QUESTION_REFERENCE_REQUIRED",
                        })
                    else:
                        for reference_field in (
                            "bank_id", "question_id", "question_code", "question_version", "language",
                        ):
                            if question_reference.get(reference_field) in (None, ""):
                                errors.append({
                                    "field": f"measurement_design.measurement_nodes.{index}.question_reference.{reference_field}",
                                    "code": "QUESTION_REFERENCE_FIELD_REQUIRED",
                                })
                        if question_reference.get("scale_type") != node.get("scale_type"):
                            errors.append({
                                "field": f"measurement_design.measurement_nodes.{index}.question_reference.scale_type",
                                "code": "QUESTION_NODE_SCALE_MISMATCH",
                            })
                node_scale = node.get("scale_type")
                if node_scale and get_scale_definition(node_scale) is None:
                    errors.append({
                        "field": f"measurement_design.measurement_nodes.{index}.scale_type",
                        "code": "REGISTERED_MEASUREMENT_SCALE_REQUIRED_WHEN_BOUND",
                    })

            dependency_nodes = (
                (definition.get("dependency_design") or {}).get("dependencies")
                or []
            )
            for index, node in enumerate(dependency_nodes):
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
                if node.get("role") not in {"input", "modifier", "context", "validation"}:
                    errors.append({
                        "field": f"dependency_design.dependencies.{index}.role",
                        "code": "UNSUPPORTED_DEPENDENCY_ROLE",
                    })

            if len(node_codes) != len(set(node_codes)):
                errors.append({
                    "field": "calculation_design.components",
                    "code": "DUPLICATE_NODE_CODE",
                })

            calculation_design = definition.get("calculation_design") or {}
            formula_components = calculation_design.get("components") or []
            unknown_components = [
                code for code in formula_components if code not in set(node_codes)
            ]
            if unknown_components:
                errors.append({
                    "field": "calculation_design.components",
                    "code": "UNKNOWN_FORMULA_NODE_REFERENCE",
                    "values": unknown_components,
                })
            weights = calculation_design.get("weights") or []
            if weights and len(weights) != len(formula_components):
                errors.append({
                    "field": "calculation_design.weights",
                    "code": "FORMULA_WEIGHT_COUNT_MISMATCH",
                })

            calculation_bindings = []
            for node in measurement_nodes:
                if not isinstance(node, dict):
                    continue
                question_reference = node.get("question_reference") or {}
                calculation_bindings.append({
                    "question_code": (
                        question_reference.get("question_code")
                        or node.get("node_code")
                    ),
                    "scale_type": (
                        question_reference.get("scale_type")
                        or node.get("scale_type")
                    ),
                })
            for node in dependency_nodes:
                if isinstance(node, dict) and node.get("node_code") in formula_components:
                    calculation_bindings.append({
                        "question_code": node.get("node_code"),
                        "scale_type": node.get("scale_type"),
                    })

            selected_bindings = [
                binding for binding in calculation_bindings
                if binding.get("question_code") in formula_components
            ]
            if current_constructor_contract:
                calculation_validation = validate_calculation_selection(
                    operation_id=str(calculation_design.get("operator") or ""),
                    question_bindings=selected_bindings,
                    configuration=calculation_design.get("configuration") or {},
                    repeated_measurements=bool(
                        int((definition.get("temporal_design") or {}).get("minimum_observation_count") or 1) > 1
                    ),
                    ordered_measurements=bool(
                        (definition.get("temporal_design") or {}).get("ordering_required")
                    ),
                    output_scale_type=definition.get("scale_type"),
                )
                for calculation_error in calculation_validation.get("errors", []):
                    errors.append({
                        "field": "calculation_design",
                        **calculation_error,
                    })

            markers = (definition.get("marker_validation") or {}).get("markers") or []
            marker_codes = {
                str(marker.get("node_code") or "").strip()
                for marker in markers
                if isinstance(marker, dict)
            }
            if marker_codes.intersection(formula_components):
                errors.append({
                    "field": "marker_validation.markers",
                    "code": "MARKER_MUST_NOT_ENTER_PARAMETER_FORMULA",
                })
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
                if development_status == "active" and marker_status != "active":
                    errors.append({
                        "field": f"marker_validation.markers.{marker_index}.marker_reference.development_status",
                        "code": "ACTIVE_PARAMETER_REQUIRES_ACTIVE_MARKER",
                    })
                if reference.get("scale_type") and get_scale_definition(
                    reference.get("scale_type")
                ) is None:
                    errors.append({
                        "field": f"marker_validation.markers.{marker_index}.marker_reference.scale_type",
                        "code": "REGISTERED_MARKER_SCALE_REQUIRED",
                    })

    temporal_design = definition.get(
        "temporal_design"
    )

    if not isinstance(
        temporal_design,
        dict,
    ):
        errors.append({
            "field": "temporal_design",
            "code": (
                "TEMPORAL_DESIGN_REQUIRED"
            ),
        })
    else:
        time_roles = temporal_design.get(
            "time_roles",
            [],
        )

        if not isinstance(time_roles, list):
            errors.append({
                "field": (
                    "temporal_design.time_roles"
                ),
                "code": (
                    "TIME_ROLES_MUST_BE_LIST"
                ),
            })
        else:
            unsupported_time_roles = [
                role
                for role in time_roles
                if role
                not in SUPPORTED_TIME_ROLES
            ]

            if unsupported_time_roles:
                errors.append({
                    "field": (
                        "temporal_design.time_roles"
                    ),
                    "code": (
                        "UNSUPPORTED_TIME_ROLE"
                    ),
                    "values": (
                        unsupported_time_roles
                    ),
                })

        temporal_aggregation = (
            temporal_design.get(
                "aggregation"
            )
        )

        if temporal_aggregation not in (
            SUPPORTED_TEMPORAL_AGGREGATIONS
        ):
            errors.append({
                "field": (
                    "temporal_design.aggregation"
                ),
                "code": (
                    "UNSUPPORTED_TEMPORAL_AGGREGATION"
                ),
                "value": temporal_aggregation,
            })

        if (
            temporal_design.get(
                "global_time_reference_required"
            )
            is not True
        ):
            errors.append({
                "field": (
                    "temporal_design."
                    "global_time_reference_required"
                ),
                "code": (
                    "GLOBAL_TIME_REFERENCE_REQUIRED"
                ),
            })

        global_time_scale = temporal_design.get("global_time_scale") or {}
        if global_time_scale.get("scale_type") != "datetime":
            errors.append({
                "field": "temporal_design.global_time_scale.scale_type",
                "code": "GLOBAL_TIME_SCALE_MUST_BE_DATETIME",
            })
        elif global_time_scale.get("scale_reference") != build_scale_reference("datetime"):
            errors.append({
                "field": "temporal_design.global_time_scale.scale_reference",
                "code": "GLOBAL_TIME_SCALE_REFERENCE_MISMATCH",
            })

        time_scale = temporal_design.get("time_scale") or {}
        time_scale_type = time_scale.get("scale_type")
        registered_time_scale = get_scale_definition(time_scale_type)
        if time_scale_type is None and is_constructor_definition:
            warnings.append({
                "field": "temporal_design.time_scale.scale_type",
                "code": "CONSTRUCT_TIME_SCALE_NOT_BOUND",
                "global_time_binding": "datetime_utc_remains_required",
            })
        elif registered_time_scale is None:
            errors.append({
                "field": "temporal_design.time_scale.scale_type",
                "code": "REGISTERED_TIME_SCALE_REQUIRED_WHEN_BOUND",
            })
        elif not registered_time_scale.get("temporal_roles"):
            errors.append({
                "field": "temporal_design.time_scale.scale_type",
                "code": "TEMPORAL_ROLE_CAPABLE_SCALE_REQUIRED",
            })
        else:
            if time_scale.get("scale_reference") != build_scale_reference(
                time_scale.get("scale_type")
            ):
                errors.append({
                    "field": "temporal_design.time_scale.scale_reference",
                    "code": "TIME_SCALE_REFERENCE_MISMATCH",
                })
            role_aliases = {"recency": "duration", "persistence": "duration"}
            unsupported_roles = [
                role for role in time_roles
                if role_aliases.get(role, role)
                not in registered_time_scale.get("temporal_roles", [])
            ]
            if unsupported_roles:
                errors.append({
                    "field": "temporal_design.time_scale.scale_type",
                    "code": "TIME_SCALE_ROLE_MISMATCH",
                    "time_roles": unsupported_roles,
                    "scale_type": time_scale.get("scale_type"),
                })

        if (
            is_constructor_definition
            and development_status in {"trial", "active"}
            and not str(temporal_design.get("temporal_meaning") or "").strip()
        ):
            errors.append({
                "field": "temporal_design.temporal_meaning",
                "code": "TEMPORAL_MEANING_REQUIRED",
            })

    scaling = definition.get("scaling")

    if not isinstance(scaling, dict):
        errors.append({
            "field": "scaling",
            "code": "SCALING_OBJECT_REQUIRED",
        })
    else:
        output_transformation = (
            scaling.get(
                "output_transformation"
            )
            or {}
        )

        transformation_type = (
            output_transformation.get(
                "type"
            )
        )

        if transformation_type not in (
            SUPPORTED_TRANSFORMATION_TYPES
        ):
            errors.append({
                "field": (
                    "scaling."
                    "output_transformation.type"
                ),
                "code": (
                    "UNSUPPORTED_TRANSFORMATION_TYPE"
                ),
                "value": transformation_type,
            })

    feedback = definition.get("feedback")

    if not isinstance(feedback, dict):
        errors.append({
            "field": "feedback",
            "code": (
                "FEEDBACK_OBJECT_REQUIRED"
            ),
        })
    else:
        feedback_status = feedback.get(
            "feedback_status"
        )

        if feedback_status not in (
            SUPPORTED_FEEDBACK_STATUSES
        ):
            errors.append({
                "field": (
                    "feedback.feedback_status"
                ),
                "code": (
                    "UNSUPPORTED_FEEDBACK_STATUS"
                ),
                "value": feedback_status,
            })

    marker_validation = definition.get(
        "marker_validation"
    )

    if not isinstance(
        marker_validation,
        dict,
    ):
        errors.append({
            "field": "marker_validation",
            "code": (
                "MARKER_VALIDATION_OBJECT_REQUIRED"
            ),
        })
    elif (
        marker_validation.get(
            "included_in_parameter_value"
        )
        is True
    ):
        warnings.append({
            "field": (
                "marker_validation."
                "included_in_parameter_value"
            ),
            "code": (
                "MARKERS_INCLUDED_IN_PARAMETER_REVIEW"
            ),
        })

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }
def _multilingual_text(
    value: Any = None,
) -> dict:
    if isinstance(value, dict):
        return {
            "ru": str(
                value.get("ru") or ""
            ),
            "en": str(
                value.get("en") or ""
            ),
            "es": str(
                value.get("es") or ""
            ),
        }

    if value is None:
        text = ""
    else:
        text = str(value)

    return {
        "ru": text,
        "en": text,
        "es": text,
    }

def normalize_model_parameter_definition(
    definition: dict,
    *,
    definition_source: str,
) -> dict:
    normalized = deepcopy(definition)

    parameter_code = _clean_parameter_code(
        normalized.get("parameter_code")
    )

    normalized["parameter_code"] = parameter_code

    normalized.setdefault(
        "parameter_id",
        _stable_parameter_id(parameter_code),
    )

    normalized.setdefault(
        "schema_version",
        MODEL_PARAMETER_DEFINITION_SCHEMA_VERSION,
    )

    normalized.setdefault(
        "registry_schema_version",
        MODEL_PARAMETER_REGISTRY_SCHEMA_VERSION,
    )

    normalized.setdefault(
        "definition_version",
        1,
    )

    lifecycle_status = (
        normalized.get(
            "lifecycle_status"
        )
        or normalized.get("status")
        or "draft"
    )

    normalized[
        "lifecycle_status"
    ] = lifecycle_status

    normalized[
        "scientific_status"
    ] = (
        normalized.get(
            "scientific_status"
        )
        or "proposed"
    )

    development_status = (
        normalized.get(
            "development_status"
        )
    )

    if development_status == "developing":
        development_status = "draft"

    if not development_status:
        if lifecycle_status == "draft":
            development_status = "draft"
        else:
            development_status = "active"

    normalized[
        "development_status"
    ] = development_status
    
    if development_status == "draft":
        normalized[
            "lifecycle_status"
        ] = "draft"

    elif development_status in {
        "trial",
        "active",
    }:
        normalized[
            "lifecycle_status"
        ] = "active"

    # Временная обратная совместимость.
    normalized["status"] = (
        normalized[
            "lifecycle_status"
        ]
    )

    normalized["definition_source"] = (
        definition_source
    )

    scale_type = normalize_scale_id(
        normalized.get("scale_type")
    )
    normalized["scale_type"] = scale_type
    normalized["scale_reference"] = (
        build_scale_reference(scale_type)
        if scale_type in SUPPORTED_SCALE_TYPES
        and scale_type is not None
        else None
    )
    normalized["scale_binding_status"] = (
        "registered" if normalized["scale_reference"] is not None
        else "unbound"
    )

    normalized["title"] = _multilingual_text(
        normalized.get("title")
        or {
            "ru": parameter_code,
            "en": parameter_code,
            "es": parameter_code,
        }
    )

    normalized.setdefault(
        "parameter_role",
        "model_output",
    )

    normalized.setdefault("value_schema", {
        "minimum": None,
        "maximum": None,
        "unit": None,
        "allowed_values": None,
        "ordered_values": None,
        "components": None,
    })

    normalized.setdefault("missing_semantics", {
        "unknown_is_zero": False,
        "not_enough_data_allowed": True,
        "not_applicable_allowed": True,
        "missing_value": None,
    })

    normalized.setdefault("research", {
        "available": False,
        "allowed_analysis_roles": [],
    })

    meaning = normalized.get(
        "meaning"
    )

    if not isinstance(meaning, dict):
        meaning = {}

    meaning[
        "construct_definition"
    ] = _multilingual_text(
        meaning.get(
            "construct_definition"
        )
    )

    meaning[
        "what_is_represented"
    ] = _multilingual_text(
        meaning.get(
            "what_is_represented"
        )
    )

    meaning[
        "what_is_not_represented"
    ] = _multilingual_text(
        meaning.get(
            "what_is_not_represented"
        )
    )

    meaning[
        "scientific_hypothesis"
    ] = _multilingual_text(
        meaning.get(
            "scientific_hypothesis"
        )
    )

    meaning.setdefault(
        "activation_conditions",
        [],
    )

    meaning.setdefault(
        "non_activation_conditions",
        [],
    )

    meaning.setdefault(
        "unit_of_analysis",
        None,
    )

    normalized["meaning"] = meaning

    measurement_design = normalized.get(
        "measurement_design"
    )

    if not isinstance(
        measurement_design,
        dict,
    ):
        measurement_design = {}

    measurement_design.setdefault(
        "measurement_type",
        None,
    )

    measurement_design.setdefault(
        "semantic_components",
        [],
    )

    measurement_design.setdefault(
        "required_input_roles",
        [],
    )

    measurement_design.setdefault(
        "optional_input_roles",
        [],
    )

    measurement_design.setdefault(
        "minimum_required_inputs",
        None,
    )

    normalized[
        "measurement_design"
    ] = measurement_design

    question_input_mappings = (
        normalized.get(
            "question_input_mappings"
        )
    )

    if not isinstance(
        question_input_mappings,
        list,
    ):
        question_input_mappings = []

    normalized[
        "question_input_mappings"
    ] = question_input_mappings

    output_scale = normalized.get(
        "output_scale"
    )

    if not isinstance(output_scale, dict):
        output_scale = {}

    output_scale.setdefault(
        "scale_type",
        normalized.get(
            "scale_type"
        ),
    )
    output_scale["binding_status"] = (
        "registered" if normalized.get("scale_reference") is not None
        else "unbound"
    )
    output_scale["scale_reference"] = normalized.get("scale_reference")

    output_scale.setdefault(
        "value_type",
        normalized.get(
            "value_type"
        ),
    )

    current_value_schema = (
        normalized.get(
            "value_schema"
        )
        or {}
    )

    output_scale.setdefault(
        "minimum",
        current_value_schema.get(
            "minimum"
        ),
    )

    output_scale.setdefault(
        "maximum",
        current_value_schema.get(
            "maximum"
        ),
    )

    output_scale.setdefault(
        "unit",
        current_value_schema.get(
            "unit"
        ),
    )

    output_scale.setdefault(
        "precision",
        None,
    )

    output_scale.setdefault(
        "score_direction",
        normalized.get(
            "score_direction"
        ),
    )

    normalized["output_scale"] = (
        output_scale
    )

    scaling = normalized.get("scaling")

    if not isinstance(scaling, dict):
        scaling = {}

    scaling.setdefault(
        "input_normalization",
        "per_input_mapping",
    )

    scaling.setdefault(
        "aggregation_scale",
        {
            "minimum": None,
            "maximum": None,
        },
    )

    scaling.setdefault(
        "output_transformation",
        {
            "type": "identity",
            "source_minimum": None,
            "source_maximum": None,
            "target_minimum": (
                output_scale.get(
                    "minimum"
                )
            ),
            "target_maximum": (
                output_scale.get(
                    "maximum"
                )
            ),
            "clamp": False,
        },
    )

    normalized["scaling"] = scaling

    temporal_design = normalized.get(
        "temporal_design"
    )

    if not isinstance(
        temporal_design,
        dict,
    ):
        temporal_design = {}

    temporal_design.setdefault(
        "time_dependent",
        False,
    )

    temporal_design.setdefault(
        "time_roles",
        [],
    )

    temporal_design.setdefault(
        "observation_time_required",
        True,
    )

    temporal_design.setdefault(
        "global_time_reference_required",
        True,
    )

    temporal_design.setdefault(
        "time_variable_codes",
        [],
    )

    temporal_design.setdefault(
        "time_window",
        {
            "type": None,
            "value": None,
            "unit": None,
        },
    )

    temporal_design.setdefault(
        "aggregation",
        "single_observation",
    )

    temporal_design.setdefault(
        "minimum_observation_count",
        1,
    )

    temporal_design.setdefault(
        "ordering_required",
        False,
    )

    temporal_design.setdefault(
        "time_zone_policy",
        "global_time_reference",
    )

    # Every observation is anchored to the same absolute time scale.
    # A separate time scale may describe duration, latency, frequency, etc.
    temporal_design["global_time_scale"] = {
        "scale_type": "datetime",
        "scale_reference": build_scale_reference("datetime"),
        "role": "global_time_reference",
        "timezone_required": True,
        "synchronization_reference_required": True,
    }

    time_scale = temporal_design.get("time_scale")
    if not isinstance(time_scale, dict):
        time_scale = {}
    time_scale_code = time_scale.get("scale_type")
    if time_scale_code is None and definition_source != "constructor":
        time_scale_code = "datetime"
    time_scale["scale_type"] = time_scale_code
    time_scale["scale_reference"] = (
        build_scale_reference(time_scale_code)
        if time_scale_code is not None
        and time_scale_code in SUPPORTED_SCALE_TYPES
        else None
    )
    time_scale["binding_status"] = (
        "registered" if time_scale["scale_reference"] is not None
        else "unbound"
    )
    temporal_design["time_scale"] = time_scale

    temporal_design.setdefault(
        "missing_time_semantics",
        "not_enough_data",
    )

    normalized[
        "temporal_design"
    ] = temporal_design

    calculation_design = normalized.get(
        "calculation_design"
    )

    if not isinstance(
        calculation_design,
        dict,
    ):
        calculation_design = {}

    calculation_design.setdefault(
        "calculation_mode",
        "existing_calculator_output",
    )

    calculation_design.setdefault(
        "expression_schema_version",
        None,
    )

    calculation_design.setdefault(
        "components",
        [],
    )

    calculation_design.setdefault(
        "expression",
        None,
    )

    calculation_design.setdefault(
        "missing_data_rule",
        {
            "unknown_is_zero": False,
            "minimum_required_inputs": None,
            "on_insufficient_data": (
                "not_enough_data"
            ),
        },
    )

    normalized[
        "calculation_design"
    ] = calculation_design

    marker_validation = normalized.get(
        "marker_validation"
    )

    if not isinstance(
        marker_validation,
        dict,
    ):
        marker_validation = {}

    marker_validation.setdefault(
        "included_in_parameter_value",
        False,
    )

    marker_validation.setdefault(
        "marker_mappings",
        [],
    )

    marker_validation.setdefault(
        "confirmation_rule",
        None,
    )

    marker_validation.setdefault(
        "disconfirmation_rule",
        None,
    )

    normalized[
        "marker_validation"
    ] = marker_validation

    feedback = normalized.get(
        "feedback"
    )

    if not isinstance(feedback, dict):
        feedback = {}

    feedback.setdefault(
        "feedback_status",
        "not_evaluated",
    )

    feedback.setdefault(
        "evidence_count",
        0,
    )

    feedback.setdefault(
        "participant_count",
        0,
    )

    feedback.setdefault(
        "measurement_count",
        0,
    )

    feedback.setdefault(
        "component_contributions",
        [],
    )

    feedback.setdefault(
        "uncertainty",
        {
            "estimate": None,
            "interval_lower": None,
            "interval_upper": None,
            "confidence_level": None,
            "method_id": None,
        },
    )

    feedback.setdefault(
        "last_evaluated_at",
        None,
    )

    feedback.setdefault(
        "evidence_result_ids",
        [],
    )

    feedback.setdefault(
        "human_review_required",
        True,
    )

    normalized["feedback"] = feedback

    mechanism_compatibility = (
        normalized.get(
            "mechanism_compatibility"
        )
    )

    if not isinstance(
        mechanism_compatibility,
        dict,
    ):
        mechanism_compatibility = {}

    mechanism_compatibility.setdefault(
        "available_as_component",
        True,
    )

    mechanism_compatibility.setdefault(
        "allowed_component_roles",
        [
            "input",
            "modifier",
            "protective_factor",
            "blocking_condition",
            "marker",
        ],
    )

    normalized[
        "mechanism_compatibility"
    ] = mechanism_compatibility

    provenance = normalized.get(
        "provenance"
    )

    if not isinstance(provenance, dict):
        provenance = {}

    if definition_source == "built_in":
        provenance.setdefault(
            "creation_mode",
            "human_ai_collaboration",
        )
        provenance.setdefault(
            "human_lead",
            {
                "name": "Marina Boronenko",
                "roles": [
                    "scientific_author",
                    "system_architect",
                    "project_lead",
                ],
            },
        )
        provenance.setdefault(
            "ai_collaborators",
            [
                {
                    "name": "Ray",
                    "role": (
                        "AI research and "
                        "engineering colleague"
                    ),
                    "contribution_types": [
                        "architecture",
                        "implementation_support",
                        "scientific_structuring",
                        "validation_design",
                    ],
                }
            ],
        )
    else:
        provenance.setdefault("creation_mode", "constructor")

    normalized["provenance"] = provenance

    return normalized


def list_model_parameter_definitions(
    *,
    include_inactive: bool = False,
    include_all_versions: bool = False,
) -> list[dict]:
    definitions_by_identity: dict[
        tuple[str, int],
        dict,
    ] = {}

    for (
        parameter_code,
        definition,
    ) in (
        BUILT_IN_MODEL_PARAMETER_DEFINITIONS.items()
    ):
        normalized = (
            normalize_model_parameter_definition(
                definition,
                definition_source="built_in",
            )
        )

        identity = (
            parameter_code,
            _definition_version(
                normalized
            ),
        )

        definitions_by_identity[
            identity
        ] = normalized

    for raw_definition in (
        _load_custom_definitions_raw()
    ):
        normalized = (
            normalize_model_parameter_definition(
                raw_definition,
                definition_source="constructor",
            )
        )

        validation = (
            validate_model_parameter_definition(
                normalized
            )
        )

        normalized[
            "definition_validation"
        ] = validation

        parameter_code = normalized.get(
            "parameter_code"
        )

        if not parameter_code:
            continue

        identity = (
            parameter_code,
            _definition_version(
                normalized
            ),
        )

        # Конструктор может содержать новую версию
        # встроенного параметра, но не уничтожает
        # предыдущую версию.
        definitions_by_identity[
            identity
        ] = normalized

    definitions = list(
        definitions_by_identity.values()
    )

    if not include_inactive:
        definitions = [
            definition
            for definition in definitions
            if (
                _definition_lifecycle_status(
                    definition
                )
                == "active"
            )
        ]

    if include_all_versions:
        return sorted(
            definitions,
            key=lambda definition: (
                str(
                    definition.get(
                        "parameter_code"
                    )
                    or ""
                ),
                _definition_version(
                    definition
                ),
            ),
        )

    latest_by_code: dict[
        str,
        dict,
    ] = {}

    for definition in definitions:
        parameter_code = str(
            definition.get(
                "parameter_code"
            )
            or ""
        )

        if not parameter_code:
            continue

        previous = latest_by_code.get(
            parameter_code
        )

        if (
            previous is None
            or _definition_version(
                definition
            )
            > _definition_version(
                previous
            )
        ):
            latest_by_code[
                parameter_code
            ] = definition

    return sorted(
        latest_by_code.values(),
        key=lambda definition: (
            str(
                definition.get(
                    "parameter_code"
                )
                or ""
            )
        ),
    )


def get_model_parameter_definition(
    parameter_code: str,
    *,
    definition_version: int | None = None,
    include_inactive: bool = False,
) -> dict | None:
    normalized_code = (
        _clean_parameter_code(
            parameter_code
        )
    )

    definitions = (
        list_model_parameter_definitions(
            include_inactive=(
                include_inactive
            ),
            include_all_versions=True,
        )
    )

    matching = [
        definition
        for definition in definitions
        if (
            definition.get(
                "parameter_code"
            )
            == normalized_code
        )
    ]

    if definition_version is not None:
        for definition in matching:
            if (
                _definition_version(
                    definition
                )
                == int(
                    definition_version
                )
            ):
                return definition

        return None

    if not matching:
        return None

    return max(
        matching,
        key=_definition_version,
    )


def save_custom_model_parameter_definition(
    definition: dict,
) -> dict:
    normalized = (
        normalize_model_parameter_definition(
            definition,
            definition_source="constructor",
        )
    )

    validation = (
        validate_model_parameter_definition(
            normalized
        )
    )

    if validation["valid"] is not True:
        return {
            "ok": False,
            "status": "definition_invalid",
            "validation": validation,
            "definition": normalized,
        }

    parameter_code = normalized[
        "parameter_code"
    ]

    incoming_version = (
        _definition_version(
            normalized
        )
    )

    all_existing_definitions = (
        list_model_parameter_definitions(
            include_inactive=True,
            include_all_versions=True,
        )
    )

    matching_existing = [
        item
        for item
        in all_existing_definitions
        if (
            _clean_parameter_code(
                item.get(
                    "parameter_code"
                )
            )
            == parameter_code
        )
    ]

    existing_versions = {
        _definition_version(item)
        for item in matching_existing
    }

    if incoming_version in existing_versions:
        return {
            "ok": False,
            "status": (
                "definition_version_already_exists"
            ),
            "parameter_code": parameter_code,
            "definition_version": (
                incoming_version
            ),
            "existing_versions": sorted(
                existing_versions
            ),
        }

    if existing_versions:
        maximum_existing_version = max(
            existing_versions
        )

        if (
            incoming_version
            <= maximum_existing_version
        ):
            return {
                "ok": False,
                "status": (
                    "definition_version_must_increase"
                ),
                "parameter_code": (
                    parameter_code
                ),
                "maximum_existing_version": (
                    maximum_existing_version
                ),
                "incoming_definition_version": (
                    incoming_version
                ),
            }

    custom_definitions = (
        _load_custom_definitions_raw()
    )

    # Важно: старые версии не удаляются.
    custom_definitions.append(
        normalized
    )

    _save_custom_definitions_raw(
        custom_definitions
    )

    return {
        "ok": True,
        "status": "saved_new_version",
        "definition": normalized,
        "validation": validation,
        "previous_versions": sorted(
            existing_versions
        ),
    }


def upsert_custom_model_parameter_draft(
    definition: dict,
) -> dict:
    incoming = deepcopy(definition)
    parameter_code = _clean_parameter_code(
        incoming.get("parameter_code")
    )

    if not parameter_code:
        return {
            "ok": False,
            "status": "parameter_code_required",
        }

    all_definitions = list_model_parameter_definitions(
        include_inactive=True,
        include_all_versions=True,
    )
    matching = [
        item
        for item in all_definitions
        if item.get("parameter_code") == parameter_code
    ]
    existing_versions = {
        _definition_version(item)
        for item in matching
    }

    requested_version = incoming.get("definition_version")
    if requested_version is None:
        editable_drafts = [
            item
            for item in matching
            if item.get("definition_source") == "constructor"
            and _definition_development_status(item) == "draft"
        ]
        if editable_drafts:
            requested_version = max(
                _definition_version(item)
                for item in editable_drafts
            )
        else:
            requested_version = (
                max(existing_versions, default=0) + 1
            )

    incoming["definition_version"] = int(requested_version)
    incoming["development_status"] = "draft"
    incoming["lifecycle_status"] = "draft"
    incoming["status"] = "draft"

    normalized = normalize_model_parameter_definition(
        incoming,
        definition_source="constructor",
    )
    validation = validate_model_parameter_definition(
        normalized
    )
    if not validation["valid"]:
        return {
            "ok": False,
            "status": "definition_invalid",
            "validation": validation,
            "definition": normalized,
        }

    custom_definitions = _load_custom_definitions_raw()
    replaced = False
    updated_definitions = []

    for raw in custom_definitions:
        raw_code = _clean_parameter_code(
            raw.get("parameter_code")
        )
        raw_version = _definition_version(raw)
        if (
            raw_code == parameter_code
            and raw_version == int(requested_version)
        ):
            raw_normalized = normalize_model_parameter_definition(
                raw,
                definition_source="constructor",
            )
            if _definition_development_status(raw_normalized) != "draft":
                return {
                    "ok": False,
                    "status": "immutable_non_draft_version",
                    "parameter_code": parameter_code,
                    "definition_version": int(requested_version),
                }
            updated_definitions.append(normalized)
            replaced = True
        else:
            updated_definitions.append(raw)

    if not replaced:
        if int(requested_version) in existing_versions:
            return {
                "ok": False,
                "status": "definition_version_already_exists",
                "parameter_code": parameter_code,
                "definition_version": int(requested_version),
            }
        updated_definitions.append(normalized)

    _save_custom_definitions_raw(updated_definitions)
    return {
        "ok": True,
        "status": "draft_updated" if replaced else "draft_created",
        "definition": normalized,
        "validation": validation,
    }


def transition_custom_model_parameter_definition(
    parameter_code: str,
    definition_version: int,
    target_status: str,
) -> dict:
    transitions = {
        "draft": {"trial"},
        "trial": {"active"},
    }
    if target_status not in {"trial", "active"}:
        return {"ok": False, "status": "unsupported_target_status"}

    custom_definitions = _load_custom_definitions_raw()
    updated = []
    selected = None

    for raw in custom_definitions:
        if (
            _clean_parameter_code(raw.get("parameter_code"))
            == _clean_parameter_code(parameter_code)
            and _definition_version(raw) == int(definition_version)
        ):
            selected = normalize_model_parameter_definition(
                raw,
                definition_source="constructor",
            )
            current = _definition_development_status(selected)
            if target_status not in transitions.get(current, set()):
                return {
                    "ok": False,
                    "status": "invalid_status_transition",
                    "current_status": current,
                    "target_status": target_status,
                }
            selected["development_status"] = target_status
            selected["lifecycle_status"] = "active"
            selected["status"] = "active"
            validation = validate_model_parameter_definition(selected)
            if not validation["valid"]:
                return {
                    "ok": False,
                    "status": "transition_validation_failed",
                    "validation": validation,
                    "definition": selected,
                }
            updated.append(selected)
        else:
            updated.append(raw)

    if selected is None:
        return {"ok": False, "status": "definition_not_found"}

    _save_custom_definitions_raw(updated)
    return {
        "ok": True,
        "status": f"transitioned_to_{target_status}",
        "definition": selected,
    }


def delete_custom_model_parameter_draft(
    parameter_code: str,
    definition_version: int,
) -> dict:
    custom_definitions = _load_custom_definitions_raw()
    kept = []
    deleted = None

    for raw in custom_definitions:
        matches = (
            _clean_parameter_code(raw.get("parameter_code"))
            == _clean_parameter_code(parameter_code)
            and _definition_version(raw) == int(definition_version)
        )
        if not matches:
            kept.append(raw)
            continue

        normalized = normalize_model_parameter_definition(
            raw,
            definition_source="constructor",
        )
        if _definition_development_status(normalized) != "draft":
            return {
                "ok": False,
                "status": "only_draft_can_be_deleted",
            }
        deleted = normalized

    if deleted is None:
        return {"ok": False, "status": "definition_not_found"}

    _save_custom_definitions_raw(kept)
    return {
        "ok": True,
        "status": "draft_deleted",
        "definition": deleted,
        "calculation_cleanup": {
            "performed": False,
            "reason": (
                "model calculation runs do not yet carry "
                "parameter definition_version; deleting by "
                "parameter_code alone would be unsafe"
            ),
        },
    }


def build_model_parameter_registry() -> dict:
    definitions = (
        list_model_parameter_definitions(
            include_inactive=True,
            include_all_versions=True,
        )
    )

    validation_results = []

    for definition in definitions:
        validation_results.append({
            "parameter_code": definition.get(
                "parameter_code"
            ),
            "validation": (
                validate_model_parameter_definition(
                    definition
                )
            ),
        })

    return {
        "ok": all(
            result["validation"]["valid"]
            for result in validation_results
        ),
        "schema_version": (
            MODEL_PARAMETER_REGISTRY_SCHEMA_VERSION
        ),
        "definition_schema_version": (
            MODEL_PARAMETER_DEFINITION_SCHEMA_VERSION
        ),
        "supported_parameter_kinds": sorted(
            SUPPORTED_PARAMETER_KINDS
        ),
        "supported_value_types": sorted(
            SUPPORTED_VALUE_TYPES
        ),
        "supported_scale_types": sorted(
            value
            for value in SUPPORTED_SCALE_TYPES
            if value is not None
        ),
        "supported_calculation_statuses": sorted(
            SUPPORTED_CALCULATION_STATUSES
        ),

        "supported_lifecycle_statuses": sorted(
            SUPPORTED_LIFECYCLE_STATUSES
        ),

        "supported_scientific_statuses": sorted(
            SUPPORTED_SCIENTIFIC_STATUSES
        ),
        
        "supported_development_statuses": sorted(
            SUPPORTED_DEVELOPMENT_STATUSES
        ),
        
        "supported_interface_languages": sorted(
            SUPPORTED_INTERFACE_LANGUAGES
        ),

        "supported_measurement_types": sorted(
            SUPPORTED_MEASUREMENT_TYPES
        ),

        "supported_time_roles": sorted(
            SUPPORTED_TIME_ROLES
        ),

        "supported_temporal_aggregations": sorted(
            SUPPORTED_TEMPORAL_AGGREGATIONS
        ),

        "supported_transformation_types": sorted(
            SUPPORTED_TRANSFORMATION_TYPES
        ),

        "supported_feedback_statuses": sorted(
            SUPPORTED_FEEDBACK_STATUSES
        ),
        
    "definition_count": len(definitions),
    "definitions": definitions,
    "validation_results": validation_results,
    "custom_definitions_path": str(
        CUSTOM_PARAMETER_DEFINITIONS_PATH
    ),
}
