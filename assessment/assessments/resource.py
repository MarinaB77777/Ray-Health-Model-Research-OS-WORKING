# assessment/assessments/resource.py

RESOURCE_ASSESSMENT = {
    "assessment_id": "resource",
    "title": {
        "ru": "Оценка ресурсов",
        "en": "Resource assessment",
        "es": "Evaluación de recursos",
    },
    "description": {
        "ru": "Оценка текущих ресурсов, восстановления, устойчивости и маркеров рассогласования.",
        "en": "Assessment of current resources, recovery, resilience, and mismatch markers.",
        "es": "Evaluación de recursos actuales, recuperación, resiliencia y marcadores de discrepancia.",
    },
    "time_reference": {
        "type": "current_and_recent",
        "period": "last_2_4_weeks",
        "anchor": "now",
    },
    "completion_rules": {
        "minimum_completion": 1.0,
        "allow_partial": False,
    },
    "question_codes": [
        "T1", "T2", "T3", "T4",
        "M1", "M2", "M3", "M4",
        "G1", "G2", "G3", "G12",
        "C1", "C2", "C3",
        "F1", "F2", "F3", "F4",
        "P1", "P2", "P3",
        "RE1", "RE2",
        "PR1", "PR2", "PR3", "PR4", "PR5", "PR6",
        "SR1", "SR2", "SR3", "SR4",
        "MG1", "MG2", "MG3", "MG4", "MG5", "MG6", "MG7",
        "PEP1",
        "V1", "V2", "V3", "V4",
        "K1", "K2", "K3", "K4", "K5", "K6", "K7",
        "K8", "K9", "K10", "K11", "K12", "K13",
        "K14", "K15", "K16", "K17", "K18",
        "K19", "K20", "K21", "K22", "K23", "K24",
    ],
}