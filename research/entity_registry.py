from __future__ import annotations

from copy import deepcopy
from typing import Any

from question_banks.QUESTION_BANK_EN import QUESTION_BANK_EN
from question_banks.QUESTION_BANK_ES import QUESTION_BANK_ES
from question_banks.QUESTION_BANK_RU import QUESTION_BANK_RU
from research.repository import load_objects


MODEL_PARAMETERS = [
    {"code": "pressure", "label": {"ru": "Давление", "en": "Pressure", "es": "Presión"}},
    {"code": "energy", "label": {"ru": "Энергия", "en": "Energy", "es": "Energía"}},
    {"code": "stability", "label": {"ru": "Устойчивость", "en": "Stability", "es": "Estabilidad"}},
]
MODEL_MECHANISMS = [
    {"code": "adaptation", "label": {"ru": "Адаптация", "en": "Adaptation", "es": "Adaptación"}},
    {"code": "compensation", "label": {"ru": "Компенсация", "en": "Compensation", "es": "Compensación"}},
]
STATISTICAL_METHODS = [
    {"code": "descriptive", "label": {"ru": "Описательная статистика", "en": "Descriptive statistics", "es": "Estadística descriptiva"}},
    {"code": "correlation", "label": {"ru": "Анализ связи (не согласованности)", "en": "Association analysis (not agreement)", "es": "Análisis de asociación (no concordancia)"}},
    {"code": "mixed_effects", "label": {"ru": "Модель смешанных эффектов", "en": "Mixed-effects model", "es": "Modelo de efectos mixtos"}},
]

REGISTERED_OBJECT_TYPES = {
    "measurement_dataset", "questionnaire_result", "parameter_result",
    "analysis_result", "image_processing_run", "model_training_run",
    "trained_model", "hypothesis", "hypothesis_result", "citation_collection",
    "measurement_instrument", "observable_marker", "model_parameter",
    "mechanism", "question_bank", "project",
}

QUALITATIVE_HYPOTHESIS_ENTITY_TYPES = {
    "qualitative_dataset", "interview_corpus", "focus_group_corpus",
    "document_corpus", "observation_record", "field_notes",
    "questionnaire_result", "measurement_dataset", "parameter_result",
    "analysis_result", "image_video_dataset", "game_result",
    "model_parameter", "mechanism", "observable_marker", "hypothesis", "hypothesis_result",
    "citation_collection", "theoretical_construct", "conceptual_framework",
}

# Technical hypotheses may use only versioned scientific objects whose role can
# be stated without pretending that an instrument definition is observed data.
TECHNICAL_HYPOTHESIS_ENTITY_TYPES = {
    "measurement_dataset", "questionnaire_result", "parameter_result",
    "analysis_result", "image_processing_run", "model_training_run",
    "trained_model", "measurement_instrument", "observable_marker",
    "model_parameter", "event_annotation", "image_video_dataset", "game_result",
}

TECHNICAL_VARIABLE_ROLES = {
    "measurement_dataset": ["outcome", "predictor", "mediator", "moderator", "confounder", "grouping"],
    "questionnaire_result": ["outcome", "predictor", "mediator", "moderator", "confounder", "grouping"],
    "parameter_result": ["outcome", "predictor", "mediator", "moderator", "confounder", "grouping"],
    "analysis_result": ["outcome", "predictor", "confounder", "grouping"],
    "image_processing_run": ["outcome", "predictor", "confounder"],
    "image_video_dataset": ["outcome", "predictor", "confounder"],
    "game_result": ["outcome", "predictor", "confounder", "grouping"],
    "event_annotation": ["outcome", "predictor", "grouping"],
    "observable_marker": ["outcome", "predictor", "mediator", "moderator", "confounder"],
    "model_parameter": ["outcome", "predictor", "mediator", "moderator", "confounder"],
    "measurement_instrument": ["outcome", "predictor"],
    "trained_model": ["predictor"],
    "model_training_run": ["predictor", "confounder"],
}

TECHNICAL_SOURCE_ROLES = {
    "measurement_dataset": ["sensor_candidate", "criterion_reference", "physical_state_anchor", "covariate"],
    "questionnaire_result": ["questionnaire_anchor", "covariate"],
    "parameter_result": ["model_parameter_anchor", "physical_state_anchor", "covariate"],
    "analysis_result": ["criterion_reference", "physical_state_anchor", "covariate"],
    "image_processing_run": ["sensor_candidate", "criterion_reference", "covariate"],
    "image_video_dataset": ["sensor_candidate", "criterion_reference", "covariate"],
    "game_result": ["physical_state_anchor", "event_annotation", "covariate"],
    "event_annotation": ["event_annotation", "criterion_reference"],
    "observable_marker": ["physical_state_anchor", "covariate"],
    "model_parameter": ["model_parameter_anchor", "covariate"],
    "measurement_instrument": ["criterion_reference"],
    "trained_model": ["criterion_reference", "covariate"],
    "model_training_run": ["covariate"],
}


def _language(value: str) -> str:
    return value if value in {"ru", "en", "es"} else "ru"


