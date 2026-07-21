from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any


QUALITATIVE_HYPOTHESIS_SCHEMA_VERSION = "health-model-qualitative-inquiry-1"

INQUIRY_MODES = {
    "exploratory_question": "Exploratory research question",
    "working_hypothesis": "Exploratory working hypothesis",
    "theory_informed_proposition": "Theory-informed proposition",
    "comparative_proposition": "Comparative proposition across cases or contexts",
    "process_mechanism_proposition": "Process or mechanism proposition",
    "mixed_methods_bridge": "Qualitative proposition linked to quantitative measurements",
}

OBJECT_ROLES = {
    "focal_phenomenon": "Focal phenomenon, experience or practice",
    "construct": "Theoretical construct or concept",
    "actor_group": "People, group or institution",
    "context": "Social, cultural, institutional or situational context",
    "process": "Process, pathway or mechanism",
    "comparison_case": "Comparison case, group or context",
    "outcome_meaning": "Experienced or interpreted outcome",
}

EVIDENCE_ROLES = {
    "empirical_material": "Empirical material to be analysed",
    "prior_empirical_result": "Prior empirical finding",
    "theory_framework": "Theory or conceptual framework",
    "methodological_source": "Methodological source",
    "contextual_source": "Historical, policy or contextual source",
    "counterevidence": "Contradictory or negative-case evidence",
}

EMPIRICAL_ENTITY_TYPES = {
    "qualitative_dataset", "interview_corpus", "focus_group_corpus",
    "document_corpus", "observation_record", "field_notes",
    "questionnaire_result", "measurement_dataset", "parameter_result",
    "analysis_result", "image_video_dataset", "game_result",
}

EXTERNAL_SOURCE_TYPES = {
    "journal_article": "Journal article",
    "book": "Book",
    "book_chapter": "Book chapter",
    "conference_paper": "Conference paper",
    "dataset": "External dataset or archive",
    "policy_document": "Policy or institutional document",
    "historical_document": "Historical document or archive item",
    "theory_framework": "Published theory or conceptual framework",
    "webpage": "Web page",
}

