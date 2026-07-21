PARTICIPANT_REPORT_SCHEMA_VERSION = "participant-report-1"


def _collect_level_map_interpretations(analysis: dict) -> dict:
    level_maps = analysis.get("level_maps", {})
    records = level_maps.get("records", [])

    collected = {}

    for record in records:
        interpretations = record.get("interpretations", {})

        if not isinstance(interpretations, dict):
            continue

        for domain, item in interpretations.items():
            if domain not in collected:
                collected[domain] = item

    return collected


def _build_resource_summary(interpretations: dict) -> list[dict]:
    cards = []

    for domain, item in interpretations.items():
        interpretation = item.get("interpretation", {})

        cards.append({
            "type": "resource_summary_card",
            "domain": domain,
            "title": domain.replace("_", " ").title(),
            "level_label": _safe_level_label(item.get("level_key")),
            "summary": interpretation.get("resource_state"),
            "what_may_be_sensitive": (
                interpretation.get("cognitive_behavioral_consequences")
            ),
            "decision_context": interpretation.get("decision_impact"),
        })

    return cards


def _safe_level_label(level_key: str | None) -> str:
    if level_key == "0_1":
        return "низкая выраженность ограничений"

    if level_key in {"2", "3"}:
        return "умеренная зона внимания"

    if level_key in {"4", "5"}:
        return "выраженная зона внимания"

    return "данных недостаточно"


def _build_general_summary(cards: list[dict]) -> str:
    if not cards:
        return (
            "По текущим данным пока недостаточно оснований для полезной "
            "обобщённой интерпретации. Результат можно использовать только "
            "как предварительную ориентацию."
        )

    high_attention = [
        card for card in cards
        if card.get("level_label") == "выраженная зона внимания"
    ]

    moderate_attention = [
        card for card in cards
        if card.get("level_label") == "умеренная зона внимания"
    ]

    if high_attention:
        return (
            "Общая картина показывает несколько областей, которые сейчас могут "
            "быть особенно чувствительными к нагрузке и неопределённости. "
            "В таких условиях полезнее не усиливать давление, а сначала "
            "упростить ближайшие решения и восстановить управляемость ситуации."
        )

    if moderate_attention:
        return (
            "Общая картина показывает отдельные области, которым сейчас может "
            "требоваться больше внимания. Это не означает критическое состояние, "
            "но подсказывает, где решения могут становиться менее устойчивыми."
        )

    return (
        "Общая картина выглядит относительно устойчивой по доступным данным. "
        "Серьёзных оснований связывать решения с выраженным ресурсным ограничением "
        "по текущему результату не видно."
    )


def _build_recommendations(cards: list[dict]) -> list[dict]:
    if not cards:
        return [
            {
                "title": "Не делать далеко идущих выводов",
                "text": (
                    "Данных пока недостаточно для персональной интерпретации. "
                    "Лучше использовать результат как повод пройти следующий блок "
                    "или повторить исследование позже."
                ),
            }
        ]

    recommendations = [
        {
            "title": "Снизить сложность ближайших решений",
            "text": (
                "Если решение важное, лучше разделить его на меньшие шаги: "
                "что нужно решить сейчас, что можно отложить, а что требует "
                "дополнительной информации."
            ),
        },
        {
            "title": "Не принимать стратегические решения на пике нагрузки",
            "text": (
                "Если есть ощущение перегруза, полезно сначала восстановить "
                "минимальную ясность и только потом возвращаться к решениям "
                "с долгосрочными последствиями."
            ),
        },
        {
            "title": "Выбрать один ближайший приоритет",
            "text": (
                "На ближайшие 24–48 часов лучше выбрать одно главное направление, "
                "чтобы уменьшить конкуренцию задач и снизить вероятность "
                "реактивных решений."
            ),
        },
    ]

    return recommendations


def build_participant_report(analysis: dict) -> dict:
    interpretations = _collect_level_map_interpretations(analysis)
    cards = _build_resource_summary(interpretations)

    return {
        "report_type": "participant_safe_summary",
        "schema_version": PARTICIPANT_REPORT_SCHEMA_VERSION,

        "raw_answers_included": False,
        "questions_included": False,
        "answer_restatement_allowed": False,
        "scores_exposed": False,

        "title": "Общая картина",
        "summary": _build_general_summary(cards),
        "resource_cards": cards,
        "recommendations": _build_recommendations(cards),
        "limitations": [
            "Это предварительная интерпретация, а не диагноз.",
            "Результат не пересказывает ответы и не показывает вопросы.",
            "Вывод основан только на доступных данных текущего исследования.",
        ],
    }