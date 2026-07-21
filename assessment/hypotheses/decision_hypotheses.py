# assessment/hypotheses/decision_hypotheses.py

VERSION = 1

HYPOTHESES = [
    {
        "id": "H_DECISION_DEGRADATION",
        "title": "Decision degradation",
        "description": "Снижение качества решений при перегрузке, усталости, эмоциях или неопределённости.",
        "question_codes": [
            "KCog1", "KCog2", "KCog3", "KCog4",
            "KCog5", "KCog6", "KCog7", "KCog8",
            "PR1", "PR2", "PR4", "MT1", "MT2", "MT3", "MT4",
            "DR5", "Q4",
        ],
        "status": "active",
    },
    {
        "id": "H_OPTION_SPACE_COLLAPSE",
        "title": "Option space collapse",
        "description": "Сужение воспринимаемых вариантов действий, даже если объективные варианты могут существовать.",
        "question_codes": [
            "SR1", "G9", "G9a", "G13",
            "Q2", "Q3", "Q9", "Q10",
        ],
        "status": "active",
    },
    {
        "id": "H_COMMITMENT_TRAP",
        "title": "Commitment trap",
        "description": "Продолжение тяжёлого пути из-за вложенных ресурсов, обязательств или трудности выйти.",
        "question_codes": [
            "MG5", "MG7", "MR2", "MR8",
            "G10", "G11", "G13",
            "DR4", "DR7",
        ],
        "status": "active",
    },
    {
        "id": "H_LEARNING_FAILURE",
        "title": "Learning failure",
        "description": "Повторение неработающих решений или паттернов несмотря на негативный результат.",
        "question_codes": [
            "KCog3", "KCog4", "KCog5",
            "DR1", "DR2", "DR3", "DR6",
            "MR2", "MR8",
        ],
        "status": "active",
    },
    {
        "id": "H_RECOVERY_MISMATCH",
        "title": "Recovery mismatch",
        "description": "Нагрузка сохраняется или накапливается быстрее, чем человек восстанавливается.",
        "question_codes": [
            "RE1", "RE2",
            "V2", "V3", "V4",
            "T4", "K3", "K7", "K13",
            "G11", "Q10",
        ],
        "status": "active",
    },
]


def get_hypotheses():
    return HYPOTHESES