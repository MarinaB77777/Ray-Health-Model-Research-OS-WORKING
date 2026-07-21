from assessment.questionnaire_components import (
    normalize_question_type_id,
    normalize_response_type_id,
    normalize_scale_type_id,
)
from assessment.measurement.scale_registry import (
    get_scale_definition,
)


def build_data_types(
    *,
    source_category: str,
    source_definition: dict,
) -> list[str]:
    if source_category == "questionnaire":
        return _build_questionnaire_data_types(
            source_definition
        )

    return []


def _build_questionnaire_data_types(
    source_definition: dict,
) -> list[str]:
    questions = source_definition.get(
        "questions",
        {},
    )

    detected = set()

    for question in questions.values():

        question_type = normalize_question_type_id(
            question.get("question_type") or question.get("type")
        )

        answer_type = normalize_response_type_id(
            question.get("answer_type")
            or question.get("response_type")
            or question_type
        )

        scale = normalize_scale_type_id(
            question.get("scale_type") or question.get("scale")
        )
        scale_definition = get_scale_definition(scale)

        if answer_type == "text":
            detected.add("text")

        if answer_type == "numeric":
            detected.add("numeric")

        if (
            question_type in {"multiple_choice", "single_choice"}
            or (
                scale_definition is not None
                and scale_definition["value_structure"] == "category"
            )
        ):
            detected.add("categorical")

        if (
            question_type == "binary"
            or (
                scale_definition is not None
                and scale_definition["numeric_nature"] == "binary"
            )
        ):
            detected.add("boolean")

        if (
            scale_definition is not None
            and scale_definition["measurement_level"] == "ordinal"
        ):
            detected.add("ordinal")

        if (
            scale_definition is not None
            and scale_definition["numeric_nature"]
            not in {"not_numeric", "mixed"}
        ):
            detected.add("numeric")

        if (
            scale_definition is not None
            and scale_definition["value_structure"] == "text"
        ):
            detected.add("text")

    return sorted(detected)
