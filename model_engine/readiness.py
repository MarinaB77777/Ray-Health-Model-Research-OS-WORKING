# model_engine/readiness.py


def analyze_readiness(engine_result: dict) -> dict:
    """
    Centralized Readiness / Governance Analyzer.

    Does NOT:
    - calculate S / Δ / pressure
    - modify engine state
    - write storage
    - rewrite calibration

    Analyzer only decides:
    - can we trust the current result
    - what is allowed
    - what is blocked
    - what is missing
    - whether data is consistent enough
    - whether clarification is required
    """

    core = analyze_core_readiness(engine_result)
    activity = analyze_activity_context(engine_result)
    source_access = analyze_source_access(engine_result)
    source_quality = analyze_source_quality(
        engine_result,
        source_access
    )

    data_freshness = analyze_data_freshness(engine_result) 
    source_failure = analyze_source_failure_detection(engine_result)   
    sensor = analyze_sensor_readiness(engine_result)
    context = analyze_context_consistency(
        engine_result,
        sensor
    )

    data_consistency = analyze_data_consistency(
        engine_result,
        core,
        activity,
        sensor,
        context
    )

    data_reliability = analyze_data_reliability(
        core,
        activity,
        source_access,
        source_quality,
        data_consistency
    )

    risk = analyze_risk_governance(
        engine_result,
        core,
        activity,
        sensor,
        context,
        data_consistency,
        source_failure
    )

    structural_forecast = analyze_structural_forecast_readiness(
        core,
        activity,
        data_consistency,
        risk
    )

    state_risk = analyze_state_risk_readiness(
        structural_forecast,
        risk
    )

    trajectory = analyze_trajectory_readiness(
        engine_result,
        core,
        activity,
        data_consistency,
        risk
    )

    vnext_signals = analyze_vnext_signal_readiness(
        engine_result
    )

    learning = analyze_learning_governance(
        engine_result,
        sensor,
        context
    )
    
    investigations = analyze_investigations(
        engine_result,
        data_consistency,
        source_failure,
        data_freshness,
        risk
    )

    return build_readiness_output(        
        core,
        activity,
        source_access,
        source_quality,
        data_reliability,
        data_freshness,
        source_failure,
        sensor,
        context,
        data_consistency,
        risk,
        structural_forecast,
        state_risk,
        trajectory,
        vnext_signals,
        learning,
        investigations
    )


# =========================================================
# CORE READINESS
# =========================================================

def analyze_core_readiness(engine_result: dict) -> dict:
    reason_codes = []
    blocked_components = []
    missing_domains = []

    coverage = engine_result.get("coverage")

    q_global = (
        engine_result.get("q_global")
        if engine_result.get("q_global") is not None
        else engine_result.get("Q_global")
    )

    minimum_core_ready = (
        coverage is not None
        and q_global is not None
    )

    if coverage is None:
        reason_codes.append("NO_COVERAGE")
        blocked_components.append("core")

    if q_global is None:
        reason_codes.append("NO_Q_GLOBAL")
        blocked_components.append("core")

    r_data = (
        engine_result.get("r")
        if engine_result.get("r") is not None
        else engine_result.get("R")
    )

    k_self_data = (
        engine_result.get("k_self")
        if engine_result.get("k_self") is not None
        else engine_result.get("K_self")
    )

    r_ready = has_any_domain_score(r_data)
    k_self_ready = has_any_domain_score(k_self_data)

    pressure_ready = has_calculated_pressure(
        engine_result.get("pressure")
    )
    
    delta_count = count_calculated_delta(
        engine_result.get("delta")
    )

    if delta_count == 0:
        delta_status = "none"
    elif delta_count < 3:
        delta_status = "partial"
    else:
        delta_status = "sufficient"

    delta_ready = delta_count >= 3    

    if not r_ready:
        reason_codes.append("R_NOT_READY")
        missing_domains.append("R")

    if not k_self_ready:
        reason_codes.append("K_SELF_NOT_READY")
        missing_domains.append("K_self")

    if not pressure_ready:
        reason_codes.append("PRESSURE_NOT_READY")

    if not delta_ready:
        reason_codes.append("DELTA_NOT_READY")

    state_conclusion_ready = (
        minimum_core_ready
        and r_ready
        and k_self_ready
    )

    if not state_conclusion_ready:
        reason_codes.append("NOT_ENOUGH_DATA")

    return {
        "minimum_core_ready": minimum_core_ready,
        "r_ready": r_ready,
        "k_self_ready": k_self_ready,
        "pressure_ready": pressure_ready,
        "delta_ready": delta_ready,
        "delta_status": delta_status,
        "delta_calculated_count": delta_count,
        "state_conclusion_ready": state_conclusion_ready,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
        "missing_domains": missing_domains,
    }


# =========================================================
# ACTIVITY CONTEXT GOVERNANCE
# =========================================================

def analyze_activity_context(engine_result: dict) -> dict:
    """
    Governance-only layer.

    D-main / activity is a primary context anchor.
    This block does NOT infer occupation.
    It only checks whether activity context is known enough.
    """

    reason_codes = []
    blocked_components = []

    missing_fields = engine_result.get("missing_fields", [])

    activity_context_ready = (
        "d0" not in missing_fields
    )

    activity_type_known = activity_context_ready
    activity_risk_profile_known = activity_context_ready

    occupation_specific_interpretation_allowed = (
        activity_context_ready
    )

    if not activity_context_ready:
        reason_codes.append("ACTIVITY_CONTEXT_UNKNOWN")
        blocked_components.append(
            "occupation_specific_interpretation"
        )

    return {
        "activity_context_ready":
            activity_context_ready,
        "activity_type_known":
            activity_type_known,
        "activity_risk_profile_known":
            activity_risk_profile_known,
        "occupation_specific_interpretation_allowed":
            occupation_specific_interpretation_allowed,
        "reason_codes":
            reason_codes,
        "blocked_components":
            blocked_components,
    }

# =========================================================
# SOURCE ACCESS
# =========================================================

def analyze_source_access(engine_result: dict) -> dict:
    sources = engine_result.get("sources", {})

    if not isinstance(sources, dict):
        sources = {}

    def status(name: str) -> str:
        value = sources.get(name)

        if value is None:
            return "missing"

        if value is False:
            return "blocked"

        return "available"

    return {
        "model_outputs": "available",
        "questionnaires": status("questionnaires"),
        "sensors": status("sensors"),
        "baselines": status("baselines"),
        "history": status("history"),
        "context": status("context"),
        "external_verification": status("external_verification"),
        "reason_codes": [],
        "blocked_components": [],
    }

# =========================================================
# SOURCE QUALITY
# =========================================================

def analyze_source_quality(
    engine_result: dict,
    source_access: dict
) -> dict:

    """
    Source reliability / freshness / verification layer.

    Does NOT:
    - rewrite data
    - choose truth
    - modify engine calculations

    Only evaluates:
    - how trustworthy sources are
    - whether verification exists
    - whether contradiction risk is high
    """

    questionnaires_status = (
        source_access.get("questionnaires")
    )

    sensors_status = (
        source_access.get("sensors")
    )

    external_status = (
        source_access.get("external_verification")
    )

    history_status = (
        source_access.get("history")
    )

    self_report_quality = (
        "medium"
        if questionnaires_status == "available"
        else "unknown"
    )

    sensor_quality = (
        "high"
        if sensors_status == "available"
        else "unknown"
    )

    external_data_quality = (
        "low"
        if external_status == "available"
        else "unknown"
    )

    history_quality = (
        "medium"
        if history_status == "available"
        else "unknown"
    )

    verification_level = compute_verification_level(
        questionnaires_status,
        sensors_status,
        external_status
    )

    freshness = "unknown"

    contradiction_risk = "unknown"

    return {
        "self_report_quality": self_report_quality,
        "sensor_quality": sensor_quality,
        "external_data_quality": external_data_quality,
        "history_quality": history_quality,
        "verification_level": verification_level,
        "freshness": freshness,
        "contradiction_risk": contradiction_risk,
        "reason_codes": [],
        "blocked_components": [],
    }

