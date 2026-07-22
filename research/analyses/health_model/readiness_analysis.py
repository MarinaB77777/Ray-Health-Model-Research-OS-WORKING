from collections import Counter


NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"


def _subject(record: dict):
    return record.get("participant_id") or record.get("subject_link_id")


def _time_is_globally_referenced(record: dict) -> bool:
    reference = record.get("global_time_reference")
    if reference == "UTC":
        return True
    if isinstance(reference, dict) and reference.get("axis") == "UTC":
        return True
    contract = record.get("time_contract")
    return isinstance(contract, dict) and contract.get("axis") == "UTC"


def _comparable_series_key(record: dict):
    subject = _subject(record)
    study = record.get("study_id")
    variable = (
        record.get("parameter_code")
        or record.get("question_uuid")
        or record.get("question_code")
        or record.get("variable_id")
        or record.get("analysis_type")
    )
    if not subject or not study or not variable:
        return None
    return str(subject), str(study), str(variable)


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
    reason_codes = []

    comparable_series = {}
    for record in records:
        key = _comparable_series_key(record)
        observation_time = record.get("observation_time")
        session_id = record.get("session_id")
        if key is None or not observation_time or not session_id:
            continue
        if not _time_is_globally_referenced(record):
            continue
        comparable_series.setdefault(key, set()).add((str(session_id), str(observation_time)))

    trajectory_series = {
        key: observations
        for key, observations in comparable_series.items()
        if len(observations) >= 2
    }

    if trajectory_series:
        available.append(
            "trajectory_analysis"
        )
    else:
        blocked.append(
            "trajectory_analysis"
        )
        reason_codes.append("NO_COMPARABLE_REPEATED_SERIES_ON_GLOBAL_TIME_AXIS")

    if len(studies) >= 2:
        available.append("cross_study_analysis_candidate")
        blocked.append("cross_study_analysis")
        reason_codes.append("CROSS_STUDY_ALIGNMENT_MUST_BE_EXPLICIT")
    else:
        blocked.append(
            "cross_study_analysis"
        )

    return {
        "ready": True,
        "record_count": total_records,
        "study_count": len(studies),
        "session_count": len(sessions),
        "trajectory_series_count": len(trajectory_series),
        "trajectory_series_keys": [list(key) for key in sorted(trajectory_series)],
        "available_analyses": available,
        "blocked_analyses": blocked,
        "reason_codes": reason_codes,
    }
