from model_engine.forecast_narratives import build_forecast_narratives

def build_participant_summary_text(
    readiness_public: dict,
    output: dict,
) -> str:

    summary = readiness_public.get(
        "summary_text",
        output.get("summary_text"),
    )

    investigation_active = readiness_public.get(
        "investigation_active",
        False,
    )

    if investigation_active:
        return (
            f"{summary} Есть сигнал, который лучше уточнить "
            "перед более сильными выводами."
        )

    return summary

def format_included_status(included: bool) -> dict:
    if included:
        return {
            "status": "included",
            "text": "Учитывалось",
        }

    return {
        "status": "not_included",
        "text": "Не учитывалось",
    }
def build_readiness_item(
    item_id: str,
    label: str,
    allowed: bool,
    blocked_reason_codes: list = None,
    allowed_text: str = "Доступно",
    blocked_text: str = "Недоступно",
) -> dict:

    status = "allowed" if allowed else "blocked"

    return {
        "id": item_id,
        "label": label,
        "allowed": allowed,
        "status": status,
        "reason_codes": [] if allowed else (blocked_reason_codes or []),
        "text": allowed_text if allowed else blocked_text,
    }

def build_trajectory_factor_items(forecast: dict) -> list:
    labels = {
        "OPTION_SPACE_COLLAPSE": (
            "Сейчас может быть ощущение, что вариантов действий становится меньше."
        ),
        "HOPELESSNESS_SIGNAL": (
            "В ответах есть признаки снижения веры в возможность улучшения ситуации."
        ),
        "NEGATIVE_SPIRAL": (
            "Есть признаки того, что одна проблема может усиливать другую."
        ),
        "RESOURCE_EXHAUSTION": (
            "Есть признаки истощения ресурсов для продолжения в прежнем режиме."
        ),
    }

    items = []

    for factor in forecast.get("trajectory_factors", []):
        code = factor.get("code")
        text = labels.get(code)

        if text:
            items.append({
                "code": code,
                "severity": factor.get("severity"),
                "text": text,
            })

    return items

def build_participant_sections(
    engine_result: dict,
    readiness_public: dict,
    human_dialogue: dict,
    investigations: dict,
    output: dict,
) -> list:

    sections = []

    sections.append({
        "id": "current_state",
        "title": "Текущее состояние",
        "type": "summary_card",
        "priority": 1,
        "items": [
            {
                "label": "Итог",
                "value": readiness_public.get(
                    "summary_text",
                    output.get("summary_text"),
                ),
            },
            {
                "label": "Статус интерпретации",
                "value": (
                    "Базовая интерпретация возможна"
                    if readiness_public.get("state_conclusion_ready")
                    else "Нужно больше данных"
                ),
            },
            {
                "label": "Надёжность данных",
                "value": readiness_public.get("data_reliability"),
            },
        ],
    })

    sections.append({
        "id": "interpretation_scope",
        "title": "Что можно сказать сейчас",
        "type": "readiness_card",
        "priority": 2,
        "items": [
            build_readiness_item(
                item_id="current_state",
                label="Текущее состояние",
                allowed=readiness_public.get("state_conclusion_ready"),
                blocked_reason_codes=["NOT_ENOUGH_DATA"],
                allowed_text="Можно дать базовую интерпретацию текущего состояния.",
                blocked_text="Пока недостаточно данных для интерпретации текущего состояния.",
            ),
            build_readiness_item(
                item_id="forecast",
                label="Прогноз",
                allowed=readiness_public.get("forecast_allowed"),
                blocked_reason_codes=["FORECAST_BLOCKED"],
                allowed_text="Можно строить ограниченный прогноз.",
                blocked_text="Прогноз сейчас заблокирован.",
            ),
            build_readiness_item(
                item_id="hidden_factors",
                label="Скрытые факторы",
                allowed=readiness_public.get("hidden_factor_detection_allowed"),
                blocked_reason_codes=[
                    "STRUCTURAL_FORECAST_BLOCKED_STATE_NOT_READY",
                    "DELTA_NOT_READY",
                ],
                allowed_text="Можно анализировать возможные неучтённые факторы.",
                blocked_text="Анализ скрытых факторов сейчас недоступен.",
            ),
            build_readiness_item(
                item_id="trajectory",
                label="Динамика во времени",
                allowed=readiness_public.get("trajectory_analysis_allowed"),
                blocked_reason_codes=[
                    "TRAJECTORY_NOT_READY_INSUFFICIENT_REPEATED_MEASUREMENTS",
                    "TRAJECTORY_NOT_READY_MEASUREMENTS_NOT_COMPARABLE",
                    "TRAJECTORY_NOT_READY_SHARED_TIME_REFERENCE_MISSING",
                ],
                allowed_text="Можно анализировать динамику во времени.",
                blocked_text="Динамика во времени пока недоступна: нужны сопоставимые повторные замеры.",
            ),
        ],
    })

    trajectory_items = build_trajectory_factor_items(
        engine_result.get("forecast", {})
    )

    if trajectory_items:
        sections.append({
            "id": "trajectory_factors",
            "title": "Факторы динамики",
            "type": "trajectory_factor_card",
            "priority": 3,
            "items": trajectory_items,
        })

    forecast_narratives = build_forecast_narratives(engine_result)

    if forecast_narratives:
        sections.append({
            "id": "forecast_narratives",
            "title": "Что это может означать дальше",
            "type": "forecast_narrative_card",
            "priority": 4,
            "items": forecast_narratives,
        })

    if investigations.get("active_hypotheses"):
        sections.append({
            "id": "open_investigations",
            "title": "Что стоит уточнить",
            "type": "investigation_card",
            "priority": 5,
            "summary": readiness_public.get(
                "investigation_summary",
            ),
            "items": investigations.get(
                "active_hypotheses",
                [],
            ),
        })

    if human_dialogue.get("investigation_questions"):
        sections.append({
            "id": "clarification_questions",
            "title": "Уточняющие вопросы",
            "type": "question_card",
            "priority": 6,
            "items": human_dialogue.get(
                "investigation_questions",
                [],
            ),
        })

    if output.get("domain_summary"):
       sections.append({
            "id": "domains",
            "title": "Области состояния",
            "type": "domain_summary_card",
            "priority": 7,
            "items": output.get("domain_summary", {}),
        })

    sections.append({
        "id": "limits",
        "title": "Что не учитывалось",
        "type": "limits_card",
        "priority": 8,
        "items": [
            {
                "label": "Сенсоры",
                "included": engine_result.get("sources", {}).get("sensors"),
                **format_included_status(
                    engine_result.get("sources", {}).get("sensors")
                ),
            },
            {
                "label": "Личная базовая линия",
                "included": engine_result.get("sources", {}).get("baselines"),
                **format_included_status(
                    engine_result.get("sources", {}).get("baselines")
                ),
            },
            {
                "label": "История изменений",
                "included": engine_result.get("sources", {}).get("history"),
                **format_included_status(
                    engine_result.get("sources", {}).get("history")
                ),
            },
        ],
    })

    return sections