# =========================================================
# DATA RELIABILITY
# =========================================================

def analyze_data_reliability(
    core: dict,
    activity: dict,
    source_access: dict,
    source_quality: dict,
    data_consistency: dict
) -> dict:

    """
    Evaluates whether current data can be trusted
    as a basis for interpretation / forecast / recommendations.

    Does NOT:
    - calculate S
    - calculate Δ
    - modify model output
    - decide medical truth

    Only evaluates reliability of available data.
    """

    reason_codes = []
    blocked_components = []

    contradiction_detected = (
        data_consistency.get("status") == "contradiction"
    )

    requires_clarification = data_consistency.get(
        "requires_clarification",
        False
    )

    self_report_only = (
        source_access.get("questionnaires") == "available"
        and source_access.get("sensors") != "available"
        and source_access.get("external_verification") != "available"
    )

    no_activity_context = not activity.get(
        "activity_context_ready",
        False
    )

    model_not_ready = not core.get(
        "state_conclusion_ready",
        False
    )

    if contradiction_detected:
        reason_codes.append("RELIABILITY_LOW_DATA_CONTRADICTION")
        blocked_components.append("forecast")
        overall_reliability = "low"

    elif model_not_ready:
        reason_codes.append("RELIABILITY_UNKNOWN_MODEL_NOT_READY")
        overall_reliability = "unknown"

    elif no_activity_context:
        reason_codes.append("RELIABILITY_LOW_ACTIVITY_CONTEXT_MISSING")
        overall_reliability = "low"

    elif self_report_only:
        reason_codes.append("RELIABILITY_BASIC_SELF_REPORT_ONLY")
        overall_reliability = "basic"

    else:
        verification_level = source_quality.get(
            "verification_level",
            "unknown"
        )

        if verification_level == "high":
            overall_reliability = "high"
        elif verification_level == "medium":
            overall_reliability = "medium"
        elif verification_level == "basic":
            overall_reliability = "basic"
        else:
            overall_reliability = "unknown"

    return {
        "overall_reliability": overall_reliability,
        "self_report_only": self_report_only,
        "self_report_bias_risk": (
            "medium" if self_report_only else "unknown"
        ),
        "sensor_noise_risk": "unknown",
        "context_reliability": (
            "low" if no_activity_context else "unknown"
        ),
        "external_verification_conflict": False,
        "contradiction_detected": contradiction_detected,
        "requires_clarification": requires_clarification,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }

# =========================================================
# DATA FRESHNESS
# =========================================================

def analyze_data_freshness(engine_result: dict) -> dict:
    """
    Evaluates whether current data is fresh enough
    for interpretation / forecast / recommendations.

    Does NOT:
    - update data
    - write storage
    - recalculate model

    Only reports freshness and refresh needs.
    """

    metadata = engine_result.get("metadata", {})
    freshness = metadata.get("freshness", {})

    if not isinstance(freshness, dict):
        freshness = {}

    stale_components = []
    refresh_recommended = []
    reason_codes = []
    blocked_components = []

    for component, status in freshness.items():

        if status == "stale":
            stale_components.append(component)
            refresh_recommended.append(component)
            reason_codes.append(
                f"{component.upper()}_STALE"
            )

        if status == "expired":
            stale_components.append(component)
            refresh_recommended.append(component)
            reason_codes.append(
                f"{component.upper()}_EXPIRED"
            )
            blocked_components.append(component)

    overall_freshness = "fresh"

    if stale_components:
        overall_freshness = "stale"

    if blocked_components:
        overall_freshness = "expired"

    if not freshness:
        overall_freshness = "unknown"
        reason_codes.append("FRESHNESS_UNKNOWN")

    return {
        "overall_freshness": overall_freshness,
        "stale_components": stale_components,
        "refresh_recommended": refresh_recommended,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }

# =========================================================
# SOURCE FAILURE DETECTION
# =========================================================

def analyze_source_failure_detection(engine_result: dict) -> dict:
    """
    Detects whether a data source may be offline, noisy,
    broken, or producing physically implausible values.

    Does NOT:
    - diagnose the person
    - assume sensor failure automatically
    - override emergency logic

    Critical-looking signals are treated as safety-relevant
    until context or verification proves otherwise.
    """

    metadata = engine_result.get("metadata", {})
    source_status = metadata.get("source_status", {})
    signal_quality = metadata.get("signal_quality", {})
    source_failures = metadata.get("source_failures", [])

    if not isinstance(source_status, dict):
        source_status = {}

    if not isinstance(signal_quality, dict):
        signal_quality = {}

    if not isinstance(source_failures, list):
        source_failures = []

    suspected_failures = []
    reason_codes = []
    blocked_components = []

    failure_detected = False
    requires_device_check = False
    requires_safety_routing = False
    critical_signal_possible = False

    for source, status in source_status.items():

        if status == "offline":
            failure_detected = True
            suspected_failures.append({
                "source": source,
                "type": "offline"
            })
            reason_codes.append(
                f"{source.upper()}_SOURCE_OFFLINE"
            )
            requires_device_check = True

        if status == "disconnected":
            failure_detected = True
            suspected_failures.append({
                "source": source,
                "type": "disconnected"
            })
            reason_codes.append(
                f"{source.upper()}_SOURCE_DISCONNECTED"
            )
            requires_device_check = True

        if status == "failed":
            failure_detected = True
            suspected_failures.append({
                "source": source,
                "type": "failed"
            })
            reason_codes.append(
                f"{source.upper()}_SOURCE_FAILED"
            )
            blocked_components.append(source)
            requires_device_check = True

    for source, quality in signal_quality.items():

        if quality == "noisy":
            failure_detected = True
            suspected_failures.append({
                "source": source,
                "type": "noisy"
            })
            reason_codes.append(
                f"{source.upper()}_SIGNAL_NOISY"
            )
            requires_device_check = True

        if quality == "implausible":
            failure_detected = True
            suspected_failures.append({
                "source": source,
                "type": "implausible"
            })
            reason_codes.append(
                f"{source.upper()}_SIGNAL_IMPLAUSIBLE"
            )
            requires_device_check = True

        if quality == "critical":
            critical_signal_possible = True
            requires_safety_routing = True
            reason_codes.append(
                f"{source.upper()}_CRITICAL_SIGNAL_POSSIBLE"
            )

    for item in source_failures:
        failure_detected = True
        suspected_failures.append(item)

        if isinstance(item, dict):
            code = item.get("code")
            if code:
                reason_codes.append(code)

    return {
        "failure_detected": failure_detected,
        "suspected_failures": suspected_failures,
        "critical_signal_possible": critical_signal_possible,
        "requires_device_check": requires_device_check,
        "requires_safety_routing": requires_safety_routing,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }

# =========================================================
# SENSOR READINESS
# =========================================================

def analyze_sensor_readiness(engine_result: dict) -> dict:
    """
    Future-ready safe stub.

    Sensor interpretation requires:
    - current biosignals
    - contextual baseline
    - context
    - consistency checks
    """

    reason_codes = []
    blocked_components = []

    sensor_data = engine_result.get("sensor_data")
    baseline = engine_result.get("contextual_baseline")
    context = engine_result.get("context")

    sensor_data_ready = sensor_data is not None
    baseline_ready = baseline is not None
    context_ready = context is not None

    if not sensor_data_ready:
        reason_codes.append("NO_CURRENT_SENSOR_DATA")

    if not baseline_ready:
        reason_codes.append("NO_SENSOR_BASELINE")

    if not context_ready:
        reason_codes.append(
            "NO_CONTEXT_FOR_BIOSIGNAL_INTERPRETATION"
        )

    biosignal_consistency_ready = (
        sensor_data_ready
        and baseline_ready
        and context_ready
    )

    if not biosignal_consistency_ready:
        blocked_components.append("sensor_interpretation")

    return {
        "sensor_data_ready": sensor_data_ready,
        "baseline_ready": baseline_ready,
        "context_ready": context_ready,
        "biosignal_consistency_ready":
            biosignal_consistency_ready,
        "anomaly_detected": False,
        "anomaly_explained_by_context": False,
        "requires_user_question": False,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }


