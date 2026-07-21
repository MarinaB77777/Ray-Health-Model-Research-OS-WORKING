HEALTH_MODEL_V61_MAPPING_SCHEMA_VERSION = "health-model-v61-mapping-1"


DOMAIN_ALIASES = {
    "psych": "psychological",
    "goals": "goal",
    "goal": "goal",
    "cognitive": "cognitive",
    "social": "social",
    "finance": "financial",
    "financial": "financial",
    "physical": "physical",
    "pep": "pep",
    "recovery": "recovery",
}


def _mean(values):
    clean = [
        float(value)
        for value in values
        if isinstance(value, (int, float))
    ]

    if not clean:
        return None

    return sum(clean) / len(clean)


def _score_answer(question: dict, answer_value):
    if answer_value is None:
        return None

    if not isinstance(answer_value, (int, float)):
        return None

    direction = question.get("score_direction")

    if direction == "higher_is_more_risk":
        return float(answer_value)

    if direction == "higher_is_more_resource":
        return 5 - float(answer_value)

    if direction == "higher_is_more_goal_alignment":
        return 5 - float(answer_value)

    return None


def build_health_model_v61_domain_scores(
    *,
    answers: dict,
    question_bank: dict,
) -> dict:
    domain_values = {}
    used_questions = []
    skipped_questions = []

    for question_code, answer_value in (answers or {}).items():
        question = question_bank.get(question_code)

        if question is None:
            skipped_questions.append({
                "question_code": question_code,
                "reason": "QUESTION_NOT_FOUND",
            })
            continue

        raw_domain = question.get("domain")
        domain = DOMAIN_ALIASES.get(raw_domain)

        if not domain:
            skipped_questions.append({
                "question_code": question_code,
                "reason": "DOMAIN_NOT_MAPPED",
                "raw_domain": raw_domain,
            })
            continue

        score = _score_answer(question, answer_value)

        if score is None:
            skipped_questions.append({
                "question_code": question_code,
                "reason": "NOT_SCORABLE_FOR_HEALTH_MODEL_V61",
                "score_direction": question.get("score_direction"),
            })
            continue

        domain_values.setdefault(domain, []).append(score)

        used_questions.append({
            "question_code": question_code,
            "domain": domain,
            "raw_domain": raw_domain,
            "family": question.get("family"),
            "score": score,
        })

    domain_scores = {
        domain: _mean(values)
        for domain, values in domain_values.items()
    }

    return {
        "schema_version": HEALTH_MODEL_V61_MAPPING_SCHEMA_VERSION,
        "mapping_id": "health_model_v61_domain_scores",
        "domain_scores": domain_scores,
        "used_questions": used_questions,
        "skipped_questions": skipped_questions,
    }