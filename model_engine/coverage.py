from model_engine.questionnaire_flow import build_required_fields


def compute_coverage(answers: dict):
    required_fields = build_required_fields(answers)

    valid_count = 0
    missing_fields = []

    for field in required_fields:
        value = answers.get(field)

        if value is None:
            missing_fields.append(field)
            continue

        valid_count += 1

    coverage = (
        valid_count / len(required_fields)
        if required_fields
        else 1.0
    )

    return {
        "coverage": round(coverage, 3),
        "valid_count": valid_count,
        "required_count": len(required_fields),
        "missing_fields": missing_fields,
        "required_fields": required_fields,
    }