# =========================================================
# CONTEXT CONSISTENCY
# =========================================================

def analyze_context_consistency(
    engine_result: dict,
    sensor: dict
) -> dict:
    """
    Future-ready safe stub.

    Later:
    - compare signal dynamics with context
    - detect mismatch
    - decide ask now/later
    """

    reason_codes = []
    blocked_components = []

    context_known = sensor.get("context_ready", False)
    signal_changed = False
    context_signal_match = None

    if signal_changed and not context_known:
        reason_codes.append(
            "CONTEXT_UNKNOWN_FOR_SIGNAL_CHANGE"
        )
        blocked_components.append(
            "context_consistency"
        )

    return {
        "context_known": context_known,
        "signal_changed": signal_changed,
        "context_signal_match": context_signal_match,
        "context_confidence":
            "medium" if context_known else "unknown",
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }


# =========================================================
# DATA CONSISTENCY GOVERNANCE
# =========================================================

def analyze_data_consistency(
    engine_result: dict,
    core: dict,
    activity: dict,
    sensor: dict,
    context: dict
) -> dict:
    """
    Checks whether calculated model data can be trusted
    as internally consistent.

    Does NOT invent contradictions.
    Uses only explicit consistency flags, warnings,
    reason_codes, and already calculated model outputs.

    If contradiction exists:
    - forecast should be blocked
    - clarification is required
    - human dialogue should ask what is real
    """

    reason_codes = []
    blocked_components = []
    contradictions = []
    clarification_questions = []

    consistency = engine_result.get("consistency", {})
    flags = consistency.get("flags", [])

    if not isinstance(flags, list):
        flags = []

    for flag in flags:
        contradictions.append(flag)

    consistency_checked = isinstance(consistency, dict)

    if contradictions:
        reason_codes.append("DATA_CONTRADICTION")
        blocked_components.append("forecast")
        requires_clarification = True
        status = "contradiction"

    elif consistency_checked:
        requires_clarification = False
        status = "consistent"

    else:
        requires_clarification = False
        status = "not_checked"

    if not activity.get("activity_context_ready"):
        reason_codes.append("ACTIVITY_CONTEXT_REQUIRED_FOR_CONSISTENCY")
        requires_clarification = True

        clarification_questions.append({
            "code": "ASK_ACTIVITY_CONTEXT",
            "text": {
                "ru": "Какая у вас сейчас основная деятельность: работа, учёба, спорт, уход за кем-то или другое?",
                "en": "What is your current main activity: work, study, sport, caregiving, or something else?",
                "es": "¿Cuál es tu actividad principal actual: trabajo, estudios, deporte, cuidado de alguien u otra cosa?"
            }
        })

    if contradictions:
        clarification_questions.append({
            "code": "ASK_DATA_CONTRADICTION",
            "text": {
                "ru": "Я вижу противоречие в данных. Можешь уточнить, что из этого соответствует реальности?",
                "en": "I see a contradiction in the data. Could you clarify what matches reality?",
                "es": "Veo una contradicción en los datos. ¿Puedes aclarar qué corresponde a la realidad?"
            },
            "details": contradictions
        })

    return {
        "status": status,
        "consistent": status == "consistent",
        "contradictions": contradictions,
        "requires_clarification": requires_clarification,
        "clarification_questions": clarification_questions,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }


# =========================================================
# RISK GOVERNANCE
# =========================================================

def analyze_risk_governance(
    engine_result: dict,
    core: dict,
    activity: dict,
    sensor: dict,
    context: dict,
    data_consistency: dict,
    source_failure: dict
) -> dict:

    reason_codes = []
    blocked_components = []

    s_data = engine_result.get("s", {})

    if not isinstance(s_data, dict):
        s_data = {}

    critical_override = bool(
        s_data.get("critical_override", False)
    )

    if critical_override:
        risk_level = "critical"
        reason_codes.append("CRITICAL_OVERRIDE")

    elif source_failure.get("critical_signal_possible"):
        risk_level = "critical"
        reason_codes.append("CRITICAL_SIGNAL_REQUIRES_SAFETY_ROUTING")
        blocked_components.append("forecast")

    elif data_consistency.get("status") == "contradiction":
        risk_level = "medium"
        reason_codes.append("DATA_CONTRADICTION")

    elif not core.get("state_conclusion_ready"):
        risk_level = "medium"
        reason_codes.append("NOT_ENOUGH_DATA")

    else:
        risk_level = "low"

    forecast_ready = (
        core.get("state_conclusion_ready")
        and core.get("delta_ready")
        and activity.get("activity_context_ready")
        and data_consistency.get("status") != "contradiction"
        and not critical_override
    )

    recommendation_ready = (
        core.get("state_conclusion_ready")
        and data_consistency.get("status") != "contradiction"
        and not critical_override
    )

    if not forecast_ready:
        reason_codes.append("FORECAST_BLOCKED")

    if not recommendation_ready:
        reason_codes.append("RECOMMENDATION_BLOCKED")

    interruption = {
        "ask_now":
            risk_level in ["high", "critical"]
            or data_consistency.get("requires_clarification"),
        "ask_later":
            risk_level in ["low", "medium"]
            and not data_consistency.get("requires_clarification"),
        "channel": "chat",
        "safety_override": risk_level == "critical",
    }

    next_questions = engine_result.get("next_questions", [])

    return {
        "risk_level": risk_level,
        "forecast_ready": forecast_ready,
        "recommendation_ready": recommendation_ready,
        "requires_safety_routing":
            source_failure.get("requires_safety_routing", False),
        "interruption": interruption,
        "next_questions": next_questions,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }

# =========================================================
# STRUCTURAL FORECAST READINESS
# =========================================================

def analyze_structural_forecast_readiness(
    core: dict,
    activity: dict,
    data_consistency: dict,
    risk: dict
) -> dict:
    reason_codes = []
    blocked_components = []

    critical = risk.get("risk_level") == "critical"

    base_ready = (
        core.get("state_conclusion_ready", False)
        and core.get("pressure_ready", False)
        and activity.get("activity_context_ready", False)
        and data_consistency.get("status") != "contradiction"
        and not critical
    )

    delta_interpretation_ready = (
        base_ready
        and core.get("delta_ready", False)
    )

    hidden_factor_detection_ready = (
        delta_interpretation_ready
    )

    constellation_interpretation_ready = (
        base_ready
    )

    structural_forecast_ready = (
        base_ready
        and delta_interpretation_ready
    )

    if not core.get("state_conclusion_ready", False):
        reason_codes.append("STRUCTURAL_FORECAST_BLOCKED_STATE_NOT_READY")
        blocked_components.append("structural_forecast")

    if not core.get("pressure_ready", False):
        reason_codes.append("STRUCTURAL_FORECAST_BLOCKED_PRESSURE_NOT_READY")
        blocked_components.append("structural_forecast")

    if base_ready and not core.get("delta_ready", False):
        reason_codes.append("STRUCTURAL_FORECAST_DELTA_NOT_READY_LIMITED_MODE")
        blocked_components.append("delta_interpretation")
        blocked_components.append("hidden_factor_detection")

    elif not core.get("delta_ready", False):
        reason_codes.append("DELTA_NOT_READY")
        blocked_components.append("delta_interpretation")
        blocked_components.append("hidden_factor_detection")

    if not activity.get("activity_context_ready", False):
        reason_codes.append("STRUCTURAL_FORECAST_BLOCKED_ACTIVITY_CONTEXT_UNKNOWN")
        blocked_components.append("structural_forecast")

    if data_consistency.get("status") == "contradiction":
        reason_codes.append("STRUCTURAL_FORECAST_BLOCKED_DATA_CONTRADICTION")
        blocked_components.append("structural_forecast")

    if critical:
        reason_codes.append("STRUCTURAL_FORECAST_BLOCKED_CRITICAL")
        blocked_components.append("structural_forecast")

    if structural_forecast_ready:
        structural_forecast_mode = "full"
        forecast_scope = "structural_full"
    elif base_ready:
        structural_forecast_mode = "limited"
        forecast_scope = "structural_limited"
    else:
        structural_forecast_mode = "none"
        forecast_scope = "none"

    return {
        "base_ready": base_ready,
        "structural_forecast_ready": structural_forecast_ready,
        "structural_forecast_mode": structural_forecast_mode,
        "forecast_scope": forecast_scope,
        "delta_interpretation_ready": delta_interpretation_ready,
        "hidden_factor_detection_ready": hidden_factor_detection_ready,
        "constellation_interpretation_ready": constellation_interpretation_ready,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }


