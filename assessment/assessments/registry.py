# assessment/registry.py

from importlib import import_module


ASSESSMENT_REGISTRY = {
    "intro": {
        "id": "intro",
        "object": "INTRO_ASSESSMENT",
        "module": "assessment.assessments.intro",
        "mapping": "assessment.mappings.intro_mapping",
        "active": True,
    },
    "resource": {
        "id": "resource",
        "object": "RESOURCE_ASSESSMENT",
        "module": "assessment.assessments.resource",
        "mapping": "assessment.mappings.resource_mapping",
        "active": True,
    },
    "decision": {
        "id": "decision",
        "object": "DECISION_ASSESSMENT",
        "module": "assessment.assessments.decision",
        "mapping": "assessment.mappings.decision_mapping",
        "hypotheses": "assessment.hypotheses.decision_hypotheses",
        "active": True,
    },
}


def get_assessment(assessment_id: str, question_bank: dict | None = None):
    config = ASSESSMENT_REGISTRY.get(assessment_id)

    if not config or not config.get("active"):
        return None

    module = import_module(config["module"])
    assessment = getattr(module, config["object"])

    question_codes = assessment.get("question_codes", [])

    questions = []
    missing_codes = []

    if question_bank is not None:
        for code in question_codes:
            question = question_bank.get(code)

            if question is None:
                missing_codes.append(code)
            else:
                questions.append(question)

    if missing_codes:
        return {
            "ok": False,
            "assessment_id": assessment_id,
            "error": "Missing questions in question bank",
            "missing_codes": missing_codes,
        }

    return {
        "ok": True,
        "assessment_id": assessment["assessment_id"],
        "title": assessment.get("title", {}),
        "description": assessment.get("description", {}),
        "time_reference": assessment.get("time_reference", {}),
        "question_codes": question_codes,
        "questions": questions,
        "mapping": config.get("mapping"),
        "hypotheses": config.get("hypotheses"),
    }


def list_assessments():
    result = []

    for item in ASSESSMENT_REGISTRY.values():
        if not item.get("active"):
            continue

        module = import_module(item["module"])
        assessment = getattr(module, item["object"])

        result.append({
            "id": item["id"],
            "title": assessment.get("title", {}),
            "description": assessment.get("description", {}),
        })

    return result