DATA_DESCRIPTION_SCHEMA_VERSION = (
    "data-description"
)


def build_data_description(
    *,
    source_category: str,
    source_definition: dict,
) -> dict:
    if source_category == "questionnaire":
        return _build_questionnaire_description(
            source_definition
        )

    raise ValueError(
        f"Unsupported source category: {source_category}"
    )


def _build_questionnaire_description(
    source_definition: dict,
) -> dict:
    questions = source_definition.get(
        "questions",
        {},
    )

    question_descriptions = []

    for question_id, question in questions.items():
        question_descriptions.append(
            {
                "question_id": question_id,
                "question_type": question.get(
                    "question_type"
                ),
                "measurement_scale": question.get(
                    "scale"
                ),
                "answer_type": question.get(
                    "answer_type"
                ),
                "scale_definition": {
                    "minimum": question.get(
                        "min_value"
                    ),
                    "maximum": question.get(
                        "max_value"
                    ),
                    "labels": question.get(
                        "scale_labels"
                    ),
                },
                "score_direction": question.get(
                    "score_direction"
                ),
                "domain": question.get(
                    "domain"
                ),
                "family": question.get(
                    "family"
                ),
                "required": question.get(
                    "required",
                    False,
                ),
                "active": question.get(
                    "active",
                    question.get("status") == "active",
                ),
                "transition_logic": question.get(
                    "transition_logic"
                ),
            }
        )

    return {
        "schema_version": DATA_DESCRIPTION_SCHEMA_VERSION,
        "source_category": "questionnaire",
        "question_count": len(
            question_descriptions
        ),
        "questions": question_descriptions,
    }