# =========================================================
# STATE RISK READINESS
# =========================================================

def analyze_state_risk_readiness(
    structural_forecast: dict,
    risk: dict
) -> dict:
    reason_codes = []
    blocked_components = []

    critical = risk.get("risk_level") == "critical"

    state_risk_initial_ready = (
        structural_forecast.get("base_ready", False)
        and not critical
    )

    state_risk_full_ready = (
        structural_forecast.get("structural_forecast_ready", False)
        and not critical
    )

    if not structural_forecast.get("base_ready", False):
        reason_codes.append("STATE_RISK_INITIAL_BLOCKED_BASE_NOT_READY")
        blocked_components.append("state_risk_initial")

    if (
        structural_forecast.get("base_ready", False)
        and not structural_forecast.get("structural_forecast_ready", False)
    ):
        reason_codes.append("STATE_RISK_FULL_BLOCKED_STRUCTURAL_FORECAST_NOT_FULL")
        blocked_components.append("state_risk_full")

    if critical:
        reason_codes.append("STATE_RISK_INITIAL_BLOCKED_CRITICAL")
        blocked_components.append("state_risk_initial")
        blocked_components.append("state_risk_full")

    if state_risk_full_ready:
        state_risk_mode = "initial_full"
    elif state_risk_initial_ready:
        state_risk_mode = "initial_limited"
    else:
        state_risk_mode = "none"

    return {
        "state_risk_initial_ready": state_risk_initial_ready,
        "state_risk_full_ready": state_risk_full_ready,
        "state_risk_mode": state_risk_mode,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }


# =========================================================
# TRAJECTORY READINESS
# =========================================================

def analyze_trajectory_readiness(
    engine_result: dict,
    core: dict,
    activity: dict,
    data_consistency: dict,
    risk: dict
) -> dict:
    reason_codes = []
    blocked_components = []

    history = engine_result.get("history", {})
    metadata = engine_result.get("metadata", {})

    if not isinstance(history, dict):
        history = {}

    if not isinstance(metadata, dict):
        metadata = {}

    repeated_measurements_count = history.get(
        "repeated_measurements_count",
        0
    )

    comparable_measurements = bool(
        history.get("comparable_measurements", False)
    )

    shared_time_reference_ready = bool(
        metadata.get("shared_time_reference_ready", False)
    )

    coverage_comparable = bool(
        history.get("coverage_comparable", False)
    )

    q_comparable = bool(
        history.get("q_comparable", False)
    )

    critical = risk.get("risk_level") == "critical"

    trajectory_analysis_ready = (
        repeated_measurements_count >= 2
        and comparable_measurements
        and shared_time_reference_ready
        and coverage_comparable
        and q_comparable
        and core.get("state_conclusion_ready", False)
        and activity.get("activity_context_ready", False)
        and data_consistency.get("status") != "contradiction"
        and not critical
    )

    if repeated_measurements_count < 2:
        reason_codes.append("TRAJECTORY_NOT_READY_INSUFFICIENT_REPEATED_MEASUREMENTS")
        blocked_components.append("trajectory_analysis")

    if not comparable_measurements:
        reason_codes.append("TRAJECTORY_NOT_READY_MEASUREMENTS_NOT_COMPARABLE")
        blocked_components.append("trajectory_analysis")

    if not shared_time_reference_ready:
        reason_codes.append("TRAJECTORY_NOT_READY_SHARED_TIME_REFERENCE_MISSING")
        blocked_components.append("trajectory_analysis")

    if not coverage_comparable:
        reason_codes.append("TRAJECTORY_NOT_READY_COVERAGE_NOT_COMPARABLE")
        blocked_components.append("trajectory_analysis")

    if not q_comparable:
        reason_codes.append("TRAJECTORY_NOT_READY_Q_NOT_COMPARABLE")
        blocked_components.append("trajectory_analysis")

    if data_consistency.get("status") == "contradiction":
        reason_codes.append("TRAJECTORY_NOT_READY_DATA_CONTRADICTION")
        blocked_components.append("trajectory_analysis")

    if critical:
        reason_codes.append("TRAJECTORY_NOT_READY_CRITICAL")
        blocked_components.append("trajectory_analysis")

    
    comparable_history_ready = (
        repeated_measurements_count >= 2
        and comparable_measurements
        and shared_time_reference_ready
    )

    limited_trajectory_ready = (
        comparable_history_ready
        and core.get("state_conclusion_ready", False)
        and activity.get("activity_context_ready", False)
        and data_consistency.get("status") != "contradiction"
        and not critical
    )

    if trajectory_analysis_ready:
        readiness_status = "ready"
    elif limited_trajectory_ready:
        readiness_status = "limited"
    elif repeated_measurements_count >= 2:
        readiness_status = "not_comparable"
    else:
        readiness_status = "not_ready"

    return {
        "trajectory_analysis_ready": trajectory_analysis_ready,
        "trajectory_risk_ready": trajectory_analysis_ready,
        "trajectory_readiness_status": readiness_status,
        "comparable_history_ready": comparable_history_ready,
        "limited_trajectory_ready": limited_trajectory_ready,
        "repeated_measurements_count": repeated_measurements_count,
        "comparable_measurements": comparable_measurements,
        "shared_time_reference_ready": shared_time_reference_ready,
        "coverage_comparable": coverage_comparable,
        "q_comparable": q_comparable,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }

# =========================================================
# VNEXT SIGNAL READINESS
# =========================================================

