QUESTIONNAIRE_DESCRIPTION_SCHEMA_VERSION = "questionnaire-description-1"

from assessment.questionnaire_components import (
    get_scale_type,
    get_question_type,
    get_response_type,
    is_question_type_compatible_with_scale,
    is_response_type_compatible_with_scale,
    normalize_question_type_id,
    normalize_response_type_id,
    normalize_scale_type_id,
)

def _build_scale(question: dict) -> dict:
    scale_type_id = normalize_scale_type_id(
        question.get("scale_type") or question.get("scale")
    )
    scale_type = get_scale_type(scale_type_id)

    if scale_type is None:
        return {
            "scale_type": scale_type_id,
            "measurement_scale": None,
            "default_representation": None,
            "registered": False,
            "min": question.get("min"),
            "max": question.get("max"),
            "step": question.get("step"),
            "labels": question.get("labels"),
            "direction": question.get("score_direction"),
            "unit": question.get("unit"),
        }

    return {
        "scale_type": scale_type["id"],
        "measurement_scale": scale_type["measurement_scale"],
        "default_representation": scale_type["default_representation"],
        "registered": True,
        "min": question.get("min"),
        "max": question.get("max"),
        "step": question.get("step"),
        "labels": question.get("labels"),
        "direction": question.get("score_direction"),
        "unit": question.get("unit"),
    }


def _question_component_status(question: dict) -> dict:
    question_type_id = normalize_question_type_id(
        question.get("question_type") or question.get("type")
    )
    response_type_id = normalize_response_type_id(
        question.get("response_type")
        or question.get("answer_type")
        or question_type_id
    )
    scale_type_id = normalize_scale_type_id(
        question.get("scale_type") or question.get("scale")
    )

    question_type = get_question_type(question_type_id)
    response_type = get_response_type(response_type_id)
    scale_type = get_scale_type(scale_type_id)

    return {
        "question_type_registered": question_type is not None,
        "response_type_registered": response_type is not None,
        "scale_type_registered": scale_type is not None,
        "question_type_scale_compatible": (
            is_question_type_compatible_with_scale(
                question_type_id=question_type_id,
                scale_type_id=scale_type_id,
            )
            if question_type_id and scale_type_id
            else False
        ),
        "response_type_scale_compatible": (
            is_response_type_compatible_with_scale(
                response_type_id=response_type_id,
                scale_type_id=scale_type_id,
            )
            if response_type_id and scale_type_id
            else False
        ),
    }


def _build_transition(question: dict) -> dict:
    return {
        "transition_type": question.get("transition_type", "sequential"),
        "next_question_id": question.get("next_question_id"),
        "condition": question.get("condition"),
    }


def _answer_status(code: str, question: dict, answers: dict) -> str:
    if code not in answers:
        return "ANSWER_MISSING"

    value = answers.get(code)

    if value is None:
        return "ANSWER_MISSING"

    return "ANSWERED"


def build_questionnaire_description(
    assessment: dict,
    session: dict,
    answers: dict,
) -> dict:
    assessment = assessment or {}
    session = session or {}
    answers = answers or {}

    question_bank = assessment.get("questions", {})
    question_records = []

    for code, question in question_bank.items():
        if not question.get("active", question.get("status") == "active"):
            continue

        question_records.append({
            "question_block": question.get("block") or question.get("domain"),
            "question_number_in_block": question.get("number_in_block"),
            "question_id": code,
            "question_version": question.get("version"),
            "question_type": normalize_question_type_id(
                question.get("question_type") or question.get("type")
            ),
            "response_type": normalize_response_type_id(
                question.get("response_type")
                or question.get("answer_type")
                or question.get("question_type")
                or question.get("type")
            ),
            "scale": _build_scale(question),
            "component_status": _question_component_status(question),
            "answer": answers.get(code),
            "answer_status": _answer_status(code, question, answers),
            "transition": _build_transition(question),
        })

    return {
        "schema_version": QUESTIONNAIRE_DESCRIPTION_SCHEMA_VERSION,
        "questionnaire_id": assessment.get("assessment_id"),
        "questionnaire_version": assessment.get("version"),
        "questionnaire_completion_id": session.get("session_id"),
        "attempt_number": session.get("attempt_number"),
        "attempt_started_at": session.get("collection_started_at"),
        "attempt_finished_at": session.get("collection_finished_at"),
        "previous_attempt_id": session.get("previous_attempt_id"),
        "time_since_previous_attempt": session.get("time_since_previous_attempt"),
        "questions": question_records,
        "normalization_performed": False,
        "analysis_performed": False,
    }
