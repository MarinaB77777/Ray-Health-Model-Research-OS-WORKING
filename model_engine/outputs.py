def get_result_level(s_final):
    if s_final is None:
        return "unknown"

    if s_final < 3:
        return "low"

    if s_final < 5:
        return "moderate"

    if s_final < 7:
        return "medium_high"

    if s_final < 9:
        return "high"

    return "critical"


def is_forecast_allowed(state: str, coverage: float, q_global: float, c_final: float):
    return (
        state == "FORECAST"
        and coverage >= 0.6
        and q_global <= 1.5
        and c_final <= 4
    )


def build_domain_summary(r_data: dict, k_self_data: dict, delta_data: dict):
    summary = {}

    domains = set()

    domains.update(r_data.get("domains", {}).keys())
    domains.update(k_self_data.get("domains", {}).keys())
    domains.update(delta_data.keys())

    for domain in domains:
        r_item = r_data.get("domains", {}).get(domain, {})
        k_item = k_self_data.get("domains", {}).get(domain, {})
        d_item = delta_data.get(domain, {})

        summary[domain] = {
            "r": r_item.get("score"),
            "k_self": k_item.get("score"),
            "delta": d_item.get("delta"),
            "delta_interpretation": d_item.get("interpretation"),
            "calculated": d_item.get("calculated", False),
        }

    return summary


def build_summary_text(state: str, result_level: str, confidence: str):
    if state == "CRITICAL":
        return "Обнаружен критический ответ. Сейчас важнее безопасность, чем расчёт модели."

    if state == "SAFE_DATA_REQUEST":
        return "Данных недостаточно для надёжной оценки. Нужно уточнить недостающие параметры."

    if state == "LOW_QUALITY":
        return "Качество данных недостаточно для уверенного вывода. Нужно уточнить ответы."

    if state == "CONSISTENCY_FAILURE":
        return "Данные заметно расходятся между собой, поэтому прогноз ограничен."

    if state == "FORECAST":
        return "Есть признаки накопленного давления. При сохранении условий риск ухудшения может быть повышен."

    if state == "HIDDEN_FACTOR":
        return "Маркеры состояния выражены сильнее, чем объясняет текущий расчёт. Возможен неучтённый фактор."

    if state == "DIAGNOSTIC":
        return "Текущие расчётные показатели согласованы с маркерами состояния."

    return "Оценка пока ориентировочная. Для более точного вывода нужны дополнительные данные."


def build_output(
    state: str,
    confidence: str,
    coverage: float,
    q_global: float,
    c_final: float,
    s_data: dict,
    r_data: dict,
    k_self_data: dict,
    delta_data: dict,
    warnings: list,
    public_reasons: list,
    forecast: dict = None,
    next_questions: list = None,
    uncertainty_data: dict = None,
):
    s_final = s_data.get("s_final")

    result_level = get_result_level(s_final)

    forecast_allowed = is_forecast_allowed(
        state=state,
        coverage=coverage,
        q_global=q_global,
        c_final=c_final,
    )

    domain_summary = build_domain_summary(
        r_data=r_data,
        k_self_data=k_self_data,
        delta_data=delta_data,
    )

    summary_text = build_summary_text(
        state=state,
        result_level=result_level,
        confidence=confidence,
    )

    return {
        "summary_text": summary_text,
        "result_level": result_level,
        "forecast_allowed": (forecast or {}).get("allowed", forecast_allowed),
        "forecast": forecast or {
        "allowed": forecast_allowed,
        "reason": "LEGACY_FORECAST_RULE",
        "confidence": confidence,
        "allowed_scope": "none",
    },
        "domain_summary": domain_summary,
        "warnings": warnings,
        "public_reasons": public_reasons,
        "next_questions": next_questions or [],
        "uncertainty": {
            "level": (
                uncertainty_data or {}
        ).get("uncertainty_level"),

        "dialogue_mode": (
                uncertainty_data or {}
        ).get("dialogue_mode"),

        "allow_recommendations": (
                uncertainty_data or {}
        ).get("allow_recommendations"),
   },
    }