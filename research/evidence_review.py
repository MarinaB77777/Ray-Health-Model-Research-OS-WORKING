from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from research.repository import OBJECT_STORE_LOCK, load_objects, save_objects


SCHEMA_VERSION = "scientific-evidence-review-plan-1"
OBJECT_TYPE = "evidence_review"
SUPPORTED_LANGUAGES = frozenset({"ru", "en", "es"})
SUPPORTED_STATUSES = frozenset({"draft", "trial", "active"})

REVIEW_TYPES = {
    "systematic_review": "Systematic review",
    "scoping_review": "Scoping review",
    "rapid_review": "Rapid review with declared shortcuts",
    "evidence_map": "Evidence map",
    "narrative_review": "Structured narrative review",
    "mixed_evidence_review": "Mixed quantitative and qualitative evidence review",
}

REPORTING_FRAMEWORKS = {
    "prisma_2020": "PRISMA 2020",
    "prisma_scoping": "PRISMA-ScR",
    "prisma_search": "PRISMA-S",
    "swim": "SWiM when meta-analysis is not appropriate",
    "srqr": "SRQR for qualitative evidence components",
    "coreq": "COREQ when interview or focus-group evidence applies",
    "custom_declared": "Other explicitly declared framework",
}

APPRAISAL_APPROACHES = {
    "risk_of_bias_design_specific": "Design-specific risk-of-bias assessment",
    "methodological_quality_design_specific": "Design-specific methodological-quality appraisal",
    "certainty_body_of_evidence": "Certainty or confidence in the body of evidence",
    "qualitative_confidence": "Confidence in qualitative findings",
    "not_applicable_with_justification": "Not applicable, with an explicit justification",
}

SYNTHESIS_APPROACHES = {
    "meta_analysis": "Meta-analysis when data and estimands are compatible",
    "synthesis_without_meta_analysis": "Structured synthesis without meta-analysis",
    "narrative_synthesis": "Structured narrative synthesis",
    "thematic_synthesis": "Qualitative thematic synthesis",
    "framework_synthesis": "Framework synthesis",
    "evidence_map": "Evidence mapping",
    "mixed_methods_integration": "Mixed-methods integration",
}


class EvidenceReviewError(Exception):
    def __init__(self, code: str, status_code: int = 422) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def _utc_iso() -> str:
    return datetime.now(UTC).isoformat()


def _text(value: Any, maximum: int = 30000) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise EvidenceReviewError("EVIDENCE_REVIEW_TEXT_FIELD_INVALID")
    result = value.strip()
    if len(result) > maximum:
        raise EvidenceReviewError("EVIDENCE_REVIEW_TEXT_FIELD_TOO_LONG")
    return result


def _unique_texts(values: Any, maximum_items: int = 500) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list) or len(values) > maximum_items:
        raise EvidenceReviewError("EVIDENCE_REVIEW_LIST_FIELD_INVALID")
    return list(dict.fromkeys(item for item in (_text(value, 4000) for value in values) if item))


