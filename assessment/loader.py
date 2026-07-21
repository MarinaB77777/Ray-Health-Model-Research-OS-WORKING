from importlib import import_module

from assessment.registry import ASSESSMENT_REGISTRY


def get_assessment_config(assessment_id: str) -> dict:
    if assessment_id not in ASSESSMENT_REGISTRY:
        raise ValueError(f"Unknown assessment_id: {assessment_id}")

    config = ASSESSMENT_REGISTRY[assessment_id]

    if not config.get("active", False):
        raise ValueError(f"Assessment is not active: {assessment_id}")

    module = import_module(config["module"])

    return {
        "id": config["id"],
        "title": config["title"],
        "questions": module.QUESTIONS,
        "time_reference": getattr(module, "TIME_REFERENCE", None),
        "completion_rules": getattr(module, "COMPLETION_RULES", None),
    }


def list_active_assessments() -> list[dict]:
    result = []

    for assessment_id, config in ASSESSMENT_REGISTRY.items():
        if config.get("active", False):
            result.append({
                "id": assessment_id,
                "title": config["title"],
            })

    return result
