from assessment.measurement.scale_registry import (
    normalize_scale_id,
)


def build_measurement_scales(
    *,
    source_category: str,
    source_definition: dict,
) -> list[str]:
    if source_category == "questionnaire":
        return _build_questionnaire_scales(
            source_definition
        )

    return []


def _build_questionnaire_scales(
    source_definition: dict,
) -> list[str]:
    questions = source_definition.get(
        "questions",
        {},
    )

    detected = set()

    for question in questions.values():

        scale = normalize_scale_id(
            question.get("scale_type")
            or question.get("scale")
            or question.get("measurement_scale")
        )

        if scale:
            detected.add(scale)

    return sorted(detected)
