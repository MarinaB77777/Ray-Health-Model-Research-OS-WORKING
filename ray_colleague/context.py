from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import PageContext, RayRole, normalize_language


@dataclass(frozen=True)
class PageCapability:
    page_id: str
    researcher_capabilities: tuple[str, ...]
    participant_capabilities: tuple[str, ...] = ()


PAGE_CAPABILITIES: dict[str, PageCapability] = {
    "research_workspace": PageCapability(
        "research_workspace",
        (
            "review_research_intent",
            "track_open_question",
            "track_project_decision",
            "track_research_risk",
            "navigate_research_workflow",
        ),
    ),
    "research_lab": PageCapability(
        "research_lab",
        (
            "review_hypothesis_basis",
            "review_variable_roles",
            "review_falsifiability",
            "review_time_relation",
            "review_analysis_readiness",
        ),
    ),
    "model_parameter_constructor": PageCapability(
        "model_parameter_constructor",
        (
            "review_parameter_contract",
            "review_mechanism_contract",
            "review_measurement_binding",
            "review_time_binding",
            "review_calculation_rule",
        ),
    ),
    "data_preparation": PageCapability(
        "data_preparation",
        (
            "review_dataset_selection",
            "review_analysis_compatibility",
            "review_statistical_assumptions",
            "review_time_alignment",
        ),
    ),
    "data_editor": PageCapability(
        "data_editor",
        (
            "profile_input_format",
            "review_missingness",
            "review_noise_and_outliers",
            "recommend_normalization",
            "review_time_binding",
        ),
    ),
    "measurement_setup": PageCapability(
        "measurement_setup",
        (
            "review_browser_device_capability",
            "review_device_identity",
            "review_permission_state",
            "prepare_official_driver_search",
            "review_measurement_time_binding",
        ),
    ),
    "model_training": PageCapability(
        "model_training",
        (
            "review_training_sources",
            "review_source_mask_pairing",
            "review_independent_group_split",
            "review_training_configuration",
            "review_validation_and_test_policy",
            "prepare_colab_training_run",
        ),
    ),
    "fiji_integration": PageCapability(
        "fiji_integration",
        (
            "review_fiji_installation",
            "review_image_metadata",
            "review_processing_pipeline",
            "review_operation_parameters",
            "review_image_time_binding",
            "review_processing_provenance",
            "guide_fiji_interactive_work",
        ),
    ),
    "scientific_results": PageCapability(
        "scientific_results",
        (
            "review_result_provenance",
            "review_method_trace",
            "review_quality_limitations",
            "review_claim_support",
        ),
    ),
    "research_participant": PageCapability(
        "research_participant",
        (
            "review_participant_record_provenance",
            "review_longitudinal_time",
        ),
        (
            "explain_own_session",
            "explain_own_tasks",
            "explain_own_report",
        ),
    ),
    "assessment": PageCapability(
        "assessment",
        ("review_measurement_session",),
        (
            "explain_current_question",
            "explain_response_format",
            "request_clarification",
        ),
    ),
    "pilot": PageCapability(
        "pilot",
        ("review_pilot_flow",),
        (
            "explain_current_question",
            "explain_session_progress",
            "request_clarification",
        ),
    ),
    "consent": PageCapability(
        "consent",
        ("review_consent_flow",),
        (
            "explain_consent",
            "explain_data_use",
            "request_clarification",
        ),
    ),
}


PARTICIPANT_FORBIDDEN_SELECTION_KEYS = {
    "aggregate_results",
    "all_participants",
    "author_private_notes",
    "model_internal_state",
    "project_private_notes",
    "raw_other_participant_data",
    "researcher_workspace",
}

CLIENT_FORBIDDEN_RAW_KEYS = {
    "raw_answers",
    "raw_sensor_stream",
    "raw_video",
    "secret",
    "token",
    "password",
}


def _find_forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in CLIENT_FORBIDDEN_RAW_KEYS:
                found.add(normalized)
            found.update(_find_forbidden_keys(nested))
    elif isinstance(value, (list, tuple)):
        for nested in value:
            found.update(_find_forbidden_keys(nested))
    return found


class RayContextResolver:
    def contract(self) -> dict[str, Any]:
        return {
            "version": "ray-colleague-context-1",
            "roles": [role.value for role in RayRole],
            "languages": ["ru", "en", "es"],
            "pages": {
                page_id: {
                    "research_colleague": list(item.researcher_capabilities),
                    "participant_guide": list(item.participant_capabilities),
                }
                for page_id, item in PAGE_CAPABILITIES.items()
            },
            "invariants": [
                "unknown_is_not_zero",
                "hypothesis_is_not_fact",
                "memory_is_not_authority",
                "access_is_not_permission",
                "participant_and_researcher_memory_are_isolated",
                "all_events_use_utc",
            ],
        }

    def resolve(
        self,
        *,
        role: RayRole,
        owner_id: str,
        page_id: str,
        language: str,
        session_id: str | None = None,
        project_id: str | None = None,
        study_id: str | None = None,
        entity_refs: list[str] | None = None,
        selection: dict[str, Any] | None = None,
    ) -> PageContext:
        owner = owner_id.strip()
        if not owner:
            raise ValueError("OWNER_ID_REQUIRED")

        page = PAGE_CAPABILITIES.get(page_id.strip())
        if page is None:
            raise ValueError("UNKNOWN_PAGE_CONTEXT")

        selected = dict(selection or {})
        forbidden_raw = _find_forbidden_keys(selected)
        if forbidden_raw:
            raise ValueError(
                "RAW_OR_SECRET_CLIENT_CONTEXT_FORBIDDEN:"
                + ",".join(sorted(forbidden_raw))
            )

        if role == RayRole.PARTICIPANT_GUIDE:
            if not session_id:
                raise ValueError("PARTICIPANT_SESSION_ID_REQUIRED")
            forbidden = PARTICIPANT_FORBIDDEN_SELECTION_KEYS.intersection(selected)
            if forbidden:
                raise PermissionError(
                    "PARTICIPANT_CONTEXT_FORBIDDEN:"
                    + ",".join(sorted(forbidden))
                )
            capabilities = page.participant_capabilities
            if not capabilities:
                raise PermissionError("PAGE_NOT_AVAILABLE_TO_PARTICIPANT_GUIDE")
        else:
            capabilities = page.researcher_capabilities

        refs = tuple(dict.fromkeys(str(ref) for ref in (entity_refs or []) if str(ref)))
        return PageContext(
            role=role,
            owner_id=owner,
            page_id=page.page_id,
            language=normalize_language(language),
            session_id=session_id,
            project_id=project_id,
            study_id=study_id,
            entity_refs=refs,
            selection=selected,
            allowed_capabilities=capabilities,
        )
