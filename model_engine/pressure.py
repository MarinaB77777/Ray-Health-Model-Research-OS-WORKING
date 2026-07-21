def to_num(value):
    if value is None:
        return None
    return float(value)


def cap(value, min_value=0.0, max_value=5.0):
    if value is None:
        return None
    return max(min_value, min(max_value, value))


def calc_pressure_pair(load_value, resource_value, code, label):
    """
    0 = good / no pressure
    5 = bad / high pressure

    None means not enough data.
    """
    if load_value is None or resource_value is None:
        return {
            "value": None,
            "calculated": False,
            "reason_code": f"{code}_NOT_ENOUGH_DATA",
            "warning": {
                "code": f"{code}_NOT_ENOUGH_DATA",
                "severity": "info",
                "message": f"{label} nonlinear pressure was not calculated because required data is missing.",
            },
        }

    value = (
        (load_value * resource_value / 5)
        * ((load_value + resource_value) / 10)
    )

    return {
        "value": cap(value),
        "calculated": True,
        "reason_code": None,
        "warning": None,
    }


def compute_pressure(answers: dict, loads_data: dict, r_data: dict):
    r_domains = r_data.get("domains", {})

    r_physical = to_num(r_domains.get("physical", {}).get("score"))
    r_psych = to_num(r_domains.get("psych", {}).get("score"))
    r_social = to_num(r_domains.get("social", {}).get("score"))
    r_goals = to_num(r_domains.get("goals", {}).get("score"))
    r_spiritual = to_num(r_domains.get("spiritual", {}).get("score"))

    d1 = to_num(answers.get("d1"))
    d2 = to_num(answers.get("d2"))
    d3 = to_num(answers.get("d3"))

    l_environment = to_num(loads_data.get("l_environment"))
    l_external = to_num(loads_data.get("l_external"))

    p1_data = calc_pressure_pair(d1, r_physical, "P1", "Physical")
    p2_data = calc_pressure_pair(d2, r_psych, "P2", "Psychological")
    p3_data = calc_pressure_pair(d3, r_social, "P3", "Social")
    p4_data = calc_pressure_pair(l_external, r_spiritual, "P4", "External/spiritual")
    p5_data = calc_pressure_pair(l_environment, r_goals, "P5", "Environment/goals")

    pressure_items = {
        "p1_physical": p1_data,
        "p2_psych": p2_data,
        "p3_social": p3_data,
        "p4_external": p4_data,
        "p5_goals": p5_data,
    }

    valid_values = [
        item["value"]
        for item in pressure_items.values()
        if item["calculated"] and item["value"] is not None
    ]

    p_total = cap(sum(valid_values), 0, 5)

    warnings = [
        item["warning"]
        for item in pressure_items.values()
        if item["warning"] is not None
    ]

    reason_codes = [
        item["reason_code"]
        for item in pressure_items.values()
        if item["reason_code"] is not None
    ]

    return {
        "p1_physical": None if p1_data["value"] is None else round(p1_data["value"], 3),
        "p2_psych": None if p2_data["value"] is None else round(p2_data["value"], 3),
        "p3_social": None if p3_data["value"] is None else round(p3_data["value"], 3),
        "p4_external": None if p4_data["value"] is None else round(p4_data["value"], 3),
        "p5_goals": None if p5_data["value"] is None else round(p5_data["value"], 3),
        "p_total": round(p_total, 3),
        "calculated_count": len(valid_values),
        "expected_count": 5,
        "warnings": warnings,
        "reason_codes": reason_codes,
    }