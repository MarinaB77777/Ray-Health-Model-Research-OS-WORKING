def determine_initial_state(coverage_data: dict, q_data: dict, answers: dict):
    reason_codes = []
    warnings = []

    k23 = answers.get("k23")
    k24 = answers.get("k24")

    if k23 is not None and k23 >= 3:
        reason_codes.append("CRITICAL_K23")
        warnings.append({
            "severity": "critical",
            "message": "Critical response detected: k23",
        })
        return {
            "state": "CRITICAL",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    if k24 is not None and k24 >= 2:
        reason_codes.append("CRITICAL_K24")
        warnings.append({
            "severity": "critical",
            "message": "Critical response detected: k24",
        })
        return {
            "state": "CRITICAL",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    coverage = coverage_data.get("coverage", 0)
    q_global = q_data.get("q_global", 999)

    if coverage < 0.4:
        reason_codes.append("LOW_COVERAGE")
        return {
            "state": "SAFE_DATA_REQUEST",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    if 0.4 <= coverage < 0.6:
        reason_codes.append("ORIENTING_LOW_COVERAGE")
        return {
            "state": "ORIENTING",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    if q_global > 1.5:
        reason_codes.append("LOW_QUALITY")
        return {
            "state": "LOW_QUALITY",
            "reason_codes": reason_codes,
            "warnings": warnings,
        }

    return {
        "state": "ORIENTING",
        "reason_codes": reason_codes,
        "warnings": warnings,
    }


def count_calculated_delta_domains(delta_data: dict):
    count = 0

    if not delta_data:
        return count

    for item in delta_data.values():
        if item.get("calculated"):
            count += 1

    return count

def determine_final_state(
    initial_state: str,
    s_data: dict,
    k_self_data: dict,
    consistency_data: dict,
    coverage_data: dict,
    q_data: dict,
    r_data: dict = None,
    pressure_data: dict = None,
    delta_data: dict = None,
):
    if initial_state == "CRITICAL":
        return {
            "state": "CRITICAL",
            "reason_codes": ["CRITICAL_OVERRIDE"],
        }

    if initial_state == "SAFE_DATA_REQUEST":
        return {
            "state": "SAFE_DATA_REQUEST",
            "reason_codes": ["SAFE_DATA_REQUEST_OVERRIDE"],
        }

    coverage = coverage_data.get("coverage", 0)
    q_global = q_data.get("q_global", 999)

    if coverage < 0.6:
        return {
            "state": "ORIENTING",
            "reason_codes": ["ORIENTING_LOW_COVERAGE"],
        }

    if q_global > 1.5:
        return {
            "state": "LOW_QUALITY",
            "reason_codes": ["LOW_QUALITY_OVERRIDE"],
        }

    s_norm = s_data.get("s_norm")
    k_self_norm = k_self_data.get("k_self_norm")
    c_final = consistency_data.get("c_final", 0)

    if s_norm is None or k_self_norm is None:
        return {
            "state": "ORIENTING",
            "reason_codes": ["STATE_NOT_ENOUGH_DATA"],
        }

    if c_final > 4:
        return {
            "state": "CONSISTENCY_FAILURE",
            "reason_codes": ["CONSISTENCY_FAILURE"],
        }

    readiness_reasons = []

    if r_data is None or r_data.get("r_total") is None:
        readiness_reasons.append("R_NOT_ENOUGH_DATA")

    if pressure_data is None or pressure_data.get("calculated_count", 0) == 0:
        readiness_reasons.append("PRESSURE_NOT_ENOUGH_DATA")

    
    calculated_delta_domains = count_calculated_delta_domains(delta_data)

    if calculated_delta_domains < 3:
        readiness_reasons.append("DELTA_NOT_ENOUGH_DATA")
   

    if readiness_reasons:
        return {
            "state": "ORIENTING",
            "reason_codes": ["STATE_READINESS_NOT_ENOUGH_DATA"] + readiness_reasons,
        }

    delta_total = s_norm - k_self_norm

    if abs(delta_total) <= 1.5:
        return {
            "state": "DIAGNOSTIC",
            "reason_codes": ["STATE_DIAGNOSTIC"],
        }

    if (
        s_norm > k_self_norm + 1.5
        and coverage >= 0.6
        and q_global <= 1.5
        and c_final <= 4
    ):
        return {
            "state": "FORECAST",
            "reason_codes": ["STATE_FORECAST"],
        }

    if (
        k_self_norm > s_norm + 1.5
        and coverage >= 0.6
        and q_global <= 1.5
        and c_final <= 4
    ):
        return {
            "state": "HIDDEN_FACTOR",
            "reason_codes": ["STATE_HIDDEN_FACTOR"],
        }

    return {
        "state": "ORIENTING",
        "reason_codes": ["STATE_ORIENTING"],
    }