def analyze_vnext_signal_readiness(engine_result: dict) -> dict:
    reason_codes = []
    blocked_components = []

    vnext_data = engine_result.get("vnext_signals", {})
    signals = vnext_data.get("signals", {})

    if not isinstance(signals, dict):
        signals = {}

    def signal_ready(name: str, min_coverage: float = 0.5) -> bool:
        item = signals.get(name, {})

        if not isinstance(item, dict):
            return False

        return (
            item.get("score") is not None
            and (item.get("coverage") or 0) >= min_coverage
        )

    decision_degradation_ready = signal_ready("DecisionDegradation", 0.5)
    recovery_vulnerability_ready = signal_ready("RecoveryVulnerability", 0.5)
    learning_failure_ready = signal_ready("LearningFailure", 0.5)
    commitment_trap_ready = signal_ready("CommitmentTrap", 0.5)
    negative_spiral_ready = signal_ready("NegativeSpiral", 1.0)
    pep_ready = signal_ready("PEP", 0.5)

    vnext_signal_ready = any([
        decision_degradation_ready,
        recovery_vulnerability_ready,
        learning_failure_ready,
        commitment_trap_ready,
        negative_spiral_ready,
        pep_ready,
    ])
    
    ready_signal_count = sum([
        decision_degradation_ready,
        recovery_vulnerability_ready,
        learning_failure_ready,
        commitment_trap_ready,
        negative_spiral_ready,
        pep_ready,
    ])

    if ready_signal_count == 0:
        vnext_signal_scope = "none"
    elif ready_signal_count < 3:
        vnext_signal_scope = "limited"
    else:
        vnext_signal_scope = "broad"

    vnext_interpretation_allowed = (
        vnext_signal_ready
        and vnext_signal_scope in ["limited", "broad"]
    )

    if not decision_degradation_ready:
        reason_codes.append("VNEXT_DECISION_DEGRADATION_NOT_READY")

    if not recovery_vulnerability_ready:
        reason_codes.append("VNEXT_RECOVERY_VULNERABILITY_NOT_READY")

    if not learning_failure_ready:
        reason_codes.append("VNEXT_LEARNING_FAILURE_NOT_READY")

    if not commitment_trap_ready:
        reason_codes.append("VNEXT_COMMITMENT_TRAP_NOT_READY")

    if not negative_spiral_ready:
        reason_codes.append("VNEXT_NEGATIVE_SPIRAL_NOT_READY")

    if not pep_ready:
        reason_codes.append("VNEXT_PEP_NOT_READY")

    if not vnext_signal_ready:
        blocked_components.append("vnext_signals")

    return {
        "vnext_signal_ready": vnext_signal_ready,
        "vnext_signal_scope": vnext_signal_scope,
        "vnext_interpretation_allowed": vnext_interpretation_allowed,
        "ready_signal_count": ready_signal_count,
        "decision_degradation_ready": decision_degradation_ready,
        "recovery_vulnerability_ready": recovery_vulnerability_ready,
        "learning_failure_ready": learning_failure_ready,
        "commitment_trap_ready": commitment_trap_ready,
        "negative_spiral_ready": negative_spiral_ready,
        "pep_ready": pep_ready,
        "reason_codes": reason_codes,
        "blocked_components": blocked_components,
    }

# =========================================================
# LEARNING GOVERNANCE
# =========================================================

def analyze_learning_governance(
    engine_result: dict,
    sensor: dict,
    context: dict
) -> dict:

    return {
        "pattern_candidate_detected": False,
        "stable_candidate_detected": False,
        "calibration_update_recommended": False,
        "requires_user_confirmation": False,
        "allow_external_core_update_request": False,
        "reason_codes": [],
    }


# =========================================================
# BUILD OUTPUT
# =========================================================

def build_readiness_output(
    core: dict,
    activity: dict,
    source_access: dict,
    source_quality: dict,
    data_reliability: dict,
    data_freshness,
    source_failure: dict,
    sensor: dict,
    context: dict,
    data_consistency: dict,
    risk: dict,
    structural_forecast: dict,
    state_risk: dict,
    trajectory: dict,
    vnext_signals: dict,
    learning: dict,
    investigations: dict,
) -> dict:

    internal_reason_codes = (
        core["reason_codes"]
        + activity["reason_codes"]
        + sensor["reason_codes"]
        + context["reason_codes"]
        + data_consistency["reason_codes"]
        + data_reliability["reason_codes"]
        + data_freshness["reason_codes"]
        + source_failure["reason_codes"]
        + risk["reason_codes"]
        + structural_forecast["reason_codes"]
        + state_risk["reason_codes"]
        + trajectory["reason_codes"]
        + vnext_signals["reason_codes"]
        + learning["reason_codes"]
    )

    blocked_components = (
        core["blocked_components"]
        + activity["blocked_components"]
        + sensor["blocked_components"]
        + context["blocked_components"]
        + data_consistency["blocked_components"]
        + data_reliability["blocked_components"]
        + data_freshness["blocked_components"]
        + source_failure["blocked_components"]
        + structural_forecast["blocked_components"]
        + state_risk["blocked_components"]
        + trajectory["blocked_components"]
        + vnext_signals["blocked_components"]
        + risk["blocked_components"]
    )

    trust_level = compute_trust_level(
        core,
        activity,
        data_consistency,
        risk
    )

    ordinary_interpretation_allowed = (
        core["state_conclusion_ready"]
        and data_consistency["status"] != "contradiction"
        and risk["risk_level"] != "critical"
    )

    safety_result_valid = (
        risk["risk_level"] == "critical"
        or source_failure["critical_signal_possible"]
    )

    can_trust_result = (
        ordinary_interpretation_allowed
        or safety_result_valid
    )

    public_summary = build_public_summary(
        core,
        data_consistency
    )

    vnext_summary = build_vnext_summary(
        vnext_signals
    )

    investigation_summary = build_investigation_summary(
        investigations
    )
    investigation_questions = build_investigation_questions(
        investigations
    )
    human_questions = build_human_questions(
        risk,
        data_consistency
    )

    communication_requests = build_communication_requests(
        data_consistency,
        source_failure,
        risk,
        data_freshness,
        investigations
    )

    data_acquisition_requests = build_data_acquisition_requests(
        sensor,
        source_access,
        source_failure,
        data_freshness,
        data_consistency
    )

    return {
        "internal": {
            "can_trust_result": can_trust_result,
            "ordinary_interpretation_allowed":
                ordinary_interpretation_allowed,
            "safety_result_valid":
                safety_result_valid,
            "core": core,
            "activity": activity,
            "source_access": source_access,
            "data_consistency": data_consistency,
            "data_reliability": data_reliability,
            "data_freshness": data_freshness,
            "source_failure": source_failure,
            "sensor": sensor,
            "context": context,
            "risk": risk,
            "communication_requests": communication_requests,
            "data_acquisition_requests": data_acquisition_requests,
            "learning": learning,
            "trust_level": trust_level,
            "structural_forecast": structural_forecast,
            "state_risk": state_risk,
            "trajectory": trajectory,
            "investigations": investigations,
            "investigation_summary": investigation_summary,
            "investigation_questions": investigation_questions,
            "vnext_signals": vnext_signals,
            "vnext_summary": vnext_summary,
            "reason_codes": list(dict.fromkeys(
                internal_reason_codes
            )),
            "blocked_components": list(dict.fromkeys(
                blocked_components
            )),
        },

        "human_dialogue": {
            "requires_clarification":
                data_consistency["requires_clarification"],
            "questions_for_user":
                human_questions,
            "safe_summary":
                public_summary,
            "investigation_summary":
                investigation_summary,
            "investigation_questions":
                investigation_questions,
            "vnext_summary":
                vnext_summary["summary"],
            "vnext_interpretation_allowed":
                vnext_signals["vnext_interpretation_allowed"],
        },

        "public": {
            "can_trust_result": can_trust_result,
            "ordinary_interpretation_allowed":
                ordinary_interpretation_allowed,
            "safety_result_valid":
                safety_result_valid,
            "state_conclusion_ready":
                core["state_conclusion_ready"],
            "structural_forecast_allowed":
                structural_forecast["structural_forecast_ready"],
       
            "structural_forecast_mode":
                structural_forecast["structural_forecast_mode"],

            "delta_interpretation_allowed":
                structural_forecast["delta_interpretation_ready"],

            "hidden_factor_detection_allowed":
                structural_forecast["hidden_factor_detection_ready"],

            "constellation_interpretation_allowed":
                structural_forecast["constellation_interpretation_ready"],

            "state_risk_initial_allowed":
                state_risk["state_risk_initial_ready"],
        
            "state_risk_full_allowed":
                state_risk["state_risk_full_ready"],

            "state_risk_mode":
                state_risk["state_risk_mode"],

            "trajectory_analysis_allowed":
                trajectory["trajectory_analysis_ready"],

            "trajectory_risk_allowed":
                trajectory["trajectory_risk_ready"],

            "trajectory_readiness_status":
                trajectory["trajectory_readiness_status"],
    
            "limited_trajectory_allowed":
                trajectory["limited_trajectory_ready"],

            "comparable_history_ready":
                trajectory["comparable_history_ready"],
           
            "vnext_signal_ready":
                vnext_signals["vnext_signal_ready"],
          
            "vnext_signal_scope":
                vnext_signals["vnext_signal_scope"],

            "vnext_interpretation_allowed":
                vnext_signals["vnext_interpretation_allowed"],

            "vnext_ready_signal_count":
                vnext_signals["ready_signal_count"],

            "vnext_summary":
                vnext_summary["summary"],            

            "decision_degradation_signal_ready":
                vnext_signals["decision_degradation_ready"],

            "recovery_vulnerability_signal_ready":
                vnext_signals["recovery_vulnerability_ready"],

            "learning_failure_signal_ready":
                vnext_signals["learning_failure_ready"],

            "commitment_trap_signal_ready":
                vnext_signals["commitment_trap_ready"],

            "negative_spiral_signal_ready":
                vnext_signals["negative_spiral_ready"],

            "pep_signal_ready":
                vnext_signals["pep_ready"],

            "forecast_allowed":
                structural_forecast["structural_forecast_ready"],

            "forecast_scope":
                structural_forecast["forecast_scope"],
            "interpretation_scope":
                structural_forecast["forecast_scope"],
            "recommendation_allowed":
                risk["recommendation_ready"],
            "trust_level":
                trust_level,
            "risk_level":
                risk["risk_level"],
            "communication_required":
                communication_requests["communication_required"],
            "data_acquisition_required":
                data_acquisition_requests["data_acquisition_required"],
            "investigation_active":
                investigations["investigation_active"],
            "active_investigation_count":
                len(investigations.get("active_hypotheses", [])),
            "investigation_summary":
                investigation_summary,
            "data_reliability": 
                data_reliability["overall_reliability"],
            "data_freshness": data_freshness["overall_freshness"],
            "source_failure_detected":
                source_failure["failure_detected"],
            "requires_device_check":
                source_failure["requires_device_check"],
            "requires_safety_routing":
                risk.get("requires_safety_routing", False),
            "data_consistency_status":
                data_consistency["status"],
            "requires_clarification":
                data_consistency["requires_clarification"],
            "summary_text":
                public_summary,
            "public_reasons":
                build_public_reasons(
                internal_reason_codes
                ),
            "next_questions":
                risk.get("next_questions", []),
        }
    }

