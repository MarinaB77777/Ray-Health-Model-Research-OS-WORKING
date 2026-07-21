from model_engine.questionnaire_vnext import (
    VNEXT_SIGNAL_GROUPS,
    VNEXT_QUESTION_TEXTS,
)
from model_engine.question_bank import get_question

QUESTION_TEXTS = {
    "d0": {
       "ru": "Есть ли у тебя сейчас работа, учёба или другая основная деятельность?",
        "en": "Do you currently have work, studies, or another main activity?",
        "es": "¿Actualmente tienes trabajo, estudios u otra actividad principal?",
    },
    "d8": {
        "ru": "Какой объём задач сейчас приходится выполнять?",
        "en": "How heavy is your current task load?",
        "es": "¿Qué tan alta es tu carga actual de tareas?",
    },
    "d9": {
        "ru": "Насколько жёсткие сейчас сроки или дедлайны?",
        "en": "How strict are your current deadlines?",
        "es": "¿Qué tan estrictos son tus plazos actuales?",
    },
    "e4": {
        "ru": "Есть ли сейчас нерешённая или неопределённая ситуация, которая влияет на тебя?",
        "en": "Is there an unresolved or uncertain situation affecting you now?",
        "es": "¿Hay alguna situación pendiente o incierta que te esté afectando ahora?",
    },
    "e8": {
        "ru": "Создаёт ли сейчас давление нестабильность в работе, учёбе или основной деятельности?",
        "en": "Is work or study instability currently creating pressure?",
        "es": "¿La inestabilidad laboral o académica te está generando presión actualmente?",
    },

    # K_self markers
    "k3": {
        "en": "How restorative has your sleep felt recently?",
        "es": "¿Qué tan reparador ha sido tu sueño últimamente?",
    },
    "k7": {
        "en": "How is your energy during the day?",
        "es": "¿Cómo está tu energía durante el día?",
    },
    "k8": {
        "en": "How emotionally tense have you felt recently?",
        "es": "¿Qué tanta tensión emocional has sentido últimamente?",
    },
    "k10": {
        "en": "Do anxious thoughts appear before sleep?",
        "es": "¿Aparecen pensamientos de ansiedad antes de dormir?",
    },
    "k11": {
        "en": "How often do you feel mentally overloaded?",
        "es": "¿Con qué frecuencia te sientes mentalmente sobrecargado/a?",
    },
    "k12": {
        "en": "How difficult is it to calm down after stress?",
        "es": "¿Qué tan difícil te resulta calmarte después del estrés?",
    },
    "k13": {
        "en": "How often do you feel internally tense or irritated?",
        "es": "¿Con qué frecuencia sientes tensión interna o irritación?",
    },
    "k14": {
        "en": "Do you feel movement toward your goals or a sense of stagnation?",
        "es": "¿Sientes avance hacia tus metas o una sensación de estancamiento?",
    },
    "k15": {
        "en": "How clear do your current goals feel?",
        "es": "¿Qué tan claras sientes tus metas actuales?",
    },
    "k16": {
        "en": "How supported do you feel by people around you?",
        "es": "¿Qué tan apoyado/a te sientes por las personas a tu alrededor?",
    },
    "k17": {
        "en": "How much social tension or conflict is present now?",
        "es": "¿Cuánta tensión o conflicto social hay ahora?",
    },
    "k18": {
        "en": "How lonely or isolated do you feel?",
        "es": "¿Qué tan solo/a o aislado/a te sientes?",
    },
    "k21": {
        "en": "Do you feel connected to something meaningful?",
        "es": "¿Te sientes conectado/a con algo significativo?",
    },
    "k22": {
        "en": "Do you have a sense of meaninglessness?",
        "es": "¿Tienes una sensación de falta de sentido?",
    },
    "k23": {
        "en": "Have you had thoughts that you do not want to wake up or continue living?",
        "es": "¿Has tenido pensamientos de no querer despertar o no querer seguir viviendo?",
    },
    "k24": {
        "en": "Have you had urges or actions related to hurting yourself?",
        "es": "¿Has tenido impulsos o acciones relacionadas con hacerte daño?",
    },

    # R resources
    "t1": {"en": "How is your physical recovery?", "es": "¿Cómo está tu recuperación física?"},
    "t2": {"en": "How is your current sleep/resource reserve?", "es": "¿Cómo está tu reserva actual de sueño/energía?"},
    "t3": {"en": "How stable is your physical condition now?", "es": "¿Qué tan estable está tu condición física ahora?"},
    "t4": {"en": "How much physical exhaustion do you feel?", "es": "¿Cuánto agotamiento físico sientes?"},

    "m1": {"en": "How much emotional resource do you feel now?", "es": "¿Cuánto recurso emocional sientes ahora?"},
    "m2": {"en": "How stable is your mood recently?", "es": "¿Qué tan estable ha estado tu ánimo últimamente?"},
    "m3": {"en": "How well can you recover emotionally?", "es": "¿Qué tan bien puedes recuperarte emocionalmente?"},
    "m4": {"en": "How mentally resilient do you feel?", "es": "¿Qué tan resistente mentalmente te sientes?"},

    "g1": {"en": "How clear are your goals?", "es": "¿Qué tan claras están tus metas?"},
    "g2": {"en": "How achievable do your goals feel?", "es": "¿Qué tan alcanzables se sienten tus metas?"},
    "g3": {"en": "How much internal conflict do you feel around your goals?", "es": "¿Cuánto conflicto interno sientes alrededor de tus metas?"},

    "c1": {"en": "How much social support do you have?", "es": "¿Cuánto apoyo social tienes?"},
    "c2": {"en": "How safe do you feel in your close relationships?", "es": "¿Qué tan seguro/a te sientes en tus relaciones cercanas?"},
    "c3": {"en": "How much social pressure are you experiencing?", "es": "¿Cuánta presión social estás experimentando?"},

    "f1": {"en": "How stable is your financial situation?", "es": "¿Qué tan estable es tu situación financiera?"},
    "f2": {"en": "How much financial pressure do you feel?", "es": "¿Cuánta presión financiera sientes?"},
    "f3": {"en": "How predictable are your financial obligations?", "es": "¿Qué tan predecibles son tus obligaciones financieras?"},
    "f4": {"en": "How much financial reserve do you have?", "es": "¿Cuánta reserva financiera tienes?"},

    "p1": {"en": "Do you feel connected to meaning or values?", "es": "¿Te sientes conectado/a con sentido o valores?"},
    "p2": {"en": "How much inner meaning do you feel in what you do?", "es": "¿Cuánto sentido interno sientes en lo que haces?"},
    "p3": {"en": "How much spiritual or existential emptiness do you feel?", "es": "¿Cuánto vacío espiritual o existencial sientes?"},
}


