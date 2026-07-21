import os
from datetime import UTC, datetime
from uuid import uuid4

from pilot_session.schemas import (
    ParticipantSession,
    SessionStatus,
)

from research.answer_export_filter import (
    filter_answers_for_research_snapshot,
)

from research.snapshot_sanitizer import (
    sanitize_acquisition_requests,
    sanitize_next_questions,
)

from assessment.prepared_output import (
    build_prepared_domain_output,
)

from research.pseudonymization import (
    build_export_scoped_participant_reference,
)


SNAPSHOT_SCHEMA_VERSION = "research-snapshot-1"
SNAPSHOT_BUILDER_VERSION = "research-snapshot-builder-1"

DEFAULT_PSEUDONYMIZATION_SCOPE = "research_snapshot"
PSEUDONYMIZATION_SALT_ENV = "RESEARCH_PSEUDONYMIZATION_SALT"


ALLOWED_SOURCE_STATUSES = {
    SessionStatus.RUN_COMPLETED,
    SessionStatus.EXPORT_READY,
    SessionStatus.CLOSED,
}


def _get_pseudonymization_salt() -> str:
    salt = os.getenv(PSEUDONYMIZATION_SALT_ENV)

    if not salt:
        raise ValueError(
            f"{PSEUDONYMIZATION_SALT_ENV} is required"
        )

    return salt


def _has_public_output(session: ParticipantSession) -> bool:
    return bool(session.public_output)


def _is_invalidated(session: ParticipantSession) -> bool:
    return (
        session.invalidated
        or session.status == SessionStatus.INVALIDATED
    )


def _build_snapshot_policy_status(
    session: ParticipantSession,
    policy_status_override: dict | None = None,
) -> dict:
    invalidated = _is_invalidated(session)

    base = {
        "policy_evaluation": "preliminary_builder_evaluation",
        "retention_status": "not_evaluated",
        "consent_status": "not_evaluated",
        "policy_restricted": "not_evaluated",
    }

    if policy_status_override:
        base = {
            **base,
            **policy_status_override,
            "policy_status_override_applied": True,
        }
    else:
        base["policy_status_override_applied"] = False

    if invalidated:
        return {
            **base,
            "snapshot_status": "invalidated",
            "usable_for_research_preliminary": False,
            "exclusion_status": "excluded_invalidated",
        }

    if session.status not in ALLOWED_SOURCE_STATUSES:
        return {
            **base,
            "snapshot_status": "blocked",
            "usable_for_research_preliminary": False,
            "exclusion_status": "blocked_source_status",
        }

    if not _has_public_output(session):
        return {
            **base,
            "snapshot_status": "partial",
            "usable_for_research_preliminary": False,
            "exclusion_status": "missing_public_output",
        }

    return {
        **base,
        "snapshot_status": "usable_preliminary",
        "usable_for_research_preliminary": True,
        "exclusion_status": "not_evaluated",
    }


def _build_forecast_summary(public_output: dict) -> dict:
    forecast = public_output.get("forecast")

    if not forecast:
        return {
            "forecast_status": "missing",
            "allowed": None,
            "reason": None,
            "confidence": None,
            "allowed_scope": None,
        }

    allowed = forecast.get("allowed")

    if allowed is True:
        status = "allowed"
    elif allowed is False:
        status = "blocked"
    else:
        status = "present_unknown_allowed_state"

    return {
        "forecast_status": status,
        "allowed": allowed,
        "reason": forecast.get("reason"),
        "confidence": forecast.get("confidence"),
        "allowed_scope": forecast.get("allowed_scope"),
    }


def _build_uncertainty_summary(session: ParticipantSession) -> dict:
    uncertainty = session.uncertainty_snapshot or {}

    if not uncertainty:
        return {
            "uncertainty_status": "missing",
            "uncertainty_score": None,
            "uncertainty_level": None,
            "allow_recommendations": None,
            "allow_strong_recommendations": None,
            "dialogue_mode": None,
        }

    return {
        "uncertainty_status": "present",
        "uncertainty_score": uncertainty.get("uncertainty_score"),
        "uncertainty_level": uncertainty.get("uncertainty_level"),
        "allow_recommendations": uncertainty.get("allow_recommendations"),
        "allow_strong_recommendations": uncertainty.get(
            "allow_strong_recommendations"
        ),
        "dialogue_mode": uncertainty.get("dialogue_mode"),
    }