# =========================================================
# INVESTIGATION QUESTIONS
# =========================================================

def build_investigation_questions(
    investigations: dict
) -> list:

    questions = []

    active = investigations.get(
        "active_hypotheses",
        []
    )

    if not isinstance(active, list):
        active = []

    for item in active:

        if not isinstance(item, dict):
            continue

        if item.get("type") == "r_k_mismatch":

            domain = item.get("domain")

            questions.append({
                "code": "ASK_R_K_MISMATCH",
                "domain": domain,
                "reason_code": item.get("reason_code"),
                "text": {
                    "ru": (
                        "Проявления в этой области выглядят сильнее, "
                        "чем ожидается по указанному ресурсу. "
                        "Есть ли сейчас боль, болезнь, недосып, перегрузка "
                        "или другой фактор, который может это объяснить?"
                    ),
                    "en": (
                        "The manifestations in this area look stronger "
                        "than expected from the reported resource level. "
                        "Is there pain, illness, lack of sleep, overload, "
                        "or another factor that may explain this?"
                    ),
                    "es": (
                        "Las manifestaciones en esta área parecen más fuertes "
                        "de lo esperado según el nivel de recurso indicado. "
                        "¿Hay dolor, enfermedad, falta de sueño, sobrecarga "
                        "u otro factor que pueda explicarlo?"
                    ),
                },
            })

    return questions

# =========================================================
# INVESTIGATION SUMMARY
# =========================================================

def build_investigation_summary(
    investigations: dict
) -> str:

    active = investigations.get(
        "active_hypotheses",
        []
    )

    if not active:
        return ""

    count = len(active)

    if count == 1:
        return (
            "Есть один сигнал, который требует уточнения, "
            "но сам по себе не является противоречием или выводом."
        )

    return (
        f"Есть {count} сигналов, которые требуют уточнения, "
        "но сами по себе не являются противоречиями или выводами."
    )

# =========================================================
# VNEXT SUMMARY
# =========================================================

def build_vnext_summary(
    vnext_signals: dict
) -> dict:

    ready_count = vnext_signals.get(
        "ready_signal_count",
        0
    )

    scope = vnext_signals.get(
        "vnext_signal_scope",
        "none"
    )

    if ready_count == 0:
        summary = (
            "Недостаточно данных для оценки vNext-сигналов."
        )

    elif ready_count < 3:
        summary = (
            "Доступны отдельные vNext-сигналы, "
            "но интерпретация ограничена."
        )

    else:
        summary = (
            "Доступно несколько vNext-сигналов "
            "для расширенной интерпретации."
        )

    return {
        "ready_signal_count": ready_count,
        "scope": scope,
        "summary": summary,
    }

# =========================================================
# OUTPUT HELPERS
# =========================================================

def build_public_summary(
    core: dict,
    data_consistency: dict
) -> str:

    if data_consistency["status"] == "contradiction":
        return (
            "Данные требуют уточнения: обнаружено противоречие. "
            "Без уточнения нельзя делать надёжный вывод или прогноз."
        )

    if not core["state_conclusion_ready"]:
        return (
            "Недостаточно данных для уверенного вывода."
        )

    if data_consistency["requires_clarification"]:
        return (
            "Данных частично достаточно, но требуется уточнение контекста."
        )

    return (
        "Данные достаточны для базовой интерпретации."
    )


def build_human_questions(
    risk: dict,
    data_consistency: dict
) -> list:

    questions = []

    questions.extend(
        data_consistency.get(
            "clarification_questions",
            []
        )
    )

    if not questions:
        questions.extend(
            risk.get(
                "next_questions",
                []
            )
        )

    return questions

# =========================================================
# INVESTIGATION SIGNAL HELPERS
# =========================================================

def detect_r_k_mismatch_investigations(
    engine_result: dict
) -> list:

    delta_data = engine_result.get("delta", {})

    if not isinstance(delta_data, dict):
        return []

    findings = []

    for domain, item in delta_data.items():

        if not isinstance(item, dict):
            continue

        if item.get("calculated") is not True:
            continue

        delta_value = item.get("delta")

        if delta_value is None:
            continue

        abs_delta = abs(delta_value)

        if abs_delta < 2.0:
            continue

        if delta_value <= -2.0:
            direction = "manifestations_higher_than_resource_deficit"
        else:
            direction = "resource_deficit_higher_than_manifestations"

        findings.append({
            "id": f"r_k_mismatch_{domain}",
            "type": "r_k_mismatch",
            "domain": domain,
            "status": "active",
            "confidence": "medium",
            "reason_code": "R_K_MISMATCH_DETECTED",
            "delta": delta_value,
            "abs_delta": abs_delta,
            "direction": direction,
            "requires_clarification": True,
            "ttl": "short_term",
        })

    return findings

# =========================================================
# INVESTIGATIONS / HYPOTHESES
# =========================================================

