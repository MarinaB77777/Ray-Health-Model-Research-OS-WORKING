CORE_REQUIRED_FIELDS = [
    "d0",
    "k7",
    "k10",
    "k14",
    "k22",
    "k23",
    "k24",
]

PRIMARY_ACTIVITY_FIELDS = [
    "d8",
    "d9",
]


def has_primary_activity(answers: dict) -> bool:
    return answers.get("d0") == 1


def is_question_applicable(code: str, answers: dict) -> bool:
    if code in PRIMARY_ACTIVITY_FIELDS:
        return has_primary_activity(answers)

    return True


def build_required_fields(answers: dict) -> list[str]:
    fields = list(CORE_REQUIRED_FIELDS)

    if has_primary_activity(answers):
        fields.extend(PRIMARY_ACTIVITY_FIELDS)

    return fields