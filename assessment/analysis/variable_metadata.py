import importlib.util
from pathlib import Path

from assessment.registry import get_assessment
from assessment.study_registry import get_study_definition
from question_banks import get_question_bank
from assessment.questionnaire_components import (
    normalize_question_type_id,
    normalize_scale_type_id,
)
from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
)


def _normalize_question_metadata(code: str, question: dict) -> dict:
    question_type = normalize_question_type_id(
        question.get("question_type")
        or question.get("type")
    )

    scale_type = normalize_scale_type_id(
        question.get("scale_type") or question.get("scale")
    )

    if scale_type is None:
        scale_type = normalize_scale_type_id(question.get("measurement_scale"))

    scale_definition = get_scale_definition(scale_type)
    scale_reference = (
        build_scale_reference(scale_type)
        if scale_definition is not None
        else None
    )

    return {
        "question_code": code,
        "title": (
            question.get("title")
            or question.get("prompt")
            or question.get("label")
        ),
        "scale_type": scale_type,
        "scale_reference": scale_reference,
        "measurement_level": (
            scale_definition.get("measurement_level")
            if scale_definition is not None
            else None
        ),
        "value_structure": (
            scale_definition.get("value_structure")
            if scale_definition is not None
            else None
        ),
        "numeric_nature": (
            scale_definition.get("numeric_nature")
            if scale_definition is not None
            else None
        ),
        "question_type": question_type,
        "value_type": question.get("value_type"),
        "allowed_values": question.get("allowed_values"),
        "options": question.get("options"),
        "score_direction": (
            question.get("score_direction")
            or question.get("scoring_direction")
        ),
        "domain": question.get("domain"),
        "family": question.get("family"),
        "block": question.get("block"),
        "version": question.get("version"),
    }


def _load_study_questions(study_id: str, lang: str = "ru") -> dict:
    path = (
        Path("assessment")
        / "studies"
        / study_id
        / f"{study_id}_questions_{lang}.py"
    )

    if not path.exists():
        return {}

    module_name = (
        "analysis_study_questions_"
        + study_id.replace("-", "_")
        + "_"
        + lang
    )

    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        return {}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for value in vars(module).values():
        if not isinstance(value, dict):
            continue

        if all(isinstance(item, dict) for item in value.values()):
            return value

    return {}


def _load_custom_question_bank(study_id: str, lang: str = "ru") -> dict:
    variable_name = f"QUESTION_BANK_{lang.upper()}"
    path = Path("question_banks") / study_id / f"QUESTION_BANK_{lang.upper()}.py"

    if not path.exists():
        return {}

    module_name = (
        "analysis_question_bank_"
        + study_id.replace("-", "_")
        + "_"
        + lang
    )

    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        return {}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bank = getattr(module, variable_name, None)

    if not isinstance(bank, dict):
        return {}

    return bank


def build_variable_metadata(study_id: str) -> dict:
    study = get_study_definition(study_id)

    if study:
        metadata = study.get("metadata", {})
        questions = (
            metadata.get("questions")
            or metadata.get("question_bank")
            or {}
        )

        if isinstance(questions, list):
            questions = {
                q.get("code"): q
                for q in questions
                if q.get("code")
            }

        if questions:
            return {
                code: _normalize_question_metadata(
                    code=code,
                    question=question,
                )
                for code, question in questions.items()
            }

    study_questions = _load_study_questions(
        study_id=study_id,
        lang="ru",
    )

    if study_questions:
        return {
            code: _normalize_question_metadata(
                code=code,
                question=question,
            )
            for code, question in study_questions.items()
        }

    assessment = get_assessment(
        assessment_id=study_id,
        question_bank=get_question_bank("ru"),
    )

    if assessment is not None and assessment.get("ok") is not False:
        questions = assessment.get("questions", {})

        if isinstance(questions, list):
            questions = {
                q.get("code"): q
                for q in questions
                if q.get("code")
            }

        return {
            code: _normalize_question_metadata(
                code=code,
                question=question,
            )
            for code, question in questions.items()
        }

    custom_bank = _load_custom_question_bank(
        study_id=study_id,
        lang="ru",
    )

    return {
        code: _normalize_question_metadata(
            code=code,
            question=question,
        )
        for code, question in custom_bank.items()
    }
