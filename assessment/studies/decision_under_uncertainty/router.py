from .flow import DU_FLOW


def _matches(condition: dict, value) -> bool:
    if not condition:
        return False

    if "value" in condition:
        return value == condition["value"]

    if "min_value" in condition:
        return value >= condition["min_value"]

    if "max_value" in condition:
        return value <= condition["max_value"]

    if "in" in condition:
        return value in condition["in"]

    return False


def get_next_question_code(question_code: str, value):
    next_config = DU_FLOW.get(question_code) or {}

    for rule in next_config.get("rules", []):
        if _matches(rule.get("if", {}), value):
            return rule.get("goto")

    return next_config.get("default")
