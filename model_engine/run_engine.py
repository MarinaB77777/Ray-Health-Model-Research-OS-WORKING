from model_engine.coverage import compute_coverage
from model_engine.quality import compute_q_basic
from model_engine.readiness import analyze_readiness
from model_engine.vnext_signals import compute_vnext_signals
from model_engine.states import (
    determine_initial_state,
    determine_final_state,
)
from model_engine.resources import compute_r
from model_engine.markers import compute_k_self
from model_engine.loads import compute_loads
from model_engine.stress import compute_s
from model_engine.delta import compute_delta
from model_engine.consistency import compute_consistency
from model_engine.outputs import build_output
from model_engine.pilot_public_output import build_pilot_public_output
from model_engine.pressure import compute_pressure
from model_engine.multipliers import compute_multipliers
from model_engine.questions import (
    build_next_questions,
    build_data_acquisition_requests,
)
from model_engine.reasons import (
    normalize_reason_codes,
    extract_public_reasons,
)
from model_engine.warnings_engine import (
    build_warnings,
    extract_public_warnings,
)
from model_engine.forecast import build_forecast_governance
from model_engine.uncertainty import build_uncertainty_profile
from model_engine.vnext_reasons import build_vnext_reason_codes

def dedupe_list(items: list):
    result = []
    seen = set()

    for item in items:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)

    return result

def run_engine_logic(answers: dict):
    coverage_data = compute_coverage(answers)

    q_data = compute_q_basic(
        answers=answers,
        coverage_data=coverage_data,
    )

    state_data = determine_initial_state(
        coverage_data=coverage_data,
        q_data=q_data,
        answers=answers,
    )

    r_data = compute_r(answers)
    k_self_data = compute_k_self(answers)
    loads_data = compute_loads(answers)

    vnext_signals_data = compute_vnext_signals(answers)
    vnext_reason_codes = build_vnext_reason_codes(
        vnext_signals_data
    )
    pressure_data = compute_pressure(
        answers=answers,
        loads_data=loads_data,
        r_data=r_data,
    )

    multipliers_data = compute_multipliers(
        answers=answers,
        r_data=r_data,
        loads_data=loads_data,
    )

    s_data = compute_s(
        loads_data=loads_data,
        r_data=r_data,
        pressure_data=pressure_data,
        multipliers_data=multipliers_data,
    )

    if state_data["state"] == "CRITICAL":
        s_data["s_final"] = 10
        s_data["critical_override"] = True
    else:
        s_data["critical_override"] = False

    delta_data = compute_delta(
        r_data=r_data,
        k_self_data=k_self_data,
    )

    c_data = compute_consistency(delta_data)

    final_state_data = determine_final_state(
    initial_state=state_data["state"],
    s_data=s_data,
    k_self_data=k_self_data,
    consistency_data=c_data,
    coverage_data=coverage_data,
    q_data=q_data,
    r_data=r_data,
    pressure_data=pressure_data,
    delta_data=delta_data,
    )


    next_questions = build_next_questions(
        coverage_data=coverage_data,
        delta_data=delta_data,
        consistency_data=c_data,
        vnext_signals_data=vnext_signals_data,
        answers=answers,
        state=final_state_data["state"],
        limit=3,
    )

    data_acquisition_requests = build_data_acquisition_requests(
    next_questions=next_questions,
    )

    confidence = "low"

    if coverage_data["coverage"] >= 0.6 and q_data["q_global"] <= 1:
        confidence = "medium"

    if coverage_data["coverage"] >= 0.8 and q_data["q_global"] == 0:
        confidence = "high"

    combined_reason_codes = dedupe_list(
        state_data.get("reason_codes", [])
        + final_state_data.get("reason_codes", [])
        + pressure_data.get("reason_codes", [])
        + vnext_reason_codes
    )
    combined_raw_warnings = (
        state_data.get("warnings", [])
        + pressure_data.get("warnings", [])
    )

    normalized_reasons = normalize_reason_codes(combined_reason_codes)
    public_reasons = extract_public_reasons(normalized_reasons)

    normalized_warnings = build_warnings(combined_reason_codes)
    public_warnings = extract_public_warnings(normalized_warnings)

    forecast_data = build_forecast_governance(
        state=final_state_data["state"],
        confidence=confidence,
        coverage=coverage_data["coverage"],
        q_global=q_data["q_global"],
        c_final=c_data["c_final"],
        s_data=s_data,
        delta_data=delta_data,
        reason_codes=combined_reason_codes,
    )

    uncertainty_data = build_uncertainty_profile(
        coverage=coverage_data["coverage"],
        q_global=q_data["q_global"],
        c_final=c_data["c_final"],
        state=final_state_data["state"],
        forecast_data=forecast_data,
        delta_data=delta_data,
    )

    output_data = build_output(
        state=final_state_data["state"],
        confidence=confidence,
        coverage=coverage_data["coverage"],
        q_global=q_data["q_global"],
        c_final=c_data["c_final"],
        s_data=s_data,
        r_data=r_data,
        k_self_data=k_self_data,
        delta_data=delta_data,
        warnings=public_warnings,
        public_reasons=public_reasons,
        forecast=forecast_data,
        next_questions=next_questions,
        uncertainty_data=uncertainty_data,
    )

    result = {
        "initial_state": state_data["state"],
        "state": final_state_data["state"],
        "confidence": confidence,
        "engine_location": "backend",

        # Readiness compatibility

        "history": {},

        "metadata": {
            "shared_time_reference_ready": False,
        },

        "sources": {
            "questionnaires": True,
            "sensors": False,
            "baselines": False,
            "history": False,
            "context": False,
            "external_verification": False,
        },

        "coverage": coverage_data["coverage"],
        "missing_fields": coverage_data["missing_fields"],
        "q_global": q_data["q_global"],

        "warnings": combined_raw_warnings,
        "normalized_warnings": normalized_warnings,
        "public_warnings": public_warnings,

        "reason_codes": combined_reason_codes,
        "normalized_reasons": normalized_reasons,
        "public_reasons": public_reasons,

        "forecast": forecast_data,
        "uncertainty": uncertainty_data,

        "r": r_data,
        "k_self": k_self_data,
        "vnext_signals": vnext_signals_data,
        "loads": loads_data,
        "pressure": pressure_data,
        "multipliers": multipliers_data,
        "s": s_data,
        "delta": delta_data,
        "consistency": c_data,
        "c_final": c_data["c_final"],

        "next_questions": next_questions,
        "data_acquisition_requests": (
            data_acquisition_requests
        ),
        "output": output_data,
    }
    readiness_data = analyze_readiness(result)

    result["readiness"] = readiness_data

    pilot_public_output = build_pilot_public_output(result)

    result["pilot_public_output"] = pilot_public_output

    return result