def _question_entities(language: str) -> list[dict[str, Any]]:
    banks = {"ru": QUESTION_BANK_RU, "en": QUESTION_BANK_EN, "es": QUESTION_BANK_ES}
    result = []
    for code, question in banks[language].items():
        scale_type = question.get("scale_type") or "ordinal"
        result.append({
            "id": str(question.get("question_id") or code),
            "registry_id": str(question.get("question_id") or code),
            "type": "question",
            "entity_type": "question",
            "code": code,
            "label": question.get("prompt") or code,
            "display_name": question.get("prompt") or code,
            "description": question.get("prompt") or "",
            "version": question.get("version", 1),
            "status": "active" if question.get("active", True) else "draft",
            "source": "decision_under_uncertainty_question_bank",
            "measurement_scale_ref": scale_type,
            "unit": "response_score",
            "time_contract": {"contract_version": "measurement-time-contract-1", "axis": "UTC", "event": "answer_submitted_at"},
        })
    return result


def _simple_entities(items: list[dict[str, Any]], entity_type: str, source: str, language: str) -> list[dict[str, Any]]:
    result = []
    for item in items:
        code = str(item["code"])
        label = item["label"].get(language) or item["label"]["en"]
        result.append({
            "id": f"{entity_type}:{code}", "registry_id": f"{entity_type}:{code}",
            "type": entity_type, "entity_type": entity_type, "code": code,
            "label": label, "display_name": label, "description": "",
            "version": 1, "status": "active", "source": source,
        })
    return result


def _name(value: dict[str, Any]) -> str:
    return str(value.get("title") or value.get("display_name") or value.get("name") or value.get("code") or value.get("id") or "")


def _registered_object_entity(value: dict[str, Any]) -> dict[str, Any]:
    definition = value.get("scientific_definition") if isinstance(value.get("scientific_definition"), dict) else {}
    object_type = str(value.get("object_type") or value.get("entity_type") or "registered_object")
    registry_id = str(value.get("id") or value.get("registry_id") or value.get("code") or "")
    time_contract = value.get("time_contract") or value.get("global_time_contract") or definition.get("time_contract") or {}
    return {
        "id": registry_id,
        "registry_id": registry_id,
        "type": object_type,
        "entity_type": object_type,
        "code": str(value.get("code") or registry_id),
        "label": _name(value),
        "display_name": _name(value),
        "description": str(value.get("description") or definition.get("description") or ""),
        "version": value.get("version", definition.get("version", 1)),
        "status": str(value.get("status") or "draft"),
        "source": "research_object_registry",
        "schema_version": value.get("schema_version") or definition.get("schema_version"),
        "measurement_scale_ref": value.get("measurement_scale_ref") or definition.get("measurement_scale_ref") or definition.get("scale_ref") or "",
        "unit": value.get("unit") or definition.get("unit") or definition.get("measurement_unit") or "",
        "time_contract": deepcopy(time_contract),
        "scientific_definition": deepcopy(definition),
    }


