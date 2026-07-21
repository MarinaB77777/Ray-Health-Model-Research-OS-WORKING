from assessment.preparation.source_identity import build_source_identity
from assessment.preparation.questionnaire_description import (
    build_questionnaire_description,
)
from assessment.preparation.questionnaire_preparation import (
    build_questionnaire_preparation,
)

from assessment.questionnaire_flow import (
    build_linear_flow,
    build_execution_path,
)

QUESTIONNAIRE_PIPELINE_SCHEMA_VERSION = "questionnaire-preparation-pipeline-1"


def build_questionnaire_preparation_pipeline(
    assessment: dict,
    session: dict,
    answers: dict,
) -> dict:
    source_identity = build_source_identity(
        assessment=assessment,
        session=session,
    )
    
    question_codes = list((assessment.get("questions") or {}).keys())

    questionnaire_flow = build_linear_flow(
        question_codes=question_codes,
    )

    execution_path = build_execution_path(
        flow=questionnaire_flow,
        answers=answers,
    )

    questionnaire_description = build_questionnaire_description(
        assessment=assessment,
        session=session,
        answers=answers,
    )

    questionnaire_preparation = build_questionnaire_preparation(
        questionnaire_description=questionnaire_description,
    )

    return {
        "schema_version": QUESTIONNAIRE_PIPELINE_SCHEMA_VERSION,
        "source_identity": source_identity,
        "questionnaire_flow": questionnaire_flow,
        "execution_path": execution_path,
        "questionnaire_description": questionnaire_description,
        "questionnaire_preparation": questionnaire_preparation,
        "pipeline_status": "PREPARED",
        "analysis_performed": False,
    }