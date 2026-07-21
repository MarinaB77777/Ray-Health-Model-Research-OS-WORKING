REQUIRED_QUESTION_FIELDS = [
    "code",
    "block",
    "family",
    "domain",
    "type",
    "prompt",
]


def validate_question(question: dict) -> list[str]:
    errors = []

    for field in REQUIRED_QUESTION_FIELDS:
        if field not in question:
            errors.append(f"Missing field: {field}")

    if question.get("type") in ("single_select", "multi_select"):
        if "options" not in question:
            errors.append("Missing options for select question")

    return errors


def validate_assessment_questions(questions: list[dict]) -> dict:
    errors = {}
    seen_codes = set()

    for question in questions:
        code = question.get("code")

        if not code:
            errors["unknown"] = ["Missing question code"]
            continue

        if code in seen_codes:
            errors.setdefault(code, []).append("Duplicate question code")

        seen_codes.add(code)

        question_errors = validate_question(question)
        if question_errors:
            errors.setdefault(code, []).extend(question_errors)

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "question_count": len(questions),
    }
