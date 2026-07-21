from assessment.registry import get_assessment
from question_banks import get_question_bank
from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
    normalize_scale_id,
)


def _title(value, fallback):
    if isinstance(value, dict):
        return value.get("en") or value.get("ru") or value.get("es") or fallback
    return value or fallback


def resolve(connector: dict, context: dict | None = None) -> dict:
    context = context or {}
    lang = context.get("lang", "en")
    assessment_id = connector.get("connector_id")

    assessment = get_assessment(
        assessment_id=assessment_id,
        question_bank=get_question_bank(lang),
    )

    if assessment is None or assessment.get("ok") is False:
        return {
            "metadata_status": "not_found",
            "instrument": {
                "instrument_type": "questionnaire",
                "instrument_name": assessment_id,
                "instrument_version": None,
                "manufacturer": None,
                "device_id": assessment_id,
                "software_version": None,
            },
            "measurement_description": {
                "data_kind": "questionnaire_answers",
                "data_format": None,
                "measurement_scales": [],
                "scale_references": [],
                "observation_profiles": [],
                "unresolved_scale_ids": [],
                "scale_metadata_coverage": None,
                "units": [],
                "variables": [],
                "question_count": None,
                "item_metadata_available": False,
            },
        }

    questions = assessment.get("questions", {}) or {}
    variables = []
    unresolved_scale_ids = set()

    for code, question in questions.items():
        scale_code = normalize_scale_id(
            question.get("scale_type")
            or question.get("scale")
            or question.get("measurement_scale")
        )
        scale_definition = get_scale_definition(scale_code)
        scale_reference = (
            build_scale_reference(scale_code)
            if scale_definition is not None
            else None
        )

        if scale_code and scale_definition is None:
            unresolved_scale_ids.add(scale_code)

        variables.append({
            "code": code,
            "question_type": question.get("question_type") or question.get("type"),
            "answer_type": question.get("answer_type"),
            "scale": scale_code,
            "scale_type": scale_code,
            "scale_reference": scale_reference,
            "score_direction": question.get("score_direction"),
            "domain": question.get("domain"),
            "family": question.get("family"),
            "required": question.get("required", False),
            "active": question.get("active", question.get("status") == "active"),
        })

    return {
        "metadata_status": "resolved",
        "metadata_source": "questionnaire_registry",
        "instrument": {
            "instrument_type": "questionnaire",
            "instrument_name": _title(assessment.get("title"), assessment_id),
            "instrument_version": assessment.get("version"),
            "manufacturer": None,
            "device_id": assessment_id,
            "software_version": None,
        },
        "measurement_description": {
            "data_kind": "questionnaire_answers",
            "data_format": "questionnaire_session",
            "measurement_scales": sorted({
                str(v.get("scale")) for v in variables if v.get("scale")
            }),
            "scale_references": [
                v["scale_reference"]
                for v in variables
                if v.get("scale_reference") is not None
            ],
            "observation_profiles": [],
            "unresolved_scale_ids": sorted(unresolved_scale_ids),
            "scale_metadata_coverage": (
                sum(
                    1
                    for variable in variables
                    if variable.get("scale_reference") is not None
                ) / len(variables)
                if variables
                else None
            ),
            "units": [],
            "sampling_rate": None,
            "temporal_resolution": None,
            "spatial_resolution": None,
            "variables": variables,
            "question_count": len(questions),
            "item_metadata_available": True,
        },
        "quality": {
            "quality_status": (
                "metadata_incomplete"
                if any(
                    variable.get("scale_type") is None
                    for variable in variables
                )
                or unresolved_scale_ids
                else "metadata_complete"
            ),
            "quality_flags": [
                flag
                for flag, present in (
                    (
                        "question_scale_metadata_missing",
                        any(
                            variable.get("scale_type") is None
                            for variable in variables
                        ),
                    ),
                    (
                        "question_scale_id_unresolved",
                        bool(unresolved_scale_ids),
                    ),
                )
                if present
            ],
        },
    }