DOMAIN_ORDER = [
    "physical",
    "psych",
    "goals",
    "social",
    "finance",
    "spiritual",
]

R_FIELDS_BY_DOMAIN = {
    "physical": ["t1", "t2", "t3", "t4"],
    "psych": ["m1", "m2", "m3", "m4"],
    "goals": ["g1", "g2", "g3"],
    "social": ["c1", "c2", "c3"],
    "finance": ["f1", "f2", "f3", "f4"],
    "spiritual": ["p1", "p2", "p3"],
}

K_FIELDS_BY_DOMAIN = {
    "physical": ["k3", "k7"],
    "psych": ["k8", "k10", "k11", "k12", "k13"],
    "goals": ["k14", "k15"],
    "social": ["k16", "k17", "k18"],
    "spiritual": ["k21", "k22"],
}


def build_question(variable_code: str, priority: int, reason_code: str):
    bank_question = get_question(variable_code)

    if bank_question is not None:
        texts = {
            "ru": bank_question.get("prompt", ""),
        }
        return {
            "variable_code": variable_code,
            "priority": priority,
            "reason_code": reason_code,
            "text": texts,
            "question_meta": bank_question,
        }

    texts = QUESTION_TEXTS.get(variable_code)

    if texts is None:
        texts = VNEXT_QUESTION_TEXTS.get(variable_code)

    if texts is None:
        texts = {
            "ru": f"Пожалуйста, укажите значение для {variable_code}.",
            "en": f"Please provide a value for {variable_code}.",
            "es": f"Por favor proporciona un valor para {variable_code}.",
        }

    return {
        "variable_code": variable_code,
        "priority": priority,
        "reason_code": reason_code,
        "text": texts,
    }


def first_missing_field(fields: list, answers: dict):
    for field in fields:
        if answers.get(field) is None:
            return field
    return None


def add_question_if_new(questions: list, variable_code: str, priority: int, reason_code: str):
    if variable_code is None:
        return

    for q in questions:
        if q.get("variable_code") == variable_code:
            return

    questions.append(
        build_question(
            variable_code=variable_code,
            priority=priority,
            reason_code=reason_code,
        )
    )


