from __future__ import annotations

from copy import deepcopy


MODEL_ENTITY_CLASSIFICATION_SCHEMA_VERSION = "health-model-entity-classification-1"

MODEL_PARAMETER = "model_parameter"
LOGIC_ENTITY = "logic_entity"

LOGIC_CLASSIFICATIONS = {
    "forecast_allowed": {
        "entity_subtype": "decision_signal",
        "human_description": {
            "ru": "Управляющий сигнал: разрешает или запрещает построение прогноза.",
            "en": "Control signal that allows or blocks forecast generation.",
            "es": "Señal de control que permite o bloquea la generación del pronóstico.",
        },
    },
    "readiness_status": {
        "entity_subtype": "readiness_signal",
        "human_description": {
            "ru": "Состояние готовности вычислительного процесса к следующему этапу.",
            "en": "Readiness state of the calculation process for its next stage.",
            "es": "Estado de preparación del proceso de cálculo para la siguiente etapa.",
        },
    },
    "current_state.mode": {
        "entity_subtype": "interpretation_mode",
        "human_description": {
            "ru": "Режим, который определяет, как система интерпретирует текущее состояние.",
            "en": "Mode controlling how the system interprets the current state.",
            "es": "Modo que controla cómo el sistema interpreta el estado actual.",
        },
    },
    "stress_burden.critical_override_applied": {
        "entity_subtype": "audit_signal",
        "human_description": {
            "ru": "Журналируемый признак того, что критическое правило изменило обычный результат расчёта.",
            "en": "Auditable signal showing that a critical rule changed the ordinary calculation result.",
            "es": "Señal auditable de que una regla crítica cambió el resultado ordinario del cálculo.",
        },
    },
}


MODEL_SUBTYPE_BY_KIND = {
    "binary": "derived_state",
    "categorical": "derived_state",
    "structured": "composite_profile",
    "vector": "composite_profile",
    "scalar": "derived_quantity",
    "ordinal": "derived_quantity",
}


def classify_model_entity(definition: dict) -> dict:
    code = str(definition.get("parameter_code") or "")
    if code in LOGIC_CLASSIFICATIONS:
        classification = deepcopy(LOGIC_CLASSIFICATIONS[code])
        classification.update({
            "entity_class": LOGIC_ENTITY,
            "classification_source": "registered_compatibility_migration",
        })
    else:
        classification = {
            "entity_class": MODEL_PARAMETER,
            "entity_subtype": MODEL_SUBTYPE_BY_KIND.get(
                definition.get("parameter_kind"), "derived_quantity"
            ),
            "classification_source": "registered_compatibility_migration",
            "human_description": {"ru": "", "en": "", "es": ""},
        }
    if code == "critical_status.is_critical":
        classification["operational_roles"] = ["logic_condition"]
    else:
        classification.setdefault("operational_roles", [])
    return {
        "schema_version": MODEL_ENTITY_CLASSIFICATION_SCHEMA_VERSION,
        **classification,
    }


def enrich_model_entity(definition: dict) -> dict:
    enriched = deepcopy(definition)
    explicit = enriched.get("entity_classification")
    classification = (
        deepcopy(explicit)
        if isinstance(explicit, dict) and explicit.get("entity_class")
        else classify_model_entity(enriched)
    )
    enriched["entity_classification"] = classification
    return enriched


def filter_model_entities(definitions: list[dict], entity_class: str) -> list[dict]:
    return [
        enriched
        for definition in definitions
        if (enriched := enrich_model_entity(definition))["entity_classification"]["entity_class"] == entity_class
    ]