def _project_link_entities(project: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for block in project.get("blocks") or []:
        for link in block.get("entity_links") or []:
            reference = link.get("reference") if isinstance(link.get("reference"), dict) else link
            entity_ref = str(reference.get("entity_ref") or reference.get("entity_id") or reference.get("registry_id") or "")
            if not entity_ref:
                continue
            entity_type = str(reference.get("entity_type") or link.get("entity_type") or "registered_data_source")
            result.append({
                "id": entity_ref, "registry_id": entity_ref, "type": entity_type,
                "entity_type": entity_type,
                "code": str(reference.get("code") or entity_ref),
                "label": str(reference.get("display_name") or reference.get("title") or entity_ref),
                "display_name": str(reference.get("display_name") or reference.get("title") or entity_ref),
                "description": str(reference.get("description") or ""),
                "version": reference.get("version"), "status": "connected",
                "source": f"project:{project.get('id')}:block:{block.get('block_id')}",
                "measurement_scale_ref": reference.get("measurement_scale_ref") or reference.get("scale_ref") or "",
                "unit": reference.get("unit") or "",
                "time_contract": deepcopy(reference.get("time_contract") or {}),
            })
    return result


def _time_axis(language: str) -> dict[str, Any]:
    names = {"ru": "Единая временная ось UTC", "en": "Unified UTC time axis", "es": "Eje temporal UTC unificado"}
    return {
        "id": "time-axis:utc", "registry_id": "time-axis:utc",
        "type": "time_variable", "entity_type": "time_variable", "code": "utc",
        "label": names[language], "display_name": names[language],
        "description": "ISO 8601 UTC observation timestamps; display timezone never changes stored time.",
        "version": 1, "status": "active", "source": "health_model_time_contract",
        "measurement_scale_ref": "datetime", "unit": "UTC",
        "time_contract": {"contract_version": "measurement-time-contract-1", "axis": "UTC", "raw_and_derived_timestamps_preserved": True},
    }


def list_entities(
    entity_type: str | None = None,
    language: str = "ru",
    owner: str | None = None,
) -> list[dict[str, Any]]:
    lang = _language(language)
    entities = [_time_axis(lang)]
    entities.extend(_question_entities(lang))
    entities.extend(_simple_entities(MODEL_PARAMETERS, "model_parameter", "health_model_parameter_catalog", lang))
    entities.extend(_simple_entities(MODEL_MECHANISMS, "mechanism", "health_model_mechanism_catalog", lang))
    entities.extend(_simple_entities(STATISTICAL_METHODS, "statistical_method", "scientific_method_catalog", lang))
    objects = [
        item
        for item in load_objects()
        if owner is None or str(item.get("owner") or "") == owner
    ]
    for item in objects:
        if str(item.get("object_type") or "") in REGISTERED_OBJECT_TYPES:
            entities.append(_registered_object_entity(item))
        if item.get("object_type") == "project":
            entities.extend(_project_link_entities(item))
    deduplicated: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in entities:
        key = (str(item.get("entity_type")), str(item.get("registry_id")), str(item.get("version")))
        deduplicated[key] = item
    result = list(deduplicated.values())
    if entity_type:
        result = [item for item in result if item.get("entity_type") == entity_type or item.get("type") == entity_type]
    return result


def list_hypothesis_entities(*, owner: str, project_id: str | None,
                             language: str = "ru", mode: str = "humanities_qualitative") -> list[dict[str, Any]]:
    """Return role-eligible evidence, never an undifferentiated global catalog.

    Qualitative inquiry deliberately excludes question definitions and the global
    UTC axis: a question is an instrument definition, not collected evidence, and
    time metadata is added automatically to material provenance.  Technical mode
    retains the broader versioned measurement catalog.
    """
    lang = _language(language)
    objects = load_objects()
    owned = [item for item in objects if str(item.get("owner") or "") == owner]
    project = next((item for item in owned if item.get("object_type") == "project" and item.get("id") == project_id), None) if project_id else None
    project_refs: set[tuple[str, str]] = set()
    if project:
        for block in project.get("blocks") or []:
            for link in block.get("entity_links") or []:
                reference = link.get("reference") if isinstance(link.get("reference"), dict) else link
                ref = str(reference.get("entity_ref") or reference.get("entity_id") or reference.get("registry_id") or "")
                version = str(reference.get("version"))
                if ref:
                    project_refs.add((ref, version))
    result = []
    if mode == "humanities_qualitative":
        for item in owned:
            object_type = str(item.get("object_type") or "")
            if object_type not in QUALITATIVE_HYPOTHESIS_ENTITY_TYPES:
                continue
            entity = _registered_object_entity(item)
            in_project = not project_id or item.get("project_id") == project_id or (entity["registry_id"], str(entity.get("version"))) in project_refs
            entity["project_scope"] = "current_project" if in_project and project_id else "researcher_library"
            entity["eligible_roles"] = (
                ["empirical_material"] if object_type in {
                    "qualitative_dataset", "interview_corpus", "focus_group_corpus", "document_corpus",
                    "observation_record", "field_notes", "questionnaire_result", "measurement_dataset",
                    "parameter_result", "analysis_result", "image_video_dataset", "game_result",
                } else ["prior_empirical_result", "theory_framework", "contextual_source"]
            )
            result.append(entity)
        if project:
            for item in _project_link_entities(project):
                if item["entity_type"] not in QUALITATIVE_HYPOTHESIS_ENTITY_TYPES:
                    continue
                item["project_scope"] = "current_project"
                item["eligible_roles"] = ["empirical_material", "prior_empirical_result"]
                result.append(item)
    else:
        # The UTC axis is system-managed. It is returned so the client can add
        # its exact contract automatically, but it is never offered as an
        # arbitrary measured object.
        axis = _time_axis(lang)
        axis["eligible_variable_roles"] = ["time"]
        axis["eligible_source_roles"] = ["time_axis"]
        axis["system_managed"] = True
        result.append(axis)
        technical_items = [_registered_object_entity(item) for item in owned
                           if str(item.get("object_type") or "") in TECHNICAL_HYPOTHESIS_ENTITY_TYPES]
        if project:
            technical_items.extend(item for item in _project_link_entities(project)
                                   if item.get("entity_type") in TECHNICAL_HYPOTHESIS_ENTITY_TYPES)
        for entity in technical_items:
            entity_type = str(entity.get("entity_type") or "")
            entity["eligible_variable_roles"] = list(TECHNICAL_VARIABLE_ROLES.get(entity_type, []))
            entity["eligible_source_roles"] = list(TECHNICAL_SOURCE_ROLES.get(entity_type, []))
            entity["project_scope"] = (
                "current_project" if project_id and (
                    (entity["registry_id"], str(entity.get("version"))) in project_refs
                    or str(entity.get("source") or "").startswith(f"project:{project_id}:")
                ) else "researcher_library"
            )
            result.append(entity)
    deduplicated: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in result:
        key = (str(item.get("entity_type")), str(item.get("registry_id")), str(item.get("version")))
        deduplicated[key] = item
    return sorted(deduplicated.values(), key=lambda item: (item.get("project_scope") != "current_project", str(item.get("display_name") or "").lower()))