def _selected_item(
    raw: Any,
    valid_catalog_ids: set[str],
    catalog_items_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise EvidenceReviewError("EVIDENCE_REVIEW_CATALOG_ITEM_INVALID")
    catalog_id = _text(raw.get("catalog_id"), 500)
    if not catalog_id or catalog_id not in valid_catalog_ids:
        raise EvidenceReviewError("EVIDENCE_REVIEW_CATALOG_ITEM_NOT_REGISTERED")
    registered = (catalog_items_by_id or {}).get(catalog_id, raw)
    return {
        "catalog_id": catalog_id,
        "category": _text(registered.get("category"), 100),
        "registry_id": _text(registered.get("registry_id"), 500),
        "version": deepcopy(registered.get("version")),
        "title": _text(registered.get("title"), 1000),
        "status": _text(registered.get("status"), 200),
        "planned_role": _text(raw.get("planned_role"), 1000),
        "source_route": _text(registered.get("source_route"), 2000),
    }


def contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "review_types": deepcopy(REVIEW_TYPES),
        "reporting_frameworks": deepcopy(REPORTING_FRAMEWORKS),
        "appraisal_approaches": deepcopy(APPRAISAL_APPROACHES),
        "synthesis_approaches": deepcopy(SYNTHESIS_APPROACHES),
        "lifecycle_statuses": ["draft", "trial", "active"],
        "invariants": [
            "ray_suggestion_is_not_evidence",
            "registered_method_is_not_automatically_appropriate_or_executable",
            "search_sources_queries_dates_and_limits_are_preserved",
            "screening_decisions_and_exclusion_reasons_are_auditable",
            "risk_of_bias_is_distinct_from_certainty_in_the_body_of_evidence",
            "absence_of_evidence_is_not_evidence_of_absence",
            "contradictory_and_null_results_are_retained",
            "review_protocol_changes_are_versioned_not_silently_overwritten",
            "sensor_questionnaire_game_and_model_outputs_are_measurements_not_ground_truth",
            "all_collected_and_derived_data_remain_bound_to_the_global_time_reference",
        ],
    }


