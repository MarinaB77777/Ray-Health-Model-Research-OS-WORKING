# assessment/analysis/analyzer.py

from statistics import mean

from assessment.prognosis.prognosis import build_prognosis_layer


NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"


def _is_answered(value):
    return value is not None and value != "" and value != []


def _num(value):
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    return None


def _get(answers, *codes):
    for code in codes:
        value = _num(answers.get(code))

        if value is not None:
            return value

    return None


def _mean(values):
    valid = [
        value for value in values
        if value is not None
    ]

    if not valid:
        return None

    return mean(valid)


def _clip_0_5(value):
    if value is None:
        return None

    return max(0, min(5, value))


def calculate_domain_scores(answers):
    physical_base = _mean([
        _get(answers, "T1", "t1"),
        _get(answers, "T2", "t2"),
        _get(answers, "T3", "t3"),
        _get(answers, "T4", "t4"),
    ])

    b3 = _get(answers, "B3", "b3")
    b4 = _get(answers, "B4", "b4")

    physical = physical_base

    if physical is not None:
        if b3 is not None:
            physical += b3 / 5

        if b4 is not None:
            physical += b4 / 3

        physical = _clip_0_5(physical)

    psychological = _mean([
        _get(answers, "M1", "m1"),
        _get(answers, "M2", "m2"),
        _get(answers, "M3", "m3"),
        _get(answers, "M4", "m4"),
    ])

    goal = _mean([
        _get(answers, "G1", "g1"),
        _get(answers, "G2", "g2"),
        _get(answers, "G3", "g3"),
        _get(answers, "G12", "g12"),
    ])

    social = _mean([
        _get(answers, "C1", "c1"),
        _get(answers, "C2", "c2"),
        _get(answers, "C3", "c3"),
    ])

    financial = _mean([
        _get(answers, "F1", "f1"),
        _get(answers, "F2", "f2"),
        _get(answers, "F3", "f3"),
        _get(answers, "F4", "f4"),
    ])

    spiritual = _mean([
        _get(answers, "P1", "p1"),
        _get(answers, "P2", "p2"),
        _get(answers, "P3", "p3"),
    ])

    cognitive = _mean([
        _get(answers, "KCog1"),
        _get(answers, "KCog2"),
        _get(answers, "KCog3"),
        _get(answers, "KCog4"),
        _get(answers, "KCog5"),
        _get(answers, "KCog6"),
        _get(answers, "KCog7"),
        _get(answers, "KCog8"),
    ])

    recovery = _mean([
        _get(answers, "RE1"),
        _get(answers, "RE2"),
    ])

    pep = _get(answers, "PEP1")

    return {
        "physical": physical,
        "psychological": psychological,
        "goal": goal,
        "social": social,
        "financial": financial,
        "spiritual": spiritual,
        "cognitive": cognitive,
        "recovery": recovery,
        "pep": pep,
    }


def build_public_explanation(prognosis_layer):
    active = prognosis_layer.get("active_candidate_mechanisms", {})
    weak = prognosis_layer.get("weak_candidate_mechanisms", {})

    if not active:
        return {
            "summary": (
                "По имеющимся данным пока нельзя честно выделить устойчивый "
                "прогнозный механизм. Есть отдельные признаки, но их недостаточно, "
                "чтобы строить прогноз без уточнений."
            ),
            "what_is_visible": (
                "Можно использовать результат как предварительную ориентацию, "
                "но не как прогноз."
            ),
            "forecast": None,
            "what_to_clarify_next": [
                "какие ограничения повторяются в нескольких областях",
                "есть ли признаки накопленного истощения",
                "есть ли сужение доступных вариантов или только временная неопределённость",
            ],
            "weak_candidate_mechanisms": list(weak.keys()),
        }

    return {
        "summary": (
            "По конфигурации данных видны механизмы-кандидаты, подтверждённые "
            "минимум из двух областей. Это не повтор ответов, а интерпретация того, "
            "какие функции могут стать менее надёжными при сохранении текущей ситуации."
        ),
        "what_is_visible": (
            "Наиболее полезно смотреть не на отдельные ответы, а на совпадение "
            "уязвимых функций в разных областях."
        ),
        "forecast": (
            "Если текущая конфигурация сохранится, именно эти механизмы могут "
            "задавать направление дальнейшей траектории."
        ),
        "active_candidate_mechanisms": list(active.keys()),
        "weak_candidate_mechanisms": list(weak.keys()),
    }


def build_next_questions(prognosis_layer):
    questions = []

    weak = prognosis_layer.get("weak_candidate_mechanisms", {})

    for mechanism_name in weak.keys():
        questions.append({
            "priority": 3,
            "reason": "weak_mechanism_candidate_needs_confirmation",
            "mechanism": mechanism_name,
        })

    if not prognosis_layer.get("active_candidate_mechanisms"):
        questions.append({
            "priority": 5,
            "reason": "no_confirmed_mechanism_candidate",
        })

    return questions


def analyze_assessment(
    assessment_id: str,
    assessment: dict,
    answers: dict,
) -> dict:
    questions = assessment.get("questions", [])
    question_codes = [
        question.get("code")
        for question in questions
        if question.get("code")
    ]

    missing_required_data = [
        code for code in question_codes
        if not _is_answered(answers.get(code))
    ]

    answered_count = len(question_codes) - len(missing_required_data)

    completion = (
        answered_count / len(question_codes)
        if question_codes
        else 0
    )

    domain_scores = calculate_domain_scores(answers)

    prognosis_layer = build_prognosis_layer(domain_scores)

    public_explanation = build_public_explanation(
        prognosis_layer
    )

    next_questions = build_next_questions(
        prognosis_layer
    )

    return {
        "ok": True,
        "engine": "pilot_analysis_with_prognosis_v1",
        "assessment_id": assessment_id,

        "completion": completion,
        "answered_count": answered_count,
        "question_count": len(question_codes),

        "domain_scores": domain_scores,

        "prognosis_layer": prognosis_layer,
        "level_profiles": prognosis_layer["level_profiles"],
        "vulnerable_functions": prognosis_layer["vulnerable_functions"],
        "preserved_functions": prognosis_layer["preserved_functions"],
        "candidate_mechanisms": prognosis_layer["candidate_mechanisms"],
        "active_candidate_mechanisms": (
            prognosis_layer["active_candidate_mechanisms"]
        ),
        "weak_candidate_mechanisms": (
            prognosis_layer["weak_candidate_mechanisms"]
        ),

        "readiness_status": "ORIENTING",
        "forecast_allowed": bool(
            prognosis_layer["active_candidate_mechanisms"]
        ),

        "missing_required_data": missing_required_data,
        "next_questions": next_questions,

        "warnings": [
            "Forecast must be based only on supported mechanisms.",
            "Weak candidates are not treated as forecast.",
        ],
        "reason_codes": [
            "RESOURCE_LEVEL_MAPS_CONNECTED",
            "PROGNOSIS_LAYER_CONNECTED",
            "NO_ANSWER_RESTATEMENT_IN_PUBLIC_OUTPUT",
        ],
        "public_explanation": {
            "ru": public_explanation,
            "en": public_explanation,
            "es": public_explanation,
        },
    }