ANALYTIC_APPROACHES = [
    {"method_id": "reflexive_thematic_analysis", "title": "Reflexive thematic analysis", "modes": ["exploratory_question", "working_hypothesis", "comparative_proposition"], "materials": ["interview_corpus", "focus_group_corpus", "document_corpus", "field_notes", "qualitative_dataset", "image_video_dataset"], "output": "themes_with_interpretive_account", "requires_codebook": False},
    {"method_id": "codebook_thematic_analysis", "title": "Codebook thematic analysis", "modes": ["exploratory_question", "working_hypothesis", "comparative_proposition", "mixed_methods_bridge"], "materials": list(EMPIRICAL_ENTITY_TYPES), "output": "coded_segments_categories_and_case_matrix", "requires_codebook": True},
    {"method_id": "framework_analysis", "title": "Framework analysis", "modes": ["theory_informed_proposition", "comparative_proposition", "mixed_methods_bridge"], "materials": list(EMPIRICAL_ENTITY_TYPES), "output": "framework_matrix_and_interpreted_patterns", "requires_codebook": True},
    {"method_id": "qualitative_content_analysis", "title": "Qualitative content analysis", "modes": ["exploratory_question", "theory_informed_proposition", "comparative_proposition"], "materials": ["document_corpus", "interview_corpus", "focus_group_corpus", "field_notes", "qualitative_dataset"], "output": "categories_with_coded_evidence", "requires_codebook": True},
    {"method_id": "grounded_theory_constant_comparison", "title": "Grounded-theory constant comparison", "modes": ["exploratory_question", "working_hypothesis", "process_mechanism_proposition"], "materials": ["interview_corpus", "focus_group_corpus", "field_notes", "observation_record", "qualitative_dataset"], "output": "categories_memos_and_candidate_process_model", "requires_codebook": False},
    {"method_id": "interpretative_phenomenological_analysis", "title": "Interpretative phenomenological analysis", "modes": ["exploratory_question", "working_hypothesis"], "materials": ["interview_corpus", "qualitative_dataset"], "output": "idiographic_experiential_themes", "requires_codebook": False},
    {"method_id": "narrative_analysis", "title": "Narrative analysis", "modes": ["exploratory_question", "working_hypothesis", "process_mechanism_proposition"], "materials": ["interview_corpus", "document_corpus", "historical_document", "qualitative_dataset"], "output": "narrative_structure_and_interpretation", "requires_codebook": False},
    {"method_id": "discourse_analysis", "title": "Discourse analysis", "modes": ["exploratory_question", "theory_informed_proposition"], "materials": ["document_corpus", "interview_corpus", "focus_group_corpus", "historical_document", "qualitative_dataset"], "output": "discursive_patterns_positions_and_context", "requires_codebook": False},
    {"method_id": "case_study_pattern_matching", "title": "Case-study pattern matching", "modes": ["theory_informed_proposition", "comparative_proposition", "process_mechanism_proposition"], "materials": list(EMPIRICAL_ENTITY_TYPES), "output": "predicted_vs_observed_pattern_matrix", "requires_codebook": False},
    {"method_id": "process_tracing", "title": "Process tracing with rival explanations", "modes": ["process_mechanism_proposition", "theory_informed_proposition"], "materials": ["document_corpus", "observation_record", "field_notes", "interview_corpus", "analysis_result"], "output": "evidence_tests_for_causal_process_and_rivals", "requires_codebook": False},
    {"method_id": "qualitative_comparative_analysis_planning", "title": "Qualitative comparative analysis planning", "modes": ["comparative_proposition", "mixed_methods_bridge"], "materials": ["qualitative_dataset", "questionnaire_result", "parameter_result", "analysis_result"], "output": "calibrated_condition_outcome_plan", "requires_codebook": False},
    {"method_id": "joint_display_integration", "title": "Mixed-methods joint display and integration", "modes": ["mixed_methods_bridge"], "materials": ["questionnaire_result", "measurement_dataset", "parameter_result", "analysis_result", "qualitative_dataset", "interview_corpus"], "output": "integrated_joint_display_with_convergence_and_discordance", "requires_codebook": False},
]

TRUSTWORTHINESS_STRATEGIES = {
    "triangulation": "Triangulation across sources, methods, analysts or theories",
    "negative_case_analysis": "Search for negative cases and rival explanations",
    "reflexive_audit_trail": "Reflexive audit trail and decision log",
    "member_reflection": "Participant/member reflection where appropriate",
    "peer_debriefing": "Peer debriefing or analytic challenge",
    "thick_description": "Context-rich description supporting transferability assessment",
    "information_power": "Sampling sufficiency justified by information power",
    "coding_consistency_review": "Coding consistency review when the analytic approach requires it",
}

OUTCOME_STATUSES = {
    "supported": "Supported within the stated material and context",
    "partially_supported": "Partially supported",
    "not_supported": "Not supported",
    "revised": "Revised after analysis",
    "indeterminate": "Indeterminate because evidence or quality is insufficient",
    "generated": "New working hypothesis generated by exploratory analysis",
}


def qualitative_hypothesis_contract() -> dict[str, Any]:
    return {
        "schema_version": QUALITATIVE_HYPOTHESIS_SCHEMA_VERSION,
        "inquiry_modes": deepcopy(INQUIRY_MODES),
        "object_roles": deepcopy(OBJECT_ROLES),
        "evidence_roles": deepcopy(EVIDENCE_ROLES),
        "empirical_entity_types": sorted(EMPIRICAL_ENTITY_TYPES),
        "external_source_types": deepcopy(EXTERNAL_SOURCE_TYPES),
        "analytic_approaches": deepcopy(ANALYTIC_APPROACHES),
        "trustworthiness_strategies": deepcopy(TRUSTWORTHINESS_STRATEGIES),
        "outcome_statuses": deepcopy(OUTCOME_STATUSES),
        "reporting_frameworks": ["SRQR", "COREQ_when_interviews_or_focus_groups_apply"],
        "invariants": [
            "research_question_is_allowed_when_hypothesis_would_bias_exploration",
            "question_definition_is_not_empirical_evidence",
            "time_axis_is_metadata_not_a_focal_phenomenon_unless_time_itself_is_studied",
            "external_source_doi_is_optional_and_never_invented",
            "ray_suggestion_is_not_evidence",
            "interpretation_preserves_source_and_case_context",
            "counterevidence_and_limitations_are_reported",
        ],
    }


