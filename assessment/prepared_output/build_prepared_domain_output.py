from uuid import uuid4


PREPARED_OUTPUT_SCHEMA_VERSION = "prepared-domain-output-1"


def build_prepared_domain_output(
    *,
    domain_data_identity: dict,
    raw_payload: dict,
    analysis_output: dict,
) -> dict:
    answers = raw_payload.get("answers", {}) or {}
    answer_count = len(answers)
    analysis_present = bool(analysis_output)

    return {
        "schema_version": PREPARED_OUTPUT_SCHEMA_VERSION,
        "prepared_output_id": str(uuid4()),

        "domain_id": domain_data_identity.get("domain_id"),
        "source_type": domain_data_identity.get("source_type"),
        "study_id": (
            domain_data_identity.get("study_id")
            or raw_payload.get("study_id")
       ),
        "session_id": domain_data_identity.get("session_id"),
        "participant_id": domain_data_identity.get("participant_id"),

        "collection_metadata": {
            "collection_started_at": domain_data_identity.get("collection_started_at"),
            "collection_finished_at": domain_data_identity.get("collection_finished_at"),
            "global_time_reference": domain_data_identity.get("global_time_reference"),
        },

        "data_reference": {
            "data_source_path": domain_data_identity.get("data_source_path"),
            "storage_type": "research_record",
            "data_format": raw_payload.get("payload_type"),
            "data_checksum": None,
        },

        "provenance": {
            "created_by": "domain_preparation_builder",
            "created_at": None,
            "preparation_version": "1.0",
            "model_version": None,
            "software_version": "1.0",
            "source_version": None,
        },

        "permission_status": {
            "collection_allowed": True,
            "analysis_allowed": True,
            "research_allowed": True,
        },

        "calibration": {
            "calibration_required": False,
            "calibration_available": False,
            "calibration_reference_id": None,
            "calibration_confidence": None,
            "calibration_freshness": "not_applicable",
            "context_match": "not_applicable",
        },

        "handoff": {
            "handoff_ready": analysis_present,
            "handoff_target": "analyzer_constructor",
            "allowed_analysis_types": ["questionnaire_analysis"],
            "blocked_analysis_types": [],
            "handoff_notes": [],
        },

        "quality": {
            "quality_status": "preliminary",
            "quality_score": None,
            "quality_flags": [],
            "invalid_items": [],
            "skipped_items": [],
            "not_scorable_items": [],
        },

        "coverage": {
            "coverage_score": None,
            "expected_item_count": None,
            "available_item_count": answer_count,
            "used_item_count": answer_count,
            "missing_item_count": None,
        },
        
        "prepared_payload": {
            "payload_type": raw_payload.get("payload_type"),
            "study_id": (
                domain_data_identity.get("study_id")
                or raw_payload.get("study_id")
        ),
            "answer_count": answer_count,
            "analysis_output_present": analysis_present,

            # New canonical field
            "domain_output": analysis_output,

            # Legacy compatibility.
            # TODO: remove after all analyzers migrate to domain_output.
            "analysis_output": analysis_output,
        },

        "raw_data_included": False,
    }