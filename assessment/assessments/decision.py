# assessment/assessments/decision.py

DECISION_ASSESSMENT = {
    "assessment_id": "decision",

    "title": {
        "ru": "Принятие решений",
        "en": "Decision Making",
        "es": "Toma de decisiones",
    },

    "description": {
        "ru": "Исследование процесса принятия решений относительно одной актуальной жизненной ситуации.",
        "en": "Assessment of decision making regarding one current real-life situation.",
        "es": "Evaluación de la toma de decisiones respecto a una situación actual.",
    },

    "time_reference": {
        "type": "current_problem",
        "anchor": "current_problem",
        "period": "current",
    },

    "completion_rules": {
        "minimum_completion": 1.0,
        "allow_partial": False,
        "allow_resume": False,
    },

    "question_codes": [

        # Описание проблемы
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "Q5",
        "Q6",
        "Q7",
        "Q8",
        "Q9",
        "Q10",

        # Когнитивный блок
        "KCog1",
        "KCog2",
        "KCog3",
        "KCog4",
        "KCog5",
        "KCog6",
        "KCog7",
        "KCog8",

        # Decision Research
        "DR1",
        "DR2",
        "DR3",
        "DR4",
        "DR5",
        "DR6",
        "DR7",

        # Цели
        "MG1",
        "MG2",
        "MG3",
        "MG4",
        "MG5",
        "MG6",
        "MG7",

        # Психологическая устойчивость
        "PR1",
        "PR2",
        "PR3",
        "PR4",
        "PR5",
        "PR6",

        # Социальные модификаторы
        "SR1",
        "SR2",
        "SR3",
        "SR4",

        # Восстановление
        "RE1",
        "RE2",

        # Ожидания
        "PEP1",

        # Динамика состояния
        "V1",
        "V2",
        "V3",
        "V4",

        # Маркеры проверки гипотез
        "K8",
        "K9",
        "K10",
        "K11",
        "K12",
        "K13",
        "K14",
        "K15",
        "K16",
        "K17",
        "K18",
        "K21",
        "K22",
        "K23",
        "K24",
    ],
}