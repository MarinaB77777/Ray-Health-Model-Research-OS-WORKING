import math


def to_num(value):
    if value is None:
        return None
    return float(value)


def cap(value, min_value=0.0, max_value=10.0):
    if value is None:
        return None

    return max(min_value, min(max_value, value))


def valid_sum(values):
    valid = [v for v in values if v is not None]

    if not valid:
        return None

    return sum(valid)


def compute_s(
    loads_data: dict,
    r_data: dict,
    pressure_data: dict = None,
    multipliers_data: dict = None,
):
    l_environment = to_num(loads_data.get("l_environment"))
    l_requirements = to_num(loads_data.get("l_requirements"))
    l_external = to_num(loads_data.get("l_external"))
    l_additional = to_num(loads_data.get("l_additional"))

    r_total = to_num(r_data.get("r_total"))

    if pressure_data is None:
        p_total = None
    else:
        p_total = to_num(pressure_data.get("p_total"))

    if multipliers_data is None:
        m_total = 1.0
    else:
        m_total = to_num(multipliers_data.get("m_total"))

    if m_total is None:
        m_total = 1.0

    base_sum = valid_sum([
        l_environment,
        l_requirements,
        l_external,
        l_additional,
        r_total,
        p_total,
    ])

    if base_sum is None:
        return {
            "calculated": False,
            "reason_code": "S_NOT_ENOUGH_DATA",
            "s_raw": None,
            "s_norm": None,
            "s_final": None,
            "p_total": p_total,
            "m_total": round(m_total, 3),
        }

    s_raw = base_sum * m_total

    s_norm = math.log10(s_raw + 1) / math.log10(700) * 10

    s_final = cap(s_norm, 0, 10)

    return {
        "calculated": True,
        "reason_code": None,
        "s_raw": round(s_raw, 3),
        "s_norm": round(s_norm, 3),
        "s_final": round(s_final, 3),
        "p_total": p_total,
        "m_total": round(m_total, 3),
    }