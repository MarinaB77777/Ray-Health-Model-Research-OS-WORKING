def count_valid_calculated_domains(delta_data: dict):
    count = 0

    for item in delta_data.values():
        if item.get("calculated") is True:
            count += 1

    return count

def build_trajectory_factors(reason_codes: list):
    factors = []

    if "VNEXT_OPTION_SPACE_COLLAPSE" in reason_codes:
        factors.append({
            "code": "OPTION_SPACE_COLLAPSE",
            "severity": "caution",
        })

    if "VNEXT_HOPELESSNESS_SIGNAL" in reason_codes:
        factors.append({
            "code": "HOPELESSNESS_SIGNAL",
            "severity": "caution",
        })

    if "VNEXT_NEGATIVE_SPIRAL" in reason_codes:
        factors.append({
            "code": "NEGATIVE_SPIRAL",
            "severity": "caution",
        })

    if "VNEXT_RESOURCE_EXHAUSTION" in reason_codes:
        factors.append({
            "code": "RESOURCE_EXHAUSTION",
            "severity": "caution",
        })

    return factors

def build_forecast_governance(
    state: str,
    confidence: str,
    coverage: float,
    q_global: float,
    c_final: float,
    s_data: dict,
    delta_data: dict,
    reason_codes: list,
):
    critical_override = s_data.get("critical_override") is True
    calculated_domains = count_valid_calculated_domains(delta_data)
    trajectory_factors = build_trajectory_factors(reason_codes)

    if state == "CRITICAL" or critical_override:
        return {
            "allowed": False,
            "reason": "CRITICAL_STATE",
            "confidence": confidence,
            "allowed_scope": "none",
            "trajectory_factors": trajectory_factors,
        }

    if coverage < 0.4 or "LOW_COVERAGE" in reason_codes:
        return {
            "allowed": False,
            "reason": "LOW_COVERAGE",
            "confidence": confidence,
            "allowed_scope": "none",
            "trajectory_factors": trajectory_factors,
        }

    if "STATE_NOT_ENOUGH_DATA" in reason_codes:
        return {
            "allowed": False,
            "reason": "STATE_NOT_ENOUGH_DATA",
            "confidence": confidence,
            "allowed_scope": "none",
            "trajectory_factors": trajectory_factors,
        }

    if state == "HIDDEN_FACTOR":
        return {
            "allowed": False,
            "reason": "HIDDEN_FACTOR",
            "confidence": confidence,
            "allowed_scope": "trend_only",
            "trajectory_factors": trajectory_factors,
        }

    if state == "CONSISTENCY_FAILURE" or c_final > 4:
        return {
            "allowed": False,
            "reason": "CONSISTENCY_FAILURE",
            "confidence": confidence,
            "allowed_scope": "none",
            "trajectory_factors": trajectory_factors,
        }

    if q_global > 1.5:
        return {
            "allowed": False,
            "reason": "LOW_QUALITY",
            "confidence": confidence,
            "allowed_scope": "none",
            "trajectory_factors": trajectory_factors,
        }

    if calculated_domains < 3:
        return {
            "allowed": False,
            "reason": "INSUFFICIENT_DOMAIN_COVERAGE",
            "confidence": confidence,
            "allowed_scope": "trend_only",
            "trajectory_factors": trajectory_factors,
        }

    if state == "FORECAST":
        return {
            "allowed": True,
            "reason": "FORECAST_ALLOWED",
            "confidence": confidence,
            "allowed_scope": "short_term",
            "trajectory_factors": trajectory_factors,
        }

    if state == "DIAGNOSTIC":
        return {
            "allowed": False,
            "reason": "DIAGNOSTIC_ONLY",
            "confidence": confidence,
            "allowed_scope": "trend_only",
            "trajectory_factors": trajectory_factors,
        }

    return {
        "allowed": False,
        "reason": "FORECAST_BLOCKED",
        "confidence": confidence,
        "allowed_scope": "none",
        "trajectory_factors": trajectory_factors,
    }