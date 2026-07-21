from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import NAMESPACE_URL, uuid5

from assessment.measurement.scale_registry import build_scale_reference
from assessment.questionnaire_components import (
    normalize_question_type_id,
    normalize_response_type_id,
    normalize_scale_type_id,
    validate_question_measurement_contract,
)
from research.editors.audit import append_audit_event


QUESTION_EDITOR_REGISTRY_VERSION = "question-editor-registry-1"
QUESTION_DEFINITION_VERSION = "registered-question-definition-2"
DEFAULT_PATH = Path("data/question_editor_versions.json")
LANGUAGES = ("ru", "en", "es")
STATUSES = ("draft", "trial", "active")
_LOCK = RLock()


def _read(path: Path = DEFAULT_PATH) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8") or "[]")
    if isinstance(payload, dict):
        payload = payload.get("definitions", [])
    if not isinstance(payload, list):
        raise ValueError("question editor registry must contain a list")
    return payload


def _write(definitions: list[dict], path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": QUESTION_EDITOR_REGISTRY_VERSION,
        "definitions": definitions,
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(path)


def _code(value: object) -> str:
    return str(value or "").strip()


def _version(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def validate_question_definition(definition: dict) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    is_draft = definition.get("development_status") == "draft"
    for field in ("bank_id", "question_code", "question_version", "development_status"):
        if definition.get(field) in (None, ""):
            errors.append({"field": field, "code": "REQUIRED"})
    if definition.get("development_status") not in STATUSES:
        errors.append({"field": "development_status", "code": "UNSUPPORTED_STATUS"})
    translations = definition.get("translations")
    if not isinstance(translations, dict):
        errors.append({"field": "translations", "code": "TRANSLATIONS_REQUIRED"})
    else:
        for language in LANGUAGES:
            translation = translations.get(language)
            if not isinstance(translation, dict) or not str(translation.get("prompt") or "").strip():
                (warnings if is_draft else errors).append({
                    "field": f"translations.{language}.prompt",
                    "code": "PROMPT_REQUIRED_FOR_EACH_LANGUAGE",
                })
    if not definition.get("question_type"):
        errors.append({"field": "question_type", "code": "QUESTION_TYPE_REQUIRED"})
    if not definition.get("response_type"):
        errors.append({"field": "response_type", "code": "RESPONSE_TYPE_REQUIRED"})
    scale_type = definition.get("scale_type")
    if scale_type and not isinstance(scale_type, str):
        errors.append({"field": "scale_type", "code": "SCALE_TYPE_MUST_BE_STRING"})
    authorship = definition.get("authorship") or {}
    if not str(authorship.get("primary_author") or "").strip():
        errors.append({"field": "authorship.primary_author", "code": "PRIMARY_AUTHOR_REQUIRED"})
    if not str(definition.get("change_reason") or "").strip():
        errors.append({"field": "change_reason", "code": "CHANGE_REASON_REQUIRED"})
    measurement_contract = validate_question_measurement_contract(
        definition.get("question_type"),
        definition.get("response_type"),
        definition.get("scale_type"),
        definition.get("presentation_type"),
    )
    errors.extend(measurement_contract["errors"])

    requires_options = definition.get("response_type") in {
        "single_choice", "multiple_choice", "ranking"
    }
    translations = definition.get("translations") or {}
    option_counts = []
    option_values = []
    for language in LANGUAGES:
        options = (translations.get(language) or {}).get("answer_options") or []
        option_counts.append(len(options))
        option_values.append([
            option.get("value") if isinstance(option, dict) else option
            for option in options
        ])
        if requires_options and not options:
            (warnings if is_draft else errors).append({
                "field": f"translations.{language}.answer_options",
                "code": "ANSWER_OPTIONS_REQUIRED",
            })
    non_empty_counts = [count for count in option_counts if count]
    non_empty_values = [values for values in option_values if values]
    if requires_options and non_empty_counts and len(set(non_empty_counts)) > 1:
        (warnings if is_draft else errors).append({"field": "translations", "code": "OPTION_COUNT_MISMATCH_BETWEEN_LANGUAGES"})
    if requires_options and non_empty_values and any(values != non_empty_values[0] for values in non_empty_values[1:]):
        (warnings if is_draft else errors).append({"field": "translations", "code": "OPTION_VALUE_MISMATCH_BETWEEN_LANGUAGES"})
    if definition.get("scale_type") == "binary" and (
        not non_empty_counts or any(count != 2 for count in non_empty_counts)
    ):
        (warnings if is_draft else errors).append({
            "field": "translations", "code": "BINARY_SCALE_REQUIRES_TWO_OPTIONS"
        })

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": [*warnings, *measurement_contract["warnings"]],
        "measurement_contract": measurement_contract,
    }


def normalize_question_definition(definition: dict) -> dict:
    normalized = deepcopy(definition)
    bank_id = _code(normalized.get("bank_id"))
    question_code = _code(normalized.get("question_code") or normalized.get("code"))
    version = _version(normalized.get("question_version") or normalized.get("version"))
    normalized["schema_version"] = QUESTION_DEFINITION_VERSION
    normalized["registry_schema_version"] = QUESTION_EDITOR_REGISTRY_VERSION
    normalized["bank_id"] = bank_id
    normalized["question_code"] = question_code
    normalized["question_id"] = normalized.get("question_id") or str(
        uuid5(NAMESPACE_URL, f"health-model-question:{bank_id}:{question_code}")
    )
    normalized["question_version"] = version
    normalized["development_status"] = str(
        normalized.get("development_status") or "draft"
    ).lower()
    normalized["question_type"] = normalize_question_type_id(
        normalized.get("question_type")
    )
    normalized["response_type"] = normalize_response_type_id(
        normalized.get("response_type")
    )
    normalized["scale_type"] = normalize_scale_type_id(
        normalized.get("scale_type")
    )
    if normalized.get("scale_type"):
        try:
            normalized["scale_reference"] = build_scale_reference(
                normalized["scale_type"]
            )
        except KeyError:
            normalized["scale_reference"] = None
    normalized["translations"] = {
        language: deepcopy((normalized.get("translations") or {}).get(language) or {})
        for language in LANGUAGES
    }
    normalized.setdefault("routing", {})
    normalized.setdefault("calculation_role", {})
    normalized.setdefault("missing_value_policy", {})
    normalized.setdefault("presentation_type", None)
    normalized.setdefault("category", None)
    normalized.setdefault("marker_references", [])
    normalized.setdefault("authorship", {})
    normalized.setdefault("provenance", {})
    normalized["provenance"].setdefault("registry_source", "question_editor")
    normalized["updated_at"] = datetime.now(UTC).isoformat()
    return normalized


def list_question_versions(
    bank_id: str | None = None,
    question_code: str | None = None,
    *,
    path: Path = DEFAULT_PATH,
) -> list[dict]:
    definitions = [normalize_question_definition(item) for item in _read(path)]
    if bank_id:
        definitions = [item for item in definitions if item["bank_id"] == bank_id]
    if question_code:
        definitions = [item for item in definitions if item["question_code"] == question_code]
    return sorted(
        definitions,
        key=lambda item: (item["bank_id"], item["question_code"], item["question_version"]),
    )


def upsert_question_draft(
    definition: dict,
    *,
    actor_id: str,
    path: Path = DEFAULT_PATH,
) -> dict:
    incoming = deepcopy(definition)
    bank_id = _code(incoming.get("bank_id"))
    question_code = _code(incoming.get("question_code") or incoming.get("code"))
    if not bank_id or not question_code:
        return {"ok": False, "status": "question_identity_required"}
    with _LOCK:
        definitions = _read(path)
        matching = [
            normalize_question_definition(item)
            for item in definitions
            if _code(item.get("bank_id")) == bank_id
            and _code(item.get("question_code") or item.get("code")) == question_code
        ]
        requested_version = incoming.get("question_version")
        if requested_version is None:
            drafts = [item for item in matching if item["development_status"] == "draft"]
            requested_version = (
                max(item["question_version"] for item in drafts)
                if drafts
                else max((item["question_version"] for item in matching), default=_version(incoming.get("base_version"))) + 1
            )
        incoming["question_version"] = int(requested_version)
        incoming["development_status"] = "draft"
        incoming.setdefault("provenance", {})
        incoming["provenance"]["edited_by"] = actor_id
        normalized = normalize_question_definition(incoming)
        validation = validate_question_definition(normalized)
        if not validation["valid"]:
            return {"ok": False, "status": "definition_invalid", "validation": validation, "definition": normalized}
        updated, replaced = [], False
        for raw in definitions:
            current = normalize_question_definition(raw)
            if current["bank_id"] == bank_id and current["question_code"] == question_code and current["question_version"] == int(requested_version):
                if current["development_status"] != "draft":
                    return {"ok": False, "status": "immutable_non_draft_version"}
                updated.append(normalized)
                replaced = True
            else:
                updated.append(raw)
        if not replaced:
            if any(item["question_version"] == int(requested_version) for item in matching):
                return {"ok": False, "status": "question_version_already_exists"}
            normalized["created_at"] = normalized["updated_at"]
            updated.append(normalized)
        _write(updated, path)
    audit = append_audit_event(
        action="question_draft_updated" if replaced else "question_draft_created",
        actor_id=actor_id,
        object_type="question_definition",
        object_id=f"{bank_id}:{question_code}:{requested_version}",
        reason=normalized["change_reason"],
        details={"validation": validation},
    )
    return {"ok": True, "status": "draft_updated" if replaced else "draft_created", "definition": normalized, "validation": validation, "audit_event": audit}


def transition_question_definition(
    bank_id: str,
    question_code: str,
    question_version: int,
    target_status: str,
    *,
    actor_id: str,
    reason: str,
    definition_patch: dict | None = None,
    path: Path = DEFAULT_PATH,
) -> dict:
    if not str(actor_id or "").strip() or not str(reason or "").strip():
        return {"ok": False, "status": "actor_and_reason_required"}
    transitions = {"draft": {"trial"}, "trial": {"active"}}
    with _LOCK:
        definitions = _read(path)
        updated, selected = [], None
        for raw in definitions:
            current = normalize_question_definition(raw)
            matches = current["bank_id"] == bank_id and current["question_code"] == question_code and current["question_version"] == int(question_version)
            if not matches:
                updated.append(raw)
                continue
            if target_status not in transitions.get(current["development_status"], set()):
                return {"ok": False, "status": "invalid_status_transition", "current_status": current["development_status"]}
            if definition_patch:
                for field, value in deepcopy(definition_patch).items():
                    current[field] = value
            current["development_status"] = target_status
            current["provenance"]["transitioned_by"] = actor_id
            current["provenance"]["transition_reason"] = reason
            current["updated_at"] = datetime.now(UTC).isoformat()
            validation = validate_question_definition(current)
            if not validation["valid"]:
                return {"ok": False, "status": "transition_validation_failed", "validation": validation}
            selected = current
            updated.append(current)
        if selected is None:
            return {"ok": False, "status": "definition_not_found"}
        _write(updated, path)
    audit = append_audit_event(
        action=f"question_transitioned_to_{target_status}", actor_id=actor_id,
        object_type="question_definition", object_id=f"{bank_id}:{question_code}:{question_version}",
        reason=reason, details={"target_status": target_status},
    )
    return {"ok": True, "status": f"transitioned_to_{target_status}", "definition": selected, "audit_event": audit}


def delete_question_draft(
    bank_id: str,
    question_code: str,
    question_version: int,
    *,
    actor_id: str,
    reason: str,
    path: Path = DEFAULT_PATH,
) -> dict:
    if not str(actor_id or "").strip() or not str(reason or "").strip():
        return {"ok": False, "status": "actor_and_reason_required"}
    with _LOCK:
        definitions = _read(path)
        kept, deleted = [], None
        for raw in definitions:
            current = normalize_question_definition(raw)
            matches = current["bank_id"] == bank_id and current["question_code"] == question_code and current["question_version"] == int(question_version)
            if not matches:
                kept.append(raw)
            elif current["development_status"] != "draft":
                return {"ok": False, "status": "only_draft_can_be_deleted"}
            else:
                deleted = current
        if deleted is None:
            return {"ok": False, "status": "definition_not_found"}
        _write(kept, path)
    audit = append_audit_event(
        action="question_draft_deleted", actor_id=actor_id,
        object_type="question_definition", object_id=f"{bank_id}:{question_code}:{question_version}",
        reason=reason, details={"deleted_version": question_version},
    )
    return {"ok": True, "status": "draft_deleted", "definition": deleted, "audit_event": audit}


def active_question_overlays(bank_id: str, lang: str, *, path: Path = DEFAULT_PATH) -> dict[str, dict]:
    selected: dict[str, dict] = {}
    for definition in list_question_versions(bank_id=bank_id, path=path):
        if definition["development_status"] != "active":
            continue
        code = definition["question_code"]
        if code not in selected or definition["question_version"] > selected[code]["question_version"]:
            selected[code] = definition
    overlays = {}
    for code, definition in selected.items():
        translation = definition["translations"].get(lang) or definition["translations"].get("en") or {}
        overlay = {
            "question_id": definition["question_id"],
            "bank_id": definition["bank_id"],
            "code": code,
            "question_version": definition["question_version"],
            "version": definition["question_version"],
            "status": "active",
            "prompt": translation.get("prompt"),
            "text": translation.get("prompt"),
            "answer_options": translation.get("answer_options") or definition.get("answer_options") or [],
            "question_type": definition.get("question_type"),
            "response_type": definition.get("response_type"),
            "presentation_type": definition.get("presentation_type"),
            "scale_type": definition.get("scale_type"),
            "scale_reference": definition.get("scale_reference"),
            "score_direction": definition.get("score_direction"),
            "unit": definition.get("unit"),
            "allowed_range": definition.get("allowed_range") or {},
            "allowed_values": definition.get("allowed_values") or [],
            "category": definition.get("category"),
            "routing": definition.get("routing") or {},
            "calculation_role": definition.get("calculation_role") or {},
            "missing_value_policy": definition.get("missing_value_policy") or {},
            "marker_references": definition.get("marker_references") or [],
            "editor_provenance": definition.get("provenance") or {},
        }
        overlays[code] = {key: value for key, value in overlay.items() if value is not None}
    return overlays
