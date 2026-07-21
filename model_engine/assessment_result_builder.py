
from model_engine.assessment_profile_service import get_assessment_profile
from model_engine.interpretation_builder import build_level_interpretation


def numeric_values_for_codes(
    answers: dict,
    question_codes: list[str],
) -> list[float]:
    values = []

    for code in question_codes:
        value = answers.get(code)

        if isinstance(value, (int, float)) and value >= 0:
            values.append(float(value))

    return values


def mean_score(
    answers: dict,
    question_codes: list[str],
) -> float | None:
    values = numeric_values_for_codes(
        answers=answers,
        question_codes=question_codes,
    )

    if not values:
        return None

    return sum(values) / len(values)


def build_legacy_formula_results(
    profile: dict,
    answers: dict,
) -> list[dict]:
    results = []

    for block_id, block in profile.get("legacy_formula_blocks", {}).items():
        score = mean_score(
            answers=answers,
            question_codes=block.get("questions", []),
        )

        level_table = block.get("level_table")
        interpretation = None

        if level_table:
            interpretation = build_level_interpretation(
                resource_id=level_table,
                score=score,
            )

        results.append({
            "block_id": block_id,
            "source": "legacy_formula_questions",
            "formula": block.get("formula"),
            "status": "FORMULA_OR_LEVEL_READY",
            "score": score,
            "level_table": level_table,
            "interpretation": interpretation,
        })

    return results


def build_new_mechanism_results(
    profile: dict,
    answers: dict,
) -> list[dict]:
    results = []

    for block_id, block in profile.get("new_mechanism_blocks", {}).items():
        score = mean_score(
            answers=answers,
            question_codes=block.get("questions", []),
        )

        level_table = block.get("level_table")
        interpretation = None

        if level_table:
            interpretation = build_level_interpretation(
                resource_id=level_table,
                score=score,
            )

        results.append({
            "block_id": block_id,
            "source": "new_mechanism_questions",
            "status": block.get(
                "status",
                "ORIENTING_MECHANISM_ASSESSMENT",
            ),
            "score": score,
            "level_table": level_table,
            "interpretation": interpretation,
            "formula_status": "FORMULA_NOT_FINALIZED",
        })

    return results


def build_critical_gate_result(
    profile: dict,
    answers: dict,
) -> dict:
    gate_codes = profile.get("critical_gate", [])

    values = {
        code: answers.get(code)
        for code in gate_codes
    }

    k23 = values.get("K23")
    k24 = values.get("K24")

    critical = False

    if isinstance(k23, (int, float)) and k23 >= 3:
        critical = True

    if isinstance(k24, (int, float)) and k24 >= 2:
        critical = True

    return {
        "codes": gate_codes,
        "values": values,
        "critical": critical,
        "forecast_allowed": not critical,
    }


def build_assessment_result(
    profile_id: str,
    answers: dict,
) -> dict:
    profile = get_assessment_profile(profile_id)

    critical_gate = build_critical_gate_result(
        profile=profile,
        answers=answers,
    )

    legacy_results = build_legacy_formula_results(
        profile=profile,
        answers=answers,
    )

    mechanism_results = build_new_mechanism_results(
        profile=profile,
        answers=answers,
    )

    return {
        "profile_id": profile_id,
        "title": profile.get("title"),
        "status": "COMPLETED",
        "critical_gate": critical_gate,
        "legacy_formula_results": legacy_results,
        "new_mechanism_results": mechanism_results,
        "forecast_allowed": critical_gate["forecast_allowed"],
        "notes": [
            "Старые вопросы связаны с утверждёнными формулами модели.",
            "Новые вопросы используются как ориентировочная оценка механизмов до утверждения формул.",
            "Прогноз строится по уровневым таблицам, а не как диагностическое заключение.",
        ],
    }