def build_delta_gap_questions(delta_data: dict, answers: dict):
    candidates = []

    for domain in DOMAIN_ORDER:
        item = delta_data.get(domain)
        if not item:
            continue

        if item.get("calculated"):
            continue

        r_coverage = item.get("coverage_r", 0) or 0
        k_coverage = item.get("coverage_k", 0) or 0
        r_score = item.get("r_score")
        k_score = item.get("k_self_score")

        priority_score = max(
            r_score if r_score is not None else 0,
            k_score if k_score is not None else 0,
        )

        if r_coverage < 0.6:
            field = first_missing_field(
                R_FIELDS_BY_DOMAIN.get(domain, []),
                answers,
            )
            if field:
                candidates.append({
                    "field": field,
                    "priority": 2,
                    "reason_code": "DELTA_R_DOMAIN_GAP",
                    "priority_score": priority_score,
                    "domain": domain,
                })

        if k_coverage < 0.6:
            field = first_missing_field(
                K_FIELDS_BY_DOMAIN.get(domain, []),
                answers,
            )
            if field:
                candidates.append({
                    "field": field,
                    "priority": 2,
                    "reason_code": "DELTA_K_SELF_DOMAIN_GAP",
                    "priority_score": priority_score,
                    "domain": domain,
                })

    candidates.sort(
        key=lambda item: (
            -item["priority_score"],
            DOMAIN_ORDER.index(item["domain"])
            if item["domain"] in DOMAIN_ORDER
            else 999,
        )
    )

    return candidates

def build_vnext_gap_questions(
    vnext_signals_data: dict,
    answers: dict,
    min_coverage: float = 0.5,
):
    candidates = []

    signals = vnext_signals_data.get("signals", {})

    if not isinstance(signals, dict):
        return candidates

    for signal_name, signal_data in signals.items():
        if not isinstance(signal_data, dict):
            continue

        coverage = signal_data.get("coverage", 0) or 0

        if coverage >= min_coverage:
            continue

        config = VNEXT_SIGNAL_GROUPS.get(signal_name, {})
        questions = config.get("questions", [])

        for question_id in questions:
            if answers.get(question_id) is None:
                candidates.append({
                    "field": question_id,
                    "priority": 3,
                    "reason_code": "VNEXT_SIGNAL_GAP",
                    "signal": signal_name,
                    "coverage": coverage,
                })
                break

    return candidates


def build_next_questions(
    coverage_data: dict,
    delta_data: dict,
    consistency_data: dict,
    vnext_signals_data: dict = None,
    answers: dict = None,
    state: str = None,
    limit: int = 3,
):
    if answers is None:
        answers = {}
    
    if state == "CRITICAL":
        return []

    questions = []

    missing_fields = coverage_data.get("missing_fields", [])

    for field in missing_fields:
        add_question_if_new(
            questions=questions,
            variable_code=field,
            priority=1,
            reason_code="MISSING_FIELD",
        )

        if len(questions) >= limit:
            return questions[:limit]

    delta_gap_candidates = build_delta_gap_questions(
        delta_data=delta_data,
        answers=answers,
    )

    for candidate in delta_gap_candidates:
        add_question_if_new(
            questions=questions,
            variable_code=candidate["field"],
            priority=candidate["priority"],
            reason_code=candidate["reason_code"],
        )

        if len(questions) >= limit:
            return questions[:limit]
    if vnext_signals_data is None:
        vnext_signals_data = {}

    vnext_gap_candidates = build_vnext_gap_questions(
        vnext_signals_data=vnext_signals_data,
        answers=answers,
    )

    for candidate in vnext_gap_candidates:
        add_question_if_new(
            questions=questions,
            variable_code=candidate["field"],
            priority=candidate["priority"],
            reason_code=candidate["reason_code"],
        )

        if len(questions) >= limit:
            return questions[:limit]

    # Later:
    # consistency-based questions
    # pressure-specific questions
    # repeated missing-domain routing



    return questions[:limit]

def build_data_acquisition_requests(next_questions: list):
    requests = []

    for question in next_questions:
        variable_code = question.get("variable_code")
        reason_code = question.get("reason_code")

        requests.append({
            "request_type": "data_acquisition",
            "acquisition_route": "dialogue_question",
            "initiator": "core_engine",
            "target": "ray_communicator",

            "variable_code": variable_code,
            "target_data": variable_code,
            "expected_response_target": (
                f"answers.{variable_code}"
                if variable_code
                else None
            ),

            "reason_code": reason_code,
            "blocks": ["state_conclusion", "forecast"],
            "priority": question.get("priority", 3),
            "status": "pending",

            "question": question,
        })

    return requests