def build_plan(
    raw: dict[str, Any],
    *,
    status: str,
    valid_catalog_ids: set[str],
    catalog_items_by_id: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if status not in SUPPORTED_STATUSES:
        raise EvidenceReviewError("EVIDENCE_REVIEW_STATUS_UNSUPPORTED")
    if not isinstance(raw, dict):
        raise EvidenceReviewError("EVIDENCE_REVIEW_PLAN_INVALID")

    review_type = _text(raw.get("review_type"), 100)
    framework_ids = _unique_texts(raw.get("reporting_framework_ids"), 30)
    appraisal_ids = _unique_texts(raw.get("appraisal_approach_ids"), 30)
    synthesis_ids = _unique_texts(raw.get("synthesis_approach_ids"), 30)
    if review_type and review_type not in REVIEW_TYPES:
        raise EvidenceReviewError("EVIDENCE_REVIEW_TYPE_UNSUPPORTED")
    if any(value not in REPORTING_FRAMEWORKS for value in framework_ids):
        raise EvidenceReviewError("EVIDENCE_REVIEW_FRAMEWORK_UNSUPPORTED")
    if any(value not in APPRAISAL_APPROACHES for value in appraisal_ids):
        raise EvidenceReviewError("EVIDENCE_REVIEW_APPRAISAL_UNSUPPORTED")
    if any(value not in SYNTHESIS_APPROACHES for value in synthesis_ids):
        raise EvidenceReviewError("EVIDENCE_REVIEW_SYNTHESIS_UNSUPPORTED")

    selected = []
    seen = set()
    for value in raw.get("selected_catalog_items") or []:
        item = _selected_item(value, valid_catalog_ids, catalog_items_by_id)
        if item["catalog_id"] in seen:
            continue
        seen.add(item["catalog_id"])
        selected.append(item)

    search_sources = []
    for value in raw.get("search_sources") or []:
        if not isinstance(value, dict):
            raise EvidenceReviewError("EVIDENCE_REVIEW_SEARCH_SOURCE_INVALID")
        name = _text(value.get("name"), 1000)
        if not name:
            continue
        search_sources.append({
            "name": name,
            "source_type": _text(value.get("source_type"), 200),
            "coverage_or_platform": _text(value.get("coverage_or_platform"), 2000),
            "planned_query": _text(value.get("planned_query")),
            "limits_and_justification": _text(value.get("limits_and_justification")),
            "searched_at_utc": _text(value.get("searched_at_utc"), 100),
        })

    review_question = _text(raw.get("review_question"))
    eligibility = {
        "population_or_participants": _text(raw.get("population_or_participants")),
        "concept_or_exposure": _text(raw.get("concept_or_exposure")),
        "context_or_setting": _text(raw.get("context_or_setting")),
        "outcomes_or_phenomena": _text(raw.get("outcomes_or_phenomena")),
        "study_designs": _text(raw.get("study_designs")),
        "inclusion_criteria": _text(raw.get("inclusion_criteria")),
        "exclusion_criteria": _text(raw.get("exclusion_criteria")),
    }
    screening = {
        "deduplication_rule": _text(raw.get("deduplication_rule")),
        "screening_process": _text(raw.get("screening_process")),
        "reviewer_independence": _text(raw.get("reviewer_independence")),
        "disagreement_resolution": _text(raw.get("disagreement_resolution")),
        "exclusion_reason_policy": _text(raw.get("exclusion_reason_policy")),
    }
    extraction = {
        "data_items": _unique_texts(raw.get("extraction_data_items")),
        "effect_measures_or_outputs": _text(raw.get("effect_measures_or_outputs")),
        "missing_information_rule": _text(raw.get("missing_information_rule")),
        "automation_use_and_validation": _text(raw.get("automation_use_and_validation")),
    }
    synthesis = {
        "approach_ids": synthesis_ids,
        "compatibility_rule": _text(raw.get("synthesis_compatibility_rule")),
        "heterogeneity_plan": _text(raw.get("heterogeneity_plan")),
        "sensitivity_analysis_plan": _text(raw.get("sensitivity_analysis_plan")),
        "reporting_bias_plan": _text(raw.get("reporting_bias_plan")),
        "certainty_plan": _text(raw.get("certainty_plan")),
    }

    issues: list[str] = []
    if not _text(raw.get("title"), 1000):
        issues.append("EVIDENCE_REVIEW_TITLE_REQUIRED")
    if not review_question:
        issues.append("EVIDENCE_REVIEW_QUESTION_REQUIRED")
    if not review_type:
        issues.append("EVIDENCE_REVIEW_TYPE_REQUIRED")
    if not eligibility["inclusion_criteria"]:
        issues.append("EVIDENCE_REVIEW_INCLUSION_CRITERIA_REQUIRED")
    if not eligibility["exclusion_criteria"]:
        issues.append("EVIDENCE_REVIEW_EXCLUSION_CRITERIA_REQUIRED")
    if not search_sources:
        issues.append("EVIDENCE_REVIEW_SEARCH_SOURCE_REQUIRED")
    if search_sources and not all(item["planned_query"] for item in search_sources):
        issues.append("EVIDENCE_REVIEW_QUERY_REQUIRED_FOR_EACH_SOURCE")
    if not screening["screening_process"]:
        issues.append("EVIDENCE_REVIEW_SCREENING_PROCESS_REQUIRED")
    if not screening["exclusion_reason_policy"]:
        issues.append("EVIDENCE_REVIEW_EXCLUSION_REASON_POLICY_REQUIRED")
    if not extraction["data_items"]:
        issues.append("EVIDENCE_REVIEW_EXTRACTION_ITEMS_REQUIRED")
    if not appraisal_ids:
        issues.append("EVIDENCE_REVIEW_APPRAISAL_PLAN_REQUIRED")
    if not synthesis_ids:
        issues.append("EVIDENCE_REVIEW_SYNTHESIS_PLAN_REQUIRED")
    if not synthesis["compatibility_rule"]:
        issues.append("EVIDENCE_REVIEW_SYNTHESIS_COMPATIBILITY_RULE_REQUIRED")
    if not _text(raw.get("contradictory_evidence_rule")):
        issues.append("EVIDENCE_REVIEW_CONTRADICTORY_EVIDENCE_RULE_REQUIRED")
    if not _text(raw.get("claim_decision_rule")):
        issues.append("EVIDENCE_REVIEW_CLAIM_DECISION_RULE_REQUIRED")
    if not selected:
        issues.append("EVIDENCE_ACQUISITION_SOURCE_OR_METHOD_REQUIRED")
    if status == "active" and not bool(raw.get("researcher_approved")):
        issues.append("EVIDENCE_REVIEW_RESEARCHER_APPROVAL_REQUIRED")

    blockers = [] if status == "draft" else list(dict.fromkeys(issues))
    return {
        "schema_version": SCHEMA_VERSION,
        "title": _text(raw.get("title"), 1000),
        "review_question": review_question,
        "review_type": review_type,
        "objective": _text(raw.get("objective")),
        "protocol_registration": _text(raw.get("protocol_registration"), 2000),
        "reporting_framework_ids": framework_ids,
        "eligibility": eligibility,
        "search": {
            "sources": search_sources,
            "supplementary_methods": _unique_texts(raw.get("supplementary_search_methods")),
            "search_update_rule": _text(raw.get("search_update_rule")),
        },
        "screening": screening,
        "extraction": extraction,
        "appraisal": {
            "approach_ids": appraisal_ids,
            "tools_and_versions": _text(raw.get("appraisal_tools_and_versions")),
            "judgement_process": _text(raw.get("appraisal_judgement_process")),
        },
        "synthesis": synthesis,
        "evidence_acquisition_plan": {
            "selected_catalog_items": selected,
            "global_time_reference": "UTC",
            "selection_does_not_assert_method_compatibility": True,
        },
        "contradictory_evidence_rule": _text(raw.get("contradictory_evidence_rule")),
        "claim_decision_rule": _text(raw.get("claim_decision_rule")),
        "limitations_and_shortcuts": _text(raw.get("limitations_and_shortcuts")),
        "researcher_approved": bool(raw.get("researcher_approved")),
        "readiness": {
            "valid_for_status": not blockers,
            "status": status,
            "issues": list(dict.fromkeys(issues)),
            "blocking_issues": blockers,
        },
        "standards_basis": ["PRISMA_2020", "PRISMA_flow_and_search_reporting"],
        "invariants": contract()["invariants"],
    }


def save_review(
    *, owner: str,
    authorship: dict[str, Any],
    status: str,
    language: str,
    plan: dict[str, Any],
    project_id: str | None = None,
    block_id: str | None = None,
    review_id: str | None = None,
) -> dict[str, Any]:
    if language not in SUPPORTED_LANGUAGES:
        raise EvidenceReviewError("EVIDENCE_REVIEW_LANGUAGE_UNSUPPORTED")
    if not owner:
        raise EvidenceReviewError("EVIDENCE_REVIEW_OWNER_REQUIRED")
    if status != "draft" and not plan.get("readiness", {}).get("valid_for_status"):
        raise EvidenceReviewError("EVIDENCE_REVIEW_NOT_READY_FOR_STATUS")
    timestamp = _utc_iso()
    stable_id = review_id or str(uuid4())
    with OBJECT_STORE_LOCK:
        objects = load_objects()
        previous = [
            item for item in objects
            if item.get("object_type") == OBJECT_TYPE
            and item.get("owner") == owner
            and item.get("review_id") == stable_id
        ]
        version = max((int(item.get("version") or 0) for item in previous), default=0) + 1
        record = {
            "id": str(uuid4()),
            "review_id": stable_id,
            "version": version,
            "object_type": OBJECT_TYPE,
            "owner": owner,
            "status": status,
            "title": plan["title"],
            "description": plan.get("objective") or "",
            "research_question": plan["review_question"],
            "language": language,
            "project_id": project_id,
            "block_id": block_id,
            "schema_version": SCHEMA_VERSION,
            "scientific_definition": deepcopy(plan),
            "authorship": deepcopy(authorship),
            "provenance_links": [
                item["catalog_id"]
                for item in plan["evidence_acquisition_plan"]["selected_catalog_items"]
            ],
            "created_at": previous[0].get("created_at", timestamp) if previous else timestamp,
            "updated_at": timestamp,
        }
        objects.append(record)
        save_objects(objects)
    return record


def list_reviews(owner: str, *, review_id: str | None = None) -> list[dict[str, Any]]:
    values = [
        item for item in load_objects()
        if item.get("object_type") == OBJECT_TYPE and item.get("owner") == owner
    ]
    if review_id:
        values = [item for item in values if item.get("review_id") == review_id]
    return sorted(values, key=lambda item: (str(item.get("updated_at") or ""), int(item.get("version") or 0)), reverse=True)