def analyze_investigations(
    engine_result: dict,
    data_consistency: dict,
    source_failure: dict,
    data_freshness: dict,
    risk: dict
) -> dict:

    active_hypotheses = []
    requires_revalidation = []
    resolved_items = []

    investigation_active = False

    previous_investigations = engine_result.get(
        "previous_investigations",
        []
    )

    if not isinstance(previous_investigations, list):
        previous_investigations = []

    r_k_mismatch_findings = detect_r_k_mismatch_investigations(
        engine_result
    )

    previous_ids = set()

    for item in previous_investigations:

        if not isinstance(item, dict):
            continue

        item_id = item.get("id")

        if item_id:
            previous_ids.add(item_id)

    continued_investigations = []
    revalidation_needed = []

    current_r_k_ids = {
        finding.get("id")
        for finding in r_k_mismatch_findings
        if isinstance(finding, dict)
    }

    for item in previous_investigations:

        if not isinstance(item, dict):
            continue

        item_id = item.get("id")

        if item_id == "data_contradiction":

            if data_consistency.get("status") == "contradiction":
                continued_investigations.append({
                    **item,
                    "status": "continued",
                    "current_signal": True,
                })
            else:
                revalidation_needed.append({
                    **item,
                    "status": "needs_revalidation",
                    "current_signal": False,
                    "reason_code": "PREVIOUS_CONTRADICTION_NOT_SEEN_NOW",
                })

        if item_id == "source_failure":

            if source_failure.get("failure_detected"):
                continued_investigations.append({
                    **item,
                    "status": "continued",
                    "current_signal": True,
                })
            else:
                revalidation_needed.append({
                    **item,
                    "status": "needs_revalidation",
                    "current_signal": False,
                    "reason_code": "PREVIOUS_SOURCE_FAILURE_NOT_SEEN_NOW",
                })

        if item_id == "critical_state_monitoring":

            if risk.get("risk_level") == "critical":
                continued_investigations.append({
                    **item,
                    "status": "continued",
                    "current_signal": True,
                })
            else:
                revalidation_needed.append({
                    **item,
                    "status": "needs_revalidation",
                    "current_signal": False,
                    "reason_code": "PREVIOUS_CRITICAL_STATE_NOT_SEEN_NOW",
                })

        if (
            isinstance(item_id, str)
            and item_id.startswith("r_k_mismatch_")
        ):

            if item_id in current_r_k_ids:
                continued_investigations.append({
                    **item,
                    "status": "continued",
                    "current_signal": True,
                })
            else:
                revalidation_needed.append({
                    **item,
                    "status": "needs_revalidation",
                    "current_signal": False,
                    "reason_code": "PREVIOUS_R_K_MISMATCH_NOT_SEEN_NOW",
                })

    for finding in r_k_mismatch_findings:

        finding_id = finding.get("id")

        if finding_id in previous_ids:
            continue

        investigation_active = True
        active_hypotheses.append(finding)

    if data_consistency.get("status") == "contradiction":

        investigation_active = True

        active_hypotheses.append({
            "id": "data_contradiction",
            "type": "reality_conflict",
            "status": "active",
            "confidence": "medium",
            "reason_code": "DATA_CONTRADICTION",
            "requires_clarification": True,
            "ttl": "short_term",
        })

    if (
        source_failure.get("failure_detected")
        and "source_failure" not in previous_ids
    ):

        investigation_active = True

        active_hypotheses.append({
            "id": "source_failure",
            "type": "sensor_or_source_problem",
            "status": "active",
            "confidence": "medium",
            "reason_code": "SOURCE_FAILURE_DETECTED",
            "requires_clarification": True,
            "ttl": "short_term",
        })

    refresh_items = data_freshness.get(
        "refresh_recommended",
        []
    )

    if refresh_items:

        investigation_active = True

        requires_revalidation.append({
            "type": "data_refresh",
            "components": refresh_items,
            "priority": "low",
            "reason_code": "DATA_REFRESH_RECOMMENDED",
        })

    if (
        risk.get("risk_level") == "critical"
        and "critical_state_monitoring" not in previous_ids
    ):

        investigation_active = True

        active_hypotheses.append({
            "id": "critical_state_monitoring",
            "type": "critical_observation",
            "status": "active",
            "confidence": "high",
            "reason_code": "CRITICAL_STATE",
            "requires_clarification": False,
            "ttl": "immediate",
        })

    return {
        "investigation_active": investigation_active,
        "active_hypotheses": active_hypotheses,
        "requires_revalidation": requires_revalidation,
        "resolved_items": resolved_items,
        "previous_investigations_count":
            len(previous_investigations),
        "continued_investigations":
            continued_investigations,
        "revalidation_needed":
            revalidation_needed,
    }

# =========================================================
# DATA ACQUISITION REQUESTS
# =========================================================

def build_data_acquisition_requests(
    sensor: dict,
    source_access: dict,
    source_failure: dict,
    data_freshness: dict,
    data_consistency: dict
) -> dict:

    sensor_requests = []
    calibration_requests = []
    context_requests = []
    human_input_requests = []
    
    sensors_available = (
        source_access.get("sensors") == "available"
    )

    baselines_available = (
        source_access.get("baselines") == "available"
    )

    context_available = (
        source_access.get("context") == "available"
    )

    if (
        sensors_available
        and not sensor.get("sensor_data_ready")
):
        sensor_requests.append({
            "type": "sensor_data_request",
            "target": "sensor_layer",
            "priority": "medium",
            "reason_code": "NO_CURRENT_SENSOR_DATA",
            "requested_data": [
                "current_biosignals"
            ],
            "expected_response_target": "sensor_signals",
        })

    if (
        baselines_available
        and not sensor.get("baseline_ready")
):
        calibration_requests.append({
            "type": "baseline_request",
            "target": "calibration_layer",
            "priority": "medium",
            "reason_code": "NO_SENSOR_BASELINE",
            "requested_data": [
                "contextual_baseline"
            ],
            "expected_response_target": "calibration_signals",
        })

    if (
        context_available
        and not sensor.get("context_ready")
):
        context_requests.append({
            "type": "context_data_request",
            "target": "context_layer",
            "priority": "medium",
            "reason_code": "NO_CONTEXT_FOR_BIOSIGNAL_INTERPRETATION",
            "requested_data": [
                "current_context"
            ],
            "expected_response_target": "context",
        })

    if source_failure.get("requires_device_check"):
        sensor_requests.append({
            "type": "sensor_device_check",
            "target": "sensor_layer",
            "priority": "medium",
            "reason_code": "SOURCE_DEVICE_CHECK_REQUIRED",
            "requested_data": [
                "device_status",
                "signal_quality",
                "connection_status"
            ],
            "expected_response_target": "sensor_status",
        })

    refresh_items = data_freshness.get(
        "refresh_recommended",
        []
    )

    if refresh_items:
        sensor_requests.append({
            "type": "fresh_data_request",
            "target": "data_source_layer",
            "priority": "low",
            "reason_code": "DATA_REFRESH_RECOMMENDED",
            "requested_data": refresh_items,
            "expected_response_target": "updated_inputs",
        })

    if data_consistency.get("requires_clarification"):
        human_input_requests.append({
            "type": "human_clarification_request",
            "target": "ray_communicator",
            "priority": "medium",
            "reason_code": "DATA_CLARIFICATION_REQUIRED",
            "expected_response_target": "answers",
        })

    all_requests = (
        sensor_requests
        + calibration_requests
        + context_requests
        + human_input_requests
    )

    return {
        "data_acquisition_required": bool(all_requests),
        "sensor_requests": sensor_requests,
        "calibration_requests": calibration_requests,
        "context_requests": context_requests,
        "human_input_requests": human_input_requests,
        "all_requests": all_requests,
    }

# =========================================================
# COMMUNICATION REQUESTS
# =========================================================

