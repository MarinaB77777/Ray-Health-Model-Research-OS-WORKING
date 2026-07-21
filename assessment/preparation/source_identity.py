SOURCE_IDENTITY_SCHEMA_VERSION = "source-identity-1"


def build_source_identity(
    assessment: dict,
    session: dict,
) -> dict:
    """
    Block 1.

    Creates a unique scientific identity for the collected dataset.

    This block identifies WHERE, WHEN and WHAT produced the data.

    It does not describe the data itself.
    """

    assessment = assessment or {}
    session = session or {}

    return {
        "schema_version": SOURCE_IDENTITY_SCHEMA_VERSION,

        # ---- Source identity ----
        "domain_id": assessment.get("domain_id"),
        "source_category": assessment.get("source_category"),
        "source_type": assessment.get("source_type"),
        "data_structure_type": assessment.get("data_structure_type"),

        # ---- Dataset identity ----
        "assessment_id": assessment.get("assessment_id"),
        "session_id": session.get("session_id"),
        "participant_id": session.get("participant_id"),

        # ---- Time ----
        "collection_started_at": session.get("collection_started_at"),
        "collection_finished_at": session.get("collection_finished_at"),
        "shared_time_reference": session.get("shared_time_reference"),

        # ---- Provenance ----
        "study_id": session.get("study_id"),
        "protocol_id": session.get("protocol_id"),
        "site_id": session.get("site_id"),
        "device_id": session.get("device_id"),

        # ---- Versioning ----
        "assessment_version": assessment.get("version"),
        "question_bank_version": assessment.get("question_bank_version"),
    }