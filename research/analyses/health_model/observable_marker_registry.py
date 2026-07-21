from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
)


OBSERVABLE_MARKER_SCHEMA_VERSION = "health-model-observable-marker-1"
OBSERVABLE_MARKER_REGISTRY_SCHEMA_VERSION = (
    "health-model-observable-marker-registry-1"
)
OBSERVABLE_MARKER_NAMESPACE = UUID(
    "34cc8fb0-f059-4ac0-90e1-d628be15dde3"
)
CUSTOM_MARKER_DEFINITIONS_PATH = Path(
    "data/health_model_observable_markers.json"
)

DEVELOPMENT_STATUSES = {"draft", "trial", "active"}
SOURCE_TYPES = {
    "questionnaire",
    "clinical_measurement",
    "sensor",
    "camera",
    "game",
    "laboratory",
    "record",
    "researcher_observation",
    "event",
    "derived",
}
MARKER_ROLES = {
    "measurement_input",
    "change_indicator",
    "confirmation",
    "disconfirmation",
    "independent_validation",
    "data_quality",
}
DIRECTIONS = {
    "increases",
    "decreases",
    "bidirectional",
    "threshold",
    "categorical_change",
    "not_assumed",
}
AUTHORSHIP_ROLES = {
    "concept_author",
    "scientific_developer",
    "researcher",
    "engineer",
    "reviewer",
    "contributor",
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _slug(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    result = []
    previous_separator = False
    for char in normalized:
        if char.isalnum() or char in {".", "-"}:
            result.append(char)
            previous_separator = False
        elif not previous_separator:
            result.append("_")
            previous_separator = True
    return "".join(result).strip("_")


def _localized_value(value: Any, language: str) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(
            value.get(language)
            or value.get("ru")
            or value.get("en")
            or value.get("es")
            or ""
        ).strip()
    return ""


def _load_custom() -> list[dict]:
    if not CUSTOM_MARKER_DEFINITIONS_PATH.exists():
        return []
    data = json.loads(
        CUSTOM_MARKER_DEFINITIONS_PATH.read_text(encoding="utf-8")
    )
    if not isinstance(data, list):
        raise ValueError("OBSERVABLE_MARKER_REGISTRY_MUST_BE_LIST")
    return [item for item in data if isinstance(item, dict)]


def _save_custom(definitions: list[dict]) -> None:
    CUSTOM_MARKER_DEFINITIONS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    temporary = CUSTOM_MARKER_DEFINITIONS_PATH.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(definitions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(CUSTOM_MARKER_DEFINITIONS_PATH)


def normalize_observable_marker_definition(
    definition: dict,
) -> dict:
    normalized = deepcopy(definition)
    language = str(
        normalized.get("content_language") or "ru"
    ).lower()
    if language not in {"ru", "en", "es"}:
        language = "ru"
    normalized["content_language"] = language

    title = normalized.get("title")
    if isinstance(title, str):
        title = {language: title.strip()}
    elif not isinstance(title, dict):
        title = {}
    normalized["title"] = title

    marker_code = _slug(
        normalized.get("marker_code")
        or _localized_value(title, language)
    )
    normalized["marker_code"] = marker_code
    normalized.setdefault(
        "marker_id",
        str(uuid5(OBSERVABLE_MARKER_NAMESPACE, marker_code)),
    )
    normalized.setdefault(
        "schema_version",
        OBSERVABLE_MARKER_SCHEMA_VERSION,
    )
    normalized.setdefault(
        "registry_schema_version",
        OBSERVABLE_MARKER_REGISTRY_SCHEMA_VERSION,
    )
    normalized.setdefault("definition_version", 1)
    normalized.setdefault("development_status", "draft")
    normalized.setdefault("authorship", [])
    normalized.setdefault("allowed_roles", [])
    normalized.setdefault("source_contract", {})
    normalized.setdefault("value_contract", {})
    normalized.setdefault("temporal_contract", {})
    normalized.setdefault("quality_contract", {})
    normalized.setdefault("provenance", {})

    value_contract = normalized["value_contract"]
    scale_type = value_contract.get("scale_type")
    scale_definition = get_scale_definition(scale_type)
    value_contract["scale_binding_status"] = (
        "registered" if scale_definition is not None else "unbound"
    )
    value_contract["scale_reference"] = (
        build_scale_reference(scale_type)
        if scale_definition is not None
        else None
    )

    temporal_contract = normalized["temporal_contract"]
    temporal_contract.setdefault("observation_time_required", True)
    temporal_contract.setdefault("global_time_reference", "UTC")
    temporal_contract.setdefault("timezone_required", True)
    temporal_contract.setdefault(
        "synchronization_reference_required",
        True,
    )

    normalized["updated_at"] = _now()
    normalized.setdefault("created_at", normalized["updated_at"])
    return normalized


def validate_observable_marker_definition(
    definition: dict,
    *,
    target_status: str | None = None,
) -> dict:
    normalized = normalize_observable_marker_definition(definition)
    status = target_status or normalized["development_status"]
    errors = []
    warnings = []

    if not normalized["marker_code"]:
        errors.append({"field": "marker_code", "code": "MARKER_CODE_REQUIRED"})
    try:
        UUID(str(normalized.get("marker_id")))
    except (TypeError, ValueError):
        errors.append({"field": "marker_id", "code": "MARKER_ID_INVALID_UUID"})
    if status not in DEVELOPMENT_STATUSES:
        errors.append({
            "field": "development_status",
            "code": "MARKER_DEVELOPMENT_STATUS_INVALID",
        })
    language = normalized["content_language"]
    if not _localized_value(normalized["title"], language):
        errors.append({"field": "title", "code": "MARKER_TITLE_REQUIRED"})

    authorship = normalized.get("authorship") or []
    if not isinstance(authorship, list):
        errors.append({"field": "authorship", "code": "AUTHORSHIP_MUST_BE_LIST"})
        authorship = []
    for index, author in enumerate(authorship):
        if not isinstance(author, dict) or not str(author.get("display_name") or "").strip():
            errors.append({
                "field": f"authorship.{index}.display_name",
                "code": "AUTHOR_DISPLAY_NAME_REQUIRED",
            })
            continue
        if author.get("role") not in AUTHORSHIP_ROLES:
            errors.append({
                "field": f"authorship.{index}.role",
                "code": "AUTHORSHIP_ROLE_INVALID",
            })

    source = normalized.get("source_contract") or {}
    value = normalized.get("value_contract") or {}
    allowed_roles = normalized.get("allowed_roles") or []
    if source.get("source_type") and source["source_type"] not in SOURCE_TYPES:
        errors.append({"field": "source_contract.source_type", "code": "MARKER_SOURCE_TYPE_INVALID"})
    invalid_roles = sorted(set(allowed_roles) - MARKER_ROLES)
    if invalid_roles:
        errors.append({
            "field": "allowed_roles",
            "code": "MARKER_ROLE_INVALID",
            "values": invalid_roles,
        })
    if normalized.get("direction") and normalized["direction"] not in DIRECTIONS:
        errors.append({"field": "direction", "code": "MARKER_DIRECTION_INVALID"})

    if status in {"trial", "active"}:
        required = {
            "working_definition": normalized.get("working_definition"),
            "source_contract.source_type": source.get("source_type"),
            "source_contract.observable_field": source.get("observable_field"),
            "value_contract.scale_type": value.get("scale_type"),
            "allowed_roles": allowed_roles,
            "authorship": authorship,
        }
        for field, value_item in required.items():
            if value_item in (None, "", []):
                errors.append({"field": field, "code": "MARKER_FIELD_REQUIRED_FOR_TRIAL"})
        if value.get("scale_binding_status") != "registered":
            errors.append({
                "field": "value_contract.scale_type",
                "code": "REGISTERED_MARKER_SCALE_REQUIRED",
            })
    if status == "active" and not (normalized.get("quality_contract") or {}).get("acceptance_rule"):
        errors.append({
            "field": "quality_contract.acceptance_rule",
            "code": "MARKER_QUALITY_RULE_REQUIRED_FOR_ACTIVE",
        })

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "definition": normalized,
    }


def list_observable_markers(
    *,
    include_drafts: bool = True,
) -> dict:
    definitions = _load_custom()
    if not include_drafts:
        definitions = [
            item
            for item in definitions
            if item.get("development_status") in {"trial", "active"}
        ]
    definitions.sort(
        key=lambda item: (
            str(item.get("marker_code") or ""),
            int(item.get("definition_version") or 1),
        )
    )
    return {
        "ok": True,
        "registry_schema_version": OBSERVABLE_MARKER_REGISTRY_SCHEMA_VERSION,
        "definitions": definitions,
        "source_types": sorted(SOURCE_TYPES),
        "marker_roles": sorted(MARKER_ROLES),
        "directions": sorted(DIRECTIONS),
        "authorship_roles": sorted(AUTHORSHIP_ROLES),
    }


def upsert_observable_marker_draft(definition: dict) -> dict:
    normalized = normalize_observable_marker_definition(definition)
    normalized["development_status"] = "draft"
    validation = validate_observable_marker_definition(normalized)
    if not normalized["marker_code"]:
        return {"ok": False, "status": "marker_code_required", "validation": validation}

    definitions = _load_custom()
    versions = [
        int(item.get("definition_version") or 1)
        for item in definitions
        if item.get("marker_code") == normalized["marker_code"]
    ]
    requested_version = definition.get("definition_version")
    existing_index = next(
        (
            index
            for index, item in enumerate(definitions)
            if item.get("marker_code") == normalized["marker_code"]
            and int(item.get("definition_version") or 1)
            == int(requested_version or -1)
            and item.get("development_status") == "draft"
        ),
        None,
    )
    if existing_index is None:
        normalized["definition_version"] = max(versions, default=0) + 1
        definitions.append(normalized)
    else:
        normalized["definition_version"] = int(requested_version)
        normalized["created_at"] = definitions[existing_index].get(
            "created_at",
            normalized["created_at"],
        )
        definitions[existing_index] = normalized
    _save_custom(definitions)
    return {"ok": True, "status": "draft_saved", "definition": normalized, "validation": validation}


def transition_observable_marker(
    marker_code: str,
    definition_version: int,
    target_status: str,
) -> dict:
    target_status = str(target_status or "").lower()
    allowed = {"draft": {"trial"}, "trial": {"active"}, "active": set()}
    definitions = _load_custom()
    index = next(
        (
            index
            for index, item in enumerate(definitions)
            if item.get("marker_code") == marker_code
            and int(item.get("definition_version") or 1) == int(definition_version)
        ),
        None,
    )
    if index is None:
        return {"ok": False, "status": "marker_not_found"}
    current = definitions[index]
    if target_status not in allowed.get(current.get("development_status"), set()):
        return {"ok": False, "status": "marker_transition_not_allowed"}
    validation = validate_observable_marker_definition(current, target_status=target_status)
    if not validation["valid"]:
        return {"ok": False, "status": "marker_transition_validation_failed", "validation": validation}
    transitioned = validation["definition"]
    transitioned["development_status"] = target_status
    transitioned["updated_at"] = _now()
    definitions[index] = transitioned
    _save_custom(definitions)
    return {"ok": True, "status": target_status, "definition": transitioned, "validation": validation}


def delete_observable_marker_draft(
    marker_code: str,
    definition_version: int,
) -> dict:
    definitions = _load_custom()
    remaining = []
    deleted = None
    for item in definitions:
        if (
            item.get("marker_code") == marker_code
            and int(item.get("definition_version") or 1) == int(definition_version)
        ):
            if item.get("development_status") != "draft":
                return {"ok": False, "status": "only_marker_draft_can_be_deleted"}
            deleted = item
            continue
        remaining.append(item)
    if deleted is None:
        return {"ok": False, "status": "marker_not_found"}
    _save_custom(remaining)
    return {"ok": True, "status": "marker_draft_deleted", "definition": deleted}
