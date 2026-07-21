PREPARED_OUTPUT_SCHEMA_VERSION = "prepared-assessment-output-1"


def _clip_0_5(value):
    if value is None:
        return None
    return max(0, min(5, float(value)))


def _score_answer(question: dict, value):
    if value is None:
        return None

    try:
        score = float(value)
    except (TypeError, ValueError):
        return None

    direction = question.get("score_direction")

    if direction == "higher_is_more_risk":
        return _clip_0_5(score)

    if direction == "higher_is_more_resource":
        return _clip_0_5(5 - score)

    return None


def build_prepared_assessment_output(
    assessment_id: str,
    question_bank: dict,
    answers: dict,
) -> dict:
    domain_values = {}
    family_values = {}
    used_questions = []
    skipped_questions = []

    for code, question in question_bank.items():
        if not question.get("active", question.get("status") == "active"):
            continue

        if code not in answers:
            skipped_questions.append({"code": code, "reason": "ANSWER_MISSING"})
            continue

        score = _score_answer(question, answers.get(code))

        if score is None:
            skipped_questions.append({"code": code, "reason": "NOT_SCORABLE"})
            continue

        domain = question.get("domain")
        family = question.get("family")

        if domain:
            domain_values.setdefault(domain, []).append(score)

        if family:
            family_values.setdefault(family, []).append(score)

        used_questions.append({
            "code": code,
            "domain": domain,
            "family": family,
            "score": score,
        })

    domain_scores = {
        domain: round(sum(values) / len(values), 3)
        for domain, values in domain_values.items()
        if values
    }

    family_scores = {
        family: round(sum(values) / len(values), 3)
        for family, values in family_values.items()
        if values
    }

    scorable_question_count = len(used_questions) + len([
        item for item in skipped_questions
        if item["reason"] == "ANSWER_MISSING"
    ])

    coverage = (
        round(len(used_questions) / scorable_question_count, 3)
        if scorable_question_count
        else 0
    )

    return {
        "schema_version": PREPARED_OUTPUT_SCHEMA_VERSION,
        "assessment_id": assessment_id,
        "domain_scores": domain_scores,
        "family_scores": family_scores,
        "coverage": coverage,
        "answered_count": len(used_questions),
        "scorable_question_count": scorable_question_count,
        "used_questions": used_questions,
        "skipped_questions": skipped_questions,
        "raw_answers_included": False,
        "questions_included": False,
    }