def build_communication_requests(
    data_consistency: dict,
    source_failure: dict,
    risk: dict,
    data_freshness: dict,
    investigations: dict
) -> dict:

    internal_requests = []
    human_requests = []
    external_requests = []

    if data_consistency.get("requires_clarification"):
        internal_requests.append({
            "type": "clarification_needed",
            "priority": "medium",
            "target": "ray_communicator",
            "reason_code": "DATA_CLARIFICATION_REQUIRED",
        })

        human_requests.append({
            "type": "clarification",
            "priority": "medium",
            "route": "personal_human_channel",
            "reason_code": "DATA_CLARIFICATION_REQUIRED",
        })

    if source_failure.get("requires_device_check"):
        internal_requests.append({
            "type": "device_check_needed",
            "priority": "medium",
            "target": "ray_communicator",
            "reason_code": "SOURCE_DEVICE_CHECK_REQUIRED",
        })

        human_requests.append({
            "type": "device_check",
            "priority": "medium",
            "route": "personal_human_channel",
            "reason_code": "SOURCE_DEVICE_CHECK_REQUIRED",
        })

    if risk.get("requires_safety_routing"):
        internal_requests.append({
            "type": "safety_routing_needed",
            "priority": "critical",
            "target": "ray_safety_orchestrator",
            "reason_code": "SAFETY_ROUTING_REQUIRED",
        })

        human_requests.append({
            "type": "safety_check",
            "priority": "critical",
            "route": "personal_human_channel_or_emergency_protocol",
            "reason_code": "SAFETY_ROUTING_REQUIRED",
        })

    if data_freshness.get("refresh_recommended"):
        internal_requests.append({
            "type": "data_refresh_recommended",
            "priority": "low",
            "target": "ray_communicator",
            "reason_code": "DATA_REFRESH_RECOMMENDED",
            "components": data_freshness.get("refresh_recommended", []),
        })

        human_requests.append({
            "type": "data_refresh",
            "priority": "low",
            "route": "personal_human_channel",
            "reason_code": "DATA_REFRESH_RECOMMENDED",
            "components": data_freshness.get("refresh_recommended", []),
        })
    if investigations.get("revalidation_needed"):

        internal_requests.append({
            "type": "investigation_revalidation_needed",
            "priority": "low",
            "target": "ray_communicator",
            "reason_code": "INVESTIGATION_REVALIDATION_NEEDED",
            "items": investigations.get("revalidation_needed", []),
        })

        human_requests.append({
            "type": "investigation_revalidation",
            "priority": "low",
            "route": "personal_human_channel",
            "reason_code": "INVESTIGATION_REVALIDATION_NEEDED",
        })

    if investigations.get("active_hypotheses"):

        internal_requests.append({
            "type": "investigation_clarification_needed",
            "priority": "medium",
            "target": "ray_communicator",
            "reason_code": "INVESTIGATION_CLARIFICATION_REQUIRED",
            "items": investigations.get("active_hypotheses", []),
        })

        human_requests.append({
            "type": "investigation_clarification",
            "priority": "medium",
            "route": "personal_human_channel",
            "reason_code": "INVESTIGATION_CLARIFICATION_REQUIRED",
        })

    return {
        "communication_required": bool(
            internal_requests
            or human_requests
            or external_requests
        ),
        "internal_requests": internal_requests,
        "human_requests": human_requests,
        "external_requests": external_requests,
    }

# =========================================================
# PUBLIC REASON FILTERING
# =========================================================

PUBLIC_REASON_MAP = {

    "NOT_ENOUGH_DATA":
        "not enough data",

    "FORECAST_BLOCKED":
        "forecast unavailable",

    "RECOMMENDATION_BLOCKED":
        "recommendations unavailable",

    "DATA_CONTRADICTION":
        "data requires clarification",

    "NO_CURRENT_SENSOR_DATA":
        "sensor data unavailable",

    "NO_SENSOR_BASELINE":
        "baseline unavailable",

    "STATE_RISK_INITIAL_BLOCKED_BASE_NOT_READY":
        "state risk unavailable",

    "STATE_RISK_FULL_BLOCKED_STRUCTURAL_FORECAST_NOT_FULL":
        "state risk limited",

    "FRESHNESS_UNKNOWN":
        "data freshness unknown",

    "STRUCTURAL_FORECAST_BLOCKED_STATE_NOT_READY":
        "structural forecast unavailable",

    "STRUCTURAL_FORECAST_BLOCKED_DELTA_NOT_READY":
        "structural forecast unavailable",

    "STRUCTURAL_FORECAST_DELTA_NOT_READY_LIMITED_MODE":
        "structural forecast limited",

    "STRUCTURAL_FORECAST_BLOCKED_PRESSURE_NOT_READY":
        "structural forecast unavailable",

    "STATE_RISK_INITIAL_BLOCKED_STRUCTURAL_FORECAST_NOT_READY":
        "state risk unavailable",

    "TRAJECTORY_NOT_READY_INSUFFICIENT_REPEATED_MEASUREMENTS":
        "trajectory analysis unavailable",

    "TRAJECTORY_NOT_READY_MEASUREMENTS_NOT_COMPARABLE":
        "trajectory analysis unavailable",

    "TRAJECTORY_NOT_READY_SHARED_TIME_REFERENCE_MISSING":
        "trajectory analysis unavailable",

    "STRUCTURAL_FORECAST_BLOCKED_ACTIVITY_CONTEXT_UNKNOWN":
        "structural forecast unavailable",

    "STRUCTURAL_FORECAST_BLOCKED_DATA_CONTRADICTION":
        "structural forecast unavailable",

    "STRUCTURAL_FORECAST_BLOCKED_CRITICAL":
        "structural forecast unavailable",

    "STATE_RISK_INITIAL_BLOCKED_CRITICAL":
        "state risk unavailable",

    "TRAJECTORY_NOT_READY_COVERAGE_NOT_COMPARABLE":
        "trajectory analysis unavailable",

    "TRAJECTORY_NOT_READY_Q_NOT_COMPARABLE":
        "trajectory analysis unavailable",

    "TRAJECTORY_NOT_READY_DATA_CONTRADICTION":
        "trajectory analysis unavailable",

    "TRAJECTORY_NOT_READY_CRITICAL":
        "trajectory analysis unavailable",

    "ACTIVITY_CONTEXT_UNKNOWN":
        "activity context unavailable",

    "SOURCE_DEVICE_CHECK_REQUIRED":
        "device check recommended",

    "SAFETY_ROUTING_REQUIRED":
        "safety review required",
}


def build_public_reasons(
    internal_reason_codes: list
) -> list:

    public_reasons = []

    for code in internal_reason_codes:

        public_reason = PUBLIC_REASON_MAP.get(code)

        if public_reason:
            public_reasons.append(public_reason)

    return list(dict.fromkeys(public_reasons))



# =========================================================
# TRUST LEVEL
# =========================================================

def compute_trust_level(
    core: dict,
    activity: dict,
    data_consistency: dict,
    risk: dict
) -> str:

    if data_consistency["status"] == "contradiction":
        return "low"

    if not core["state_conclusion_ready"]:
        return "unknown"

    if not activity["activity_context_ready"]:
        return "low"

    if risk["risk_level"] == "critical":
        return "low"

    if core["delta_ready"]:
        return "medium"

    return "low"


# =========================================================
# HELPERS
# =========================================================

def has_any_domain_score(section: dict) -> bool:

    if not isinstance(section, dict):
        return False

    domains = section.get("domains")

    if not isinstance(domains, dict):
        return False

    for domain_data in domains.values():

        if not isinstance(domain_data, dict):
            continue

        if domain_data.get("score") is not None:
            return True

    return False


def has_calculated_pressure(pressure: dict) -> bool:

    if not isinstance(pressure, dict):
        return False

    calculated_count = pressure.get("calculated_count")

    if calculated_count is None:
        return False

    return calculated_count > 0


def count_calculated_delta(delta: dict) -> int:

    if not isinstance(delta, dict):
        return 0

    calculated_count = 0

    for domain_data in delta.values():

        if not isinstance(domain_data, dict):
            continue

        if domain_data.get("calculated") is True:
            calculated_count += 1

    return calculated_count

def compute_verification_level(
    questionnaires_status: str,
    sensors_status: str,
    external_status: str
) -> str:

    if (
        questionnaires_status == "available"
        and sensors_status == "available"
        and external_status == "available"
    ):
        return "high"

    if (
        questionnaires_status == "available"
        and sensors_status == "available"
    ):
        return "medium"

    if questionnaires_status == "available":
        return "basic"

    return "unknown"