def _build_operational_summary(public_output: dict) -> dict:
    domain_summary = public_output.get("domain_summary", {})

    if domain_summary:
        calculation_status = "present"
    elif public_output:
        calculation_status = "missing_domain_summary"
    else:
        calculation_status = "missing_public_output"

    return {
        "summary_text": public_output.get("summary_text"),
        "result_level": public_output.get("result_level"),
        "calculation_status": calculation_status,
        "domain_summary": domain_summary,
        "public_warnings": public_output.get("warnings", []),
        "public_warnings_source": "public_output.warnings",
        "public_reasons": public_output.get("public_reasons", []),
    }


def _build_acquisition_summary(session: ParticipantSession) -> dict:
    sanitized_next_questions = sanitize_next_questions(
        session.next_question_snapshots or []
    )
    sanitized_acquisition_requests = sanitize_acquisition_requests(
        session.acquisition_request_snapshots or {}
    )

    return {
        "next_questions": sanitized_next_questions,
        "data_acquisition_requests": sanitized_acquisition_requests,
        "next_questions_status": (
            "present"
            if sanitized_next_questions
            else "missing_or_empty_after_sanitization"
        ),
        "data_acquisition_requests_status": (
            "present"
            if sanitized_acquisition_requests
            else "missing_or_empty_after_sanitization"
        ),
        "research_safety_status": "bounded_allowlist_sanitized",
        "payload_safety_status": (
            "bounded_allowlist_sanitized_no_deep_semantic_sanitizer"
        ),
    }


def _build_answer_summary(session: ParticipantSession) -> dict:
    if not session.answers:
        return {
            "answer_integration_status": "missing_or_empty",
            "answer_export_result": None,
            "builder_consumed_raw_answers_directly": False,
            "builder_is_not_answer_policy_authority": True,
            "builder_is_not_consent_authority": True,
            "builder_is_not_retention_authority": True,
        }

    answer_export_result = filter_answers_for_research_snapshot(
        session.answers
    )

    return {
        "answer_integration_status": "filter_applied",
        "answer_export_result": answer_export_result,
        "builder_consumed_raw_answers_directly": False,
        "builder_is_not_answer_policy_authority": True,
        "builder_is_not_consent_authority": True,
        "builder_is_not_retention_authority": True,
    }
def _build_domain_data_identity_summary(session: ParticipantSession) -> dict:
    identity = session.domain_data_identity or {}

    if not identity:
        return {
            "identity_status": "missing",
            "domain_data_identity": {},
        }

    return {
        "identity_status": "present",
        "domain_data_identity": identity,
    }
def _build_health_model_research_model_summary(
    session: ParticipantSession,
) -> dict:
    raw_result = session.raw_engine_result or {}

    return {
        "status": (
            "present"
            if raw_result
            else "missing"
        ),
        "calculator_input": raw_result.get("calculator_input", {}),
        "coverage": raw_result.get("coverage", {}),
        "question_parameter_mapping_records": raw_result.get(
            "question_parameter_mapping_records",
            [],
        ),
        "research_calculated_parameter_records": raw_result.get(
            "research_calculated_parameter_records",
            [],
        ),
    }
