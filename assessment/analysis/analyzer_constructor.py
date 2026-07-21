from assessment.prepared_output import (
    build_prepared_assessment_output,
)


ANALYZER_CONSTRUCTOR_SCHEMA_VERSION = "analyzer-constructor-1"


DEFAULT_ANALYZER_STEPS = [
    "prepared_output",
]


def build_analyzer_pipeline(
    assessment: dict,
) -> list[str]:
    if not isinstance(assessment, dict):
        return DEFAULT_ANALYZER_STEPS.copy()

    analysis_config = assessment.get("analysis", {})

    if not isinstance(analysis_config, dict):
        return DEFAULT_ANALYZER_STEPS.copy()

    steps = analysis_config.get("steps")

    if not isinstance(steps, list) or not steps:
        return DEFAULT_ANALYZER_STEPS.copy()

    return [
        step
        for step in steps
        if step in DEFAULT_ANALYZER_STEPS
    ] or DEFAULT_ANALYZER_STEPS.copy()


def run_constructed_analyzer(
    assessment_id: str,
    assessment: dict,
    answers: dict,
) -> dict:
    pipeline = build_analyzer_pipeline(assessment)

    result = {
        "schema_version": ANALYZER_CONSTRUCTOR_SCHEMA_VERSION,
        "assessment_id": assessment_id,
        "pipeline": pipeline,
        "outputs": {},
    }

    if "prepared_output" in pipeline:
        prepared_output = build_prepared_assessment_output(
            assessment_id=assessment_id,
            question_bank=assessment.get("questions", {}),
            answers=answers,
        )

        result["outputs"]["prepared_output"] = prepared_output

    return result

REQUIRED_PREPARED_OUTPUT_SECTIONS = {
    "schema_version",
    "prepared_output_id",
    "domain_id",
    "source_type",
    "study_id",
    "session_id",
    "participant_id",
    "collection_metadata",
    "quality",
    "coverage",
    "calibration",
    "prepared_payload",
    "handoff",
    "raw_data_included",
}


def build_analyzer_input_from_prepared_outputs(
    prepared_outputs: list[dict],
) -> dict:
    accepted_outputs = []
    rejected_outputs = []

    for output in prepared_outputs:
        missing_sections = [
            section
            for section in REQUIRED_PREPARED_OUTPUT_SECTIONS
            if section not in output
        ]

        if missing_sections:
            rejected_outputs.append({
                "prepared_output_id": output.get("prepared_output_id"),
                "reason": "MISSING_REQUIRED_SECTIONS",
                "missing_sections": missing_sections,
            })
            continue

        if output.get("raw_data_included") is True:
            rejected_outputs.append({
                "prepared_output_id": output.get("prepared_output_id"),
                "reason": "RAW_DATA_INCLUDED",
            })
            continue

        handoff = output.get("handoff", {})

        if handoff.get("handoff_ready") is not True:
            rejected_outputs.append({
                "prepared_output_id": output.get("prepared_output_id"),
                "reason": "HANDOFF_NOT_READY",
                "handoff": handoff,
            })
            continue

        accepted_outputs.append(output)

    return {
        "schema_version": "analyzer-input-1",
        "input_source": "prepared_domain_outputs",
        "accepted_prepared_outputs": accepted_outputs,
        "rejected_prepared_outputs": rejected_outputs,
        "accepted_count": len(accepted_outputs),
        "rejected_count": len(rejected_outputs),
    }

def construct_analyzer_objects(
    analyzer_input: dict,
) -> dict:
    accepted = analyzer_input.get(
        "accepted_prepared_outputs",
        [],
    )

    analyzer_objects = []

    for prepared_output in accepted:
        analyzer_objects.append(
            {
                "prepared_output_id": prepared_output.get(
                    "prepared_output_id"
                ),
                "domain_id": prepared_output.get(
                    "domain_id"
                ),
                "study_id": prepared_output.get(
                    "study_id"
                ),
                "participant_id": prepared_output.get(
                    "participant_id"
                ),
                "session_id": prepared_output.get(
                    "session_id"
                ),
                "quality": prepared_output.get(
                    "quality"
                ),
                "coverage": prepared_output.get(
                    "coverage"
                ),
                "calibration": prepared_output.get(
                    "calibration"
                ),
                "prepared_payload": prepared_output.get(
                    "prepared_payload"
                ),
            }
        )

    return {
        "schema_version": "analyzer-constructor-1",
        "input_schema": analyzer_input.get(
            "schema_version"
        ),
        "analyzer_object_count": len(
            analyzer_objects
        ),
        "analyzer_objects": analyzer_objects,
    }