def compatible_qualitative_methods(inquiry_mode: str, empirical_types: list[str]) -> list[dict[str, Any]]:
    if inquiry_mode not in INQUIRY_MODES:
        raise ValueError("QUALITATIVE_INQUIRY_MODE_UNSUPPORTED")
    materials = set(empirical_types)
    result = []
    for method in ANALYTIC_APPROACHES:
        reasons = []
        if inquiry_mode not in method["modes"]:
            reasons.append("INQUIRY_MODE_INCOMPATIBLE")
        if materials and not materials.intersection(method["materials"]):
            reasons.append("EMPIRICAL_MATERIAL_INCOMPATIBLE")
        item = deepcopy(method)
        item["compatible"] = not reasons
        item["incompatibility_reasons"] = reasons
        item["execution_status"] = "registered_planning_method_requires_bound_material"
        result.append(item)
    return result


def _source(raw: dict[str, Any]) -> dict[str, Any]:
    origin = str(raw.get("origin") or "registered")
    if origin not in {"registered", "external"}:
        raise ValueError("QUALITATIVE_SOURCE_ORIGIN_UNSUPPORTED")
    role = str(raw.get("evidence_role") or "")
    if role not in EVIDENCE_ROLES:
        raise ValueError("QUALITATIVE_EVIDENCE_ROLE_UNSUPPORTED")
    source_type = str(raw.get("source_type") or "").strip()
    entity_type = str(raw.get("entity_type") or "").strip()
    if origin == "external" and role == "empirical_material":
        entity_type = {
            "dataset": "qualitative_dataset",
            "historical_document": "document_corpus",
            "policy_document": "document_corpus",
        }.get(source_type, entity_type)
    return {
        "origin": origin,
        "evidence_role": role,
        "entity_ref": str(raw.get("entity_ref") or "").strip(),
        "entity_type": entity_type,
        "version": raw.get("version"),
        "title": str(raw.get("title") or "").strip(),
        "source_type": source_type,
        "authors": deepcopy(raw.get("authors") or []),
        "year": str(raw.get("year") or "").strip(),
        "doi": str(raw.get("doi") or "").strip().removeprefix("https://doi.org/"),
        "url": str(raw.get("url") or "").strip(),
        "provenance": deepcopy(raw.get("provenance") or {}),
    }