def build_research_snapshot(
    session: ParticipantSession,
    policy_status_override: dict | None = None,
) -> dict:
    public_output = session.public_output or {}
    invalidated = _is_invalidated(session)

    pseudonymization_salt = _get_pseudonymization_salt()

    return {
        "snapshot_id": str(uuid4()),
        "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION,
        "snapshot_builder_version": SNAPSHOT_BUILDER_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "research.snapshot_builder",
        "created_from": "ParticipantSession",
        "snapshot_mode": "research",
        "snapshot_scope": "bounded_research_snapshot",

        "snapshot_policy_status": (
            _build_snapshot_policy_status(
                session=session,
                policy_status_override=policy_status_override,
            )
        ),

        "source_session": {
            "session_id": session.session_id,
            "source_session_status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "closed_at": (
                session.closed_at.isoformat()
                if session.closed_at is not None
                else None
            ),
            "study_id": session.study_id,
            "participant_role": session.participant_role,
            "synchronization_reference": session.synchronization_reference,
            "subject_link_present": session.subject_link_id is not None,
            "invalidated": invalidated,
            "invalidation_reason": session.invalidation_reason,
         },

        "versions": {
            "engine_version": session.engine_version,
            "engine_snapshot_schema_version": (
                session.engine_snapshot_schema_version
            ),
            "public_output_schema_version": (
                session.public_output_schema_version
            ),
            "export_schema_version": session.export_schema_version,
            "export_policy_version": session.export_policy_version,
        },

        "participant_reference": (
            build_export_scoped_participant_reference(
                participant_id=session.participant_id,
                export_scope=DEFAULT_PSEUDONYMIZATION_SCOPE,
                salt=pseudonymization_salt,
            )
        ),

        "operational_summary": (
            _build_operational_summary(public_output)
        ),

        "forecast_summary": (
            _build_forecast_summary(public_output)
        ),

        "uncertainty_summary": (
            _build_uncertainty_summary(session)
        ),

        "acquisition_summary": (
            _build_acquisition_summary(session)
        ),

        "answer_summary": (
            _build_answer_summary(session)
        ),

        "domain_data_identity_summary": (
            _build_domain_data_identity_summary(session)
        ),

        "sensor_summary": {
            "status": "not_implemented",
        },

        "standard_method_summary": {
            "status": "not_implemented",
        },

        "health_model_research_model_summary": (
           _build_health_model_research_model_summary(session)
        ),

        "prepared_domain_output": build_prepared_domain_output(
            domain_data_identity=session.domain_data_identity or {},
            raw_payload={
                "payload_type": "questionnaire_answers",
                "study_id": session.study_id,
                "answers": session.answers or {},
            },
            analysis_output=session.raw_engine_result or {},
         ),

        "decision_pattern_summary": {
            "status": "not_implemented",
        },

        "payload_safety": {
            "payload_safety_status": (
                "bounded_extraction_with_allowlist_sanitizer"
            ),
            "public_output_extracted_field_by_field": True,
            "acquisition_payload_allowlist_sanitized": True,
            "next_questions_allowlist_sanitized": True,
            "acquisition_payload_deep_sanitized": False,
            "next_questions_deep_sanitized": False,
            "answer_values_policy_filtered": True,
            "answer_values_not_transformed": True,
            "answer_values_not_deep_sanitized": True,
            "raw_answers_not_directly_included": True,
            "answers_included_only_via_answer_export_filter": True,
        },

        "research_interpretation_boundaries": {
            "no_diagnosis": True,
            "no_identity_inference": True,
            "no_authority": True,
            "not_participant_truth": True,
            "not_clinical_record": True,
            "not_longitudinal_profile": True,
        },

        "limitations": {
            "raw_engine_result_excluded": True,
            "raw_answers_excluded": True,
            "filtered_answer_summary_included": True,
            "answer_values_may_be_included_only_after_policy_filter": True,
            "answer_values_not_transformed": True,
            "answer_values_not_deep_sanitized": True,
            "raw_answers_not_directly_included": True,
            "answers_included_only_via_answer_export_filter": True,
            "answer_filter_output_not_final_export_authorization": True,
            "answer_filter_output_not_consent_resolution": True,
            "answer_filter_output_not_retention_resolution": True,
            "raw_answers_policy": (
                "answers_may_enter_only_through_bounded_answer_export_filter"
            ),
            "unrestricted_runtime_state_excluded": True,
            "snapshot_is_not_runtime_memory": True,
            "research_snapshot_not_participant_truth": True,
            "no_longitudinal_aggregation": True,
            "builder_is_not_export_authority": True,
            "builder_is_not_research_analysis": True,
            "builder_is_not_answer_policy_authority": True,
            "builder_is_not_consent_authority": True,
            "builder_is_not_retention_authority": True,
            "schema_is_not_serialization_contract": True,
            "participant_reference_pseudonymized": True,
            "pseudonymization_salt_not_exported": True,
            "pseudonymization_salt_source": "environment_variable",
            "research_export_policy_not_final": True,
            "acquisition_payload_deep_sanitizer_missing": True,
            "next_questions_bounded_schema_not_verified": True,
        },
    }