def build_pilot_public_output(engine_result: dict) -> dict:
    output = engine_result.get("output", {})
    readiness = engine_result.get("readiness", {})
    readiness_public = readiness.get("public", {})
    human_dialogue = readiness.get("human_dialogue", {})

    investigations = (
        readiness
        .get("internal", {})
        .get("investigations", {})
    )

    s_data = engine_result.get("s", {})
    r_data = engine_result.get("r", {})
    k_self_data = engine_result.get("k_self", {})
    delta_data = engine_result.get("delta", {})

    participant_summary_text = build_participant_summary_text(
        readiness_public,
        output,
    )

    sections = build_participant_sections(
        engine_result=engine_result,
        readiness_public=readiness_public,
        human_dialogue=human_dialogue,
        investigations=investigations,
        output=output,
    )

    return {
        "summary_text": readiness_public.get(
            "summary_text",
            output.get("summary_text"),
        ),
        "readiness_summary": readiness_public.get("summary_text"),
        "participant_summary_text": participant_summary_text,
        "sections": sections,
        "state": engine_result.get("state"),
        "interpretation_status": (
            "basic_interpretation"
            if readiness_public.get(
                "state_conclusion_ready"
        )
        else "data_request"
        ),
        "confidence": engine_result.get("confidence"),

        "current_state": {
            "s_final": s_data.get("s_final"),
            "result_level": output.get("result_level"),
            "state_conclusion_ready":
                readiness_public.get("state_conclusion_ready"),
            "data_reliability":
                readiness_public.get("data_reliability"),
            "data_consistency_status":
                readiness_public.get("data_consistency_status"),
        },

        "resource_summary": {
            "r_total": r_data.get("r_total"),
            "k_self_total_0_5":
                k_self_data.get("k_self_total_0_5"),
            "domain_summary":
                output.get("domain_summary", {}),
        },

        "forecast_governance": {
            "forecast_allowed":
                readiness_public.get("forecast_allowed"),
            "forecast_scope":
                readiness_public.get("forecast_scope"),
            "structural_forecast_mode":
                readiness_public.get("structural_forecast_mode"),
            "trajectory_readiness_status":
                readiness_public.get("trajectory_readiness_status"),
        },

        "investigations": {
            "active":
                readiness_public.get("investigation_active"),
            "active_count":
                readiness_public.get("active_investigation_count"),
            "summary":
                readiness_public.get("investigation_summary"),
            "active_hypotheses":
                investigations.get("active_hypotheses", []),
        },

        "questions": {
            "next_questions":
                engine_result.get("next_questions", []),
            "investigation_questions":
                human_dialogue.get("investigation_questions", []),
        },

        "warnings":
            engine_result.get("public_warnings", []),

        "public_reasons":
            readiness_public.get("public_reasons", []),

        "not_included": {
            "sensors_available":
                engine_result.get("sources", {}).get("sensors"),
            "baselines_available":
                engine_result.get("sources", {}).get("baselines"),
            "history_available":
                engine_result.get("sources", {}).get("history"),
        },
    }