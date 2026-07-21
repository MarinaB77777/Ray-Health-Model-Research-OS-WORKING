import re


HEALTH_MODEL_V61_CALCULATOR_INPUT_SCHEMA_VERSION = (
    "health-model-v61-calculator-input-1"
)

DIRECT_MODEL_CODE_PATTERN = re.compile(
    r"^(B|D|T|M|G|C|F|P|E|K|X)[0-9][A-Z0-9_]*$"
)


def build_health_model_v61_calculator_input(
    *,
    answers: dict,
    question_bank: dict,
) -> dict:
    model_input = {}

    for question_code, answer_value in (answers or {}).items():
        question = question_bank.get(question_code)

        if not question:
            continue

        question_uuid = question.get("question_id")
        code = question.get("code")

        if not question_uuid or not code:
            continue

        if not DIRECT_MODEL_CODE_PATTERN.match(code):
            continue

        model_input[code.lower()] = answer_value

    return model_input