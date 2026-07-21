from assessment.questionnaire_components import get_scale_type


QUESTIONNAIRE_PREPARATION_SCHEMA_VERSION = "questionnaire-preparation-1"


def _profile_for_scale(scale: dict) -> str:
    if not scale.get("registered"):
        return "unknown_profile"

    scale_type_id = scale.get("scale_type")

    if scale_type_id == "likert":
        return "likert_item_profile"

    return f"{scale_type_id}_profile"


def _representation_for_scale(scale: dict) -> str:
    scale_type = get_scale_type(scale.get("scale_type"))

    if scale_type is None:
        return "unknown_representation"

    return scale_type["default_representation"]


def _prepare_answer(question_record: dict) -> dict:
    scale = question_record.get("scale") or {}
    component_status = question_record.get("component_status") or {}
    answer_status = question_record.get("answer_status")
    answer = question_record.get("answer")

    profile = _profile_for_scale(scale)
    representation = _representation_for_scale(scale)

    prepared = {
        "question_id": question_record.get("question_id"),
        "question_block": question_record.get("question_block"),
        "question_type": question_record.get("question_type"),
        "scale_type": scale.get("scale_type"),
        "measurement_scale": scale.get("measurement_scale"),
        "preparation_profile": profile,
        "representation": representation,
        "raw_answer": answer,
        "prepared_value": None,
        "answer_status": answer_status,
        "preparation_status": "NOT_PREPARED",
        "validation_flags": [],
    }

    if not component_status.get("question_type_registered"):
        prepared["validation_flags"].append("QUESTION_TYPE_NOT_REGISTERED")

    if not component_status.get("scale_type_registered"):
        prepared["validation_flags"].append("SCALE_TYPE_NOT_REGISTERED")

    if not component_status.get("question_type_scale_compatible"):
        prepared["validation_flags"].append("QUESTION_TYPE_SCALE_NOT_COMPATIBLE")

    if not component_status.get("response_type_registered"):
        prepared["validation_flags"].append("RESPONSE_TYPE_NOT_REGISTERED")

    if not component_status.get("response_type_scale_compatible"):
        prepared["validation_flags"].append("RESPONSE_TYPE_SCALE_NOT_COMPATIBLE")

    if answer_status != "ANSWERED":
        prepared["preparation_status"] = "NOT_PREPARED_MISSING"
        prepared["validation_flags"].append(answer_status)
        return prepared

    if prepared["validation_flags"]:
        prepared["preparation_status"] = "NOT_PREPARED_INVALID_COMPONENTS"
        return prepared

    prepared["prepared_value"] = answer
    prepared["preparation_status"] = "PREPARED"

    return prepared


def build_questionnaire_preparation(
    questionnaire_description: dict,
) -> dict:
    questionnaire_description = questionnaire_description or {}

    prepared_questions = [
        _prepare_answer(question_record)
        for question_record in questionnaire_description.get("questions", [])
    ]

    return {
        "schema_version": QUESTIONNAIRE_PREPARATION_SCHEMA_VERSION,
        "questionnaire_id": questionnaire_description.get("questionnaire_id"),
        "questionnaire_version": questionnaire_description.get("questionnaire_version"),
        "questionnaire_completion_id": questionnaire_description.get(
            "questionnaire_completion_id"
        ),
        "prepared_questions": prepared_questions,
        "raw_answers_preserved": True,
        "scores_calculated": False,
        "analysis_performed": False,
        "interpretation_performed": False,
    }
