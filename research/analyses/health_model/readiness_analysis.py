from collections import Counter


NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"


def analyze_research_readiness(records: list[dict]) -> dict:
    """
    Research readiness.

    Не анализирует человека.
    Не строит прогноз.
    Не рассчитывает модель.

    Только отвечает:
    - достаточно ли исследовательских данных;
    - какие виды анализа уже доступны;
    - чего ещё не хватает.
    """

    total_records = len(records)

    if total_records == 0:
        return {
            "ready": False,
            "record_count": 0,
            "reason_codes": [
                "NO_RESEARCH_RECORDS"
            ],
            "available_analyses": [],
            "blocked_analyses": [
                "cross_record_analysis",
                "trajectory_analysis",
                "population_analysis",
            ],
        }

    studies = Counter(
        record.get("study_id")
        for record in records
    )

    sessions = {
        record.get("session_id")
        for record in records
        if record.get("session_id")
    }

    available = [
        "single_record_analysis"
    ]

    blocked = []

    if len(sessions) >= 2:
        available.append(
            "trajectory_analysis"
        )
    else:
        blocked.append(
            "trajectory_analysis"
        )

    if len(studies) >= 2:
        available.append(
            "cross_study_analysis"
        )
    else:
        blocked.append(
            "cross_study_analysis"
        )

    return {
        "ready": True,
        "record_count": total_records,
        "study_count": len(studies),
        "session_count": len(sessions),
        "available_analyses": available,
        "blocked_analyses": blocked,
        "reason_codes": [],
    }