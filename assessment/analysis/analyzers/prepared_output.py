from assessment.prepared_output import (
    build_prepared_assessment_output,
)


def add_prepared_output(
    assessment_id: str,
    assessment: dict,
    answers: dict,
    result: dict,
) -> dict:
    prepared_output = build_prepared_assessment_output(
        assessment_id=assessment_id,
        question_bank=assessment.get("questions", {}),
        answers=answers,
    )

    result["prepared_output"] = prepared_output

    return result