def build_qualitative_hypothesis_plan(raw: dict[str, Any]) -> dict[str, Any]:
    mode = str(raw.get("inquiry_mode") or "")
    if mode not in INQUIRY_MODES:
        raise ValueError("QUALITATIVE_INQUIRY_MODE_UNSUPPORTED")
    objects = []
    for value in raw.get("objects") or []:
        role = str(value.get("role") or "")
        if role not in OBJECT_ROLES:
            raise ValueError("QUALITATIVE_OBJECT_ROLE_UNSUPPORTED")
        objects.append({
            "role": role, "entity_ref": str(value.get("entity_ref") or "").strip(),
            "entity_type": str(value.get("entity_type") or "").strip(),
            "version": value.get("version"),
            "display_name": str(value.get("display_name") or "").strip(),
            "working_definition": str(value.get("working_definition") or "").strip(),
        })
    sources = [_source(item) for item in raw.get("evidence_sources") or []]
    empirical_types = [item["entity_type"] for item in sources if item["evidence_role"] == "empirical_material"]
    methods = compatible_qualitative_methods(mode, empirical_types)
    method_map = {item["method_id"]: item for item in methods}
    selected_methods = []
    for method_id in dict.fromkeys(raw.get("selected_method_ids") or []):
        if method_id not in method_map:
            raise ValueError("QUALITATIVE_METHOD_UNKNOWN")
        selected_methods.append(deepcopy(method_map[method_id]))
    strategies = list(dict.fromkeys(str(x) for x in raw.get("trustworthiness_strategy_ids") or []))
    if any(item not in TRUSTWORTHINESS_STRATEGIES for item in strategies):
        raise ValueError("QUALITATIVE_TRUSTWORTHINESS_STRATEGY_UNKNOWN")
    issues = []
    if not any(item["role"] in {"focal_phenomenon", "construct", "process"} for item in objects):
        issues.append("FOCAL_PHENOMENON_CONSTRUCT_OR_PROCESS_REQUIRED")
    if not str(raw.get("research_question") or "").strip():
        issues.append("QUALITATIVE_RESEARCH_QUESTION_REQUIRED")
    if mode != "exploratory_question" and not str(raw.get("proposition") or "").strip():
        issues.append("WORKING_HYPOTHESIS_OR_PROPOSITION_REQUIRED")
    empirical_sources = [item for item in sources if item["evidence_role"] == "empirical_material"]
    if not empirical_sources:
        issues.append("EMPIRICAL_MATERIAL_REQUIRED")
    if any(item["entity_type"] not in EMPIRICAL_ENTITY_TYPES for item in empirical_sources):
        issues.append("EMPIRICAL_MATERIAL_TYPE_UNSUPPORTED")
    for source in sources:
        if source["origin"] == "registered" and (not source["entity_ref"] or source["version"] is None):
            issues.append("REGISTERED_SOURCE_ID_AND_VERSION_REQUIRED")
        if source["origin"] == "external":
            if source["source_type"] not in EXTERNAL_SOURCE_TYPES:
                issues.append("EXTERNAL_SOURCE_TYPE_REQUIRED")
            if not source["title"]:
                issues.append("EXTERNAL_SOURCE_TITLE_REQUIRED")
            if source["doi"] and not source["doi"].startswith("10."):
                issues.append("EXTERNAL_SOURCE_DOI_INVALID")
            if source["url"] and not source["url"].startswith(("https://", "http://")):
                issues.append("EXTERNAL_SOURCE_URL_INVALID")
    if mode in {"theory_informed_proposition", "process_mechanism_proposition"} and not any(item["evidence_role"] == "theory_framework" for item in sources):
        issues.append("THEORY_OR_FRAMEWORK_SOURCE_REQUIRED")
    if not selected_methods:
        issues.append("QUALITATIVE_ANALYTIC_APPROACH_REQUIRED")
    if any(not item["compatible"] for item in selected_methods):
        issues.append("SELECTED_QUALITATIVE_METHOD_INCOMPATIBLE")
    if not str(raw.get("disconfirming_evidence_rule") or "").strip():
        issues.append("DISCONFIRMING_EVIDENCE_RULE_REQUIRED")
    if not strategies:
        issues.append("TRUSTWORTHINESS_STRATEGY_REQUIRED")
    result_template = {
        "schema_version": "health-model-qualitative-hypothesis-result-1",
        "hypothesis_or_question_ref": None,
        "outcome_status": None,
        "plain_language_conclusion": "",
        "evidence_links": [], "counterevidence_links": [],
        "themes_categories_or_process_findings": [],
        "context_and_transferability": "", "limitations": [],
        "researcher_reflexivity_note": "", "uncertainty_note": "",
        "method_and_material_versions": [], "completed_at_utc": None,
    }
    return {
        "schema_version": QUALITATIVE_HYPOTHESIS_SCHEMA_VERSION,
        "inquiry_mode": mode,
        "objects": objects,
        "evidence_sources": sources,
        "research_question": str(raw.get("research_question") or "").strip(),
        "proposition": str(raw.get("proposition") or "").strip(),
        "population_or_cases": str(raw.get("population_or_cases") or "").strip(),
        "context": str(raw.get("context") or "").strip(),
        "sampling_strategy": str(raw.get("sampling_strategy") or "").strip(),
        "disconfirming_evidence_rule": str(raw.get("disconfirming_evidence_rule") or "").strip(),
        "compatible_methods": methods,
        "selected_methods": selected_methods,
        "trustworthiness_strategy_ids": strategies,
        "analysis_outputs": [item["output"] for item in selected_methods],
        "workflow": [
            {"phase": "design", "status": "current", "outputs": ["registered_question_or_proposition", "bounded_constructs_and_context"]},
            {"phase": "materials", "status": "pending", "outputs": ["versioned_empirical_corpus", "sampling_and_provenance_record"]},
            {"phase": "analysis", "status": "pending", "outputs": [item["output"] for item in selected_methods]},
            {"phase": "challenge", "status": "pending", "outputs": ["negative_cases", "rival_explanations", "trustworthiness_record"]},
            {"phase": "result", "status": "pending", "outputs": [result_template["schema_version"]]},
        ],
        "result_contract": result_template,
        "readiness": {"valid": not issues, "issues": list(dict.fromkeys(issues))},
        "updated_at": datetime.now(UTC).isoformat(),
    }


def build_qualitative_hypothesis_result(raw: dict[str, Any]) -> dict[str, Any]:
    outcome = str(raw.get("outcome_status") or "")
    if outcome not in OUTCOME_STATUSES:
        raise ValueError("QUALITATIVE_OUTCOME_STATUS_UNSUPPORTED")
    hypothesis_ref = str(raw.get("hypothesis_ref") or "").strip()
    hypothesis_version = raw.get("hypothesis_version")
    conclusion = str(raw.get("plain_language_conclusion") or "").strip()
    if not hypothesis_ref or hypothesis_version in {None, ""}:
        raise ValueError("QUALITATIVE_HYPOTHESIS_ID_AND_VERSION_REQUIRED")
    if not conclusion:
        raise ValueError("QUALITATIVE_RESULT_CONCLUSION_REQUIRED")
    evidence_links = deepcopy(raw.get("evidence_links") or [])
    counterevidence_links = deepcopy(raw.get("counterevidence_links") or [])
    limitations = [str(x).strip() for x in raw.get("limitations") or [] if str(x).strip()]
    issues = []
    if not evidence_links:
        issues.append("RESULT_EVIDENCE_LINK_REQUIRED")
    if outcome in {"supported", "partially_supported"} and not str(raw.get("context_and_transferability") or "").strip():
        issues.append("CONTEXT_AND_TRANSFERABILITY_REQUIRED")
    if not limitations:
        issues.append("RESULT_LIMITATIONS_REQUIRED")
    return {
        "schema_version": "health-model-qualitative-hypothesis-result-1",
        "hypothesis_ref": hypothesis_ref,
        "hypothesis_version": hypothesis_version,
        "outcome_status": outcome,
        "outcome_label": OUTCOME_STATUSES[outcome],
        "plain_language_conclusion": conclusion,
        "evidence_links": evidence_links,
        "counterevidence_links": counterevidence_links,
        "themes_categories_or_process_findings": deepcopy(raw.get("findings") or []),
        "context_and_transferability": str(raw.get("context_and_transferability") or "").strip(),
        "limitations": limitations,
        "researcher_reflexivity_note": str(raw.get("researcher_reflexivity_note") or "").strip(),
        "uncertainty_note": str(raw.get("uncertainty_note") or "").strip(),
        "method_and_material_versions": deepcopy(raw.get("method_and_material_versions") or []),
        "validation": {"valid": not issues, "issues": issues},
        "completed_at_utc": datetime.now(UTC).isoformat(),
    }
