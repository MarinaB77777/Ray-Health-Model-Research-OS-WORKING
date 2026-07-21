import re


HEALTH_MODEL_V61_PARAMETER_REGISTRY_SCHEMA_VERSION = (
    "health-model-v61-parameter-registry-1"
)

DIRECT_MODEL_CODE_PATTERN = re.compile(
    r"^(B|D|T|M|G|C|F|P|E|K|X)[0-9][A-Z0-9_]*$"
)


def build_uuid_to_model_parameter_registry(
    question_bank: dict,
) -> dict:
    registry = {}

    for question in (question_bank or {}).values():
        question_uuid = question.get("question_id")
        question_code = question.get("code")

        if not question_uuid or not question_code:
            continue

        if not DIRECT_MODEL_CODE_PATTERN.match(question_code):
            continue

        registry[question_uuid] = {
            "schema_version": HEALTH_MODEL_V61_PARAMETER_REGISTRY_SCHEMA_VERSION,
            "question_uuid": question_uuid,
            "question_code": question_code,
            "model_parameter_code": question_code.lower(),
            "mapping_type": "direct_model_code",
            "status": "active",
        }

    return registry


def build_health_model_input_from_uuid_answers(
    *,
    answers: dict,
    question_bank: dict,
) -> dict:
    registry = build_uuid_to_model_parameter_registry(question_bank)

    question_uuid_by_code = {
        question.get("code"): question.get("question_id")
        for question in (question_bank or {}).values()
        if question.get("code") and question.get("question_id")
    }

    model_input = {}

    for question_code, answer_value in (answers or {}).items():
        question_uuid = question_uuid_by_code.get(question_code)

        if not question_uuid:
            continue

        mapping = registry.get(question_uuid)

        if not mapping:
            continue

        model_input[mapping["model_parameter_code"]] = answer_value

    return model_input

def build_health_model_input_mapping_records(
    *,
    answers: dict,
    question_bank: dict,
) -> list[dict]:
    registry = build_uuid_to_model_parameter_registry(question_bank)

    question_uuid_by_code = {
        question.get("code"): question.get("question_id")
        for question in (question_bank or {}).values()
        if question.get("code") and question.get("question_id")
    }

    records = []

    for question_code, answer_value in (answers or {}).items():
        question_uuid = question_uuid_by_code.get(question_code)

        if not question_uuid:
            continue

        mapping = registry.get(question_uuid)

        if not mapping:
            continue

        records.append({
            "schema_version": HEALTH_MODEL_V61_PARAMETER_REGISTRY_SCHEMA_VERSION,
            "record_type": "question_to_model_parameter_mapping",
            "question_uuid": question_uuid,
            "question_code": question_code,
            "model_parameter_code": mapping["model_parameter_code"],
            "mapping_type": mapping["mapping_type"],
            "answer_value": answer_value,
        })

    return records