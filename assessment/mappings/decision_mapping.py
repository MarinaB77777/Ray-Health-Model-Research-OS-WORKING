# assessments/decision_mapping.py

from assessments.decision_making import QUESTIONS


def get_answer(answers, code, default=None):
    return answers.get(code, default)


def is_high(value, threshold=4):
    return value is not None and value >= threshold


def is_medium(value, threshold=3):
    return value is not None and value >= threshold


def mean(values):
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return None
    return sum(clean) / len(clean)


DECISION_HYPOTHESES = [
    {
        "id": "decision_degradation",
        "title": "Decision degradation",
        "description": "Снижение качества решений из-за перегрузки, эмоций, усталости или недостаточной проверки информации.",
        "codes": [
            "KCog1", "KCog2", "KCog3", "KCog4", "KCog5", "KCog6", "KCog7", "KCog8",
            "DR5", "PR1", "PR2", "PR4", "MT1", "MT2", "MT3", "MT4",
            "Q4", "Q10",
        ],
    },
    {
        "id": "option_space_collapse",
        "title": "Option space collapse",
        "description": "Сужение воспринимаемого пространства вариантов, даже если объективно варианты могут существовать.",
        "codes": [
            "SR1", "FR1", "G9", "G9a", "Q2", "Q3", "Q9", "Q10",
        ],
    },
    {
        "id": "commitment_trap",
        "title": "Commitment trap",
        "description": "Сложность выйти из выбранного пути, обязательства или цели, даже если цена становится слишком высокой.",
        "codes": [
            "MG5", "MG6", "MG7", "G10", "G11", "G13", "DR4", "MR2", "PV1", "PV2", "PV3",
        ],
    },
    {
        "id": "learning_failure",
        "title": "Learning failure",
        "description": "Повторение неработающих решений без существенного изменения стратегии.",
        "codes": [
            "DR1", "DR2", "DR3", "KCog3", "KCog4", "KCog5", "PR5", "MR8",
        ],
    },
    {
        "id": "scarcity_pressure",
        "title": "Scarcity pressure",
        "description": "Ускорение решений под давлением дефицита времени, денег, вариантов или исчезающей возможности.",
        "codes": [
            "FR2", "FR3", "FR4", "F1", "F2", "MR7", "Q8", "Q10",
        ],
    },
]

def calculate_hypothesis_score(answers, codes):
    values = [get_answer(answers, code) for code in codes]
    return mean(values)


def evaluate_hypotheses(answers):
    results = []

    for hypothesis in DECISION_HYPOTHESES:
        score = calculate_hypothesis_score(answers, hypothesis["codes"])

        if score is None:
            level = "not_enough_data"
        elif score >= 4:
            level = "high"
        elif score >= 2.5:
            level = "medium"
        else:
            level = "low"

        results.append({
            "id": hypothesis["id"],
            "title": hypothesis["title"],
            "description": hypothesis["description"],
            "score": score,
            "level": level,
            "source_codes": hypothesis["codes"],
        })

    return results

CONTRADICTION_RULES = [
    {
        "id": "high_control_but_no_options",
        "title": "Контроль заявлен, но варианты не видны",
        "if_high": ["MG4", "Q9"],
        "if_low": ["G9", "G9a", "SR1"],
        "description": "Человек сообщает способность влиять на ситуацию, но одновременно плохо видит реальные варианты действий.",
    },
    {
        "id": "goal_identity_but_low_progress",
        "title": "Цель важна, но движение заблокировано",
        "if_high": ["MG6", "MG5"],
        "if_low": ["G7", "G9", "G11"],
        "description": "Цель субъективно очень важна, но продвижение, варианты или устойчивость пути снижены.",
    },
    {
        "id": "low_markers_but_high_burden",
        "title": "Высокая нагрузка без выраженных маркеров",
        "if_high": ["D8", "D9", "D10", "G10"],
        "if_low": ["K7", "K12", "K13", "V2", "V3"],
        "description": "Ответы описывают высокую нагрузку, но маркеры состояния пока низкие. Возможна компенсация или ранняя стадия.",
    },
    {
        "id": "high_markers_but_low_reported_burden",
        "title": "Маркеры хуже, чем описанная нагрузка",
        "if_high": ["K7", "K8", "K10", "K11", "K12", "V2", "V3"],
        "if_low": ["D8", "D9", "D10", "G10"],
        "description": "Маркеры состояния выражены сильнее, чем заявленная нагрузка. Нужна проверка скрытого фактора.",
    },
    {
        "id": "confidence_but_repeated_failure",
        "title": "Уверенность при повторяющемся нерабочем паттерне",
        "if_high": ["PV5", "MG4"],
        "if_low": ["DR1", "DR2", "DR4", "MR2"],
        "description": "Заявленная уверенность или контроль могут расходиться с повторением неработающих решений.",
    },
]


def evaluate_contradictions(answers):
    flags = []

    for rule in CONTRADICTION_RULES:
        high_score = calculate_hypothesis_score(answers, rule["if_high"])
        low_side_score = calculate_hypothesis_score(answers, rule["if_low"])

        if high_score is None or low_side_score is None:
            continue

        if high_score >= 3.5 and low_side_score >= 3.5:
            flags.append({
                "id": rule["id"],
                "title": rule["title"],
                "description": rule["description"],
                "severity": "needs_clarification",
                "high_side_score": high_score,
                "other_side_score": low_side_score,
                "source_codes": rule["if_high"] + rule["if_low"],
            })

    return flags

def run_decision_mapping(answers):
    return {
        "assessment_id": ASSESSMENT_ID,
        "assessment_name": ASSESSMENT_NAME,
        "time_reference": TIME_REFERENCE,
        "question_codes": QUESTION_CODES,
        "scores": {
            "hypotheses": evaluate_hypotheses(answers),
            "contradictions": evaluate_contradictions(answers),
        },
        "warnings": [],
        "notes": [
            "This assessment is exploratory and hypothesis-generating.",
            "High scores do not diagnose a condition.",
            "Contradictions require clarification, not automatic interpretation.",
            "K markers are used as state/manifestation checks, not as causes.",
        ],
    }