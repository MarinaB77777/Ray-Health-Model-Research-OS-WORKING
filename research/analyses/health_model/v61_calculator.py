import math


NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"


def _num(answers: dict, code: str):
    value = answers.get(code)

    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mean(values: list[float]):
    valid = [
        value for value in values
        if value is not None
    ]

    if not valid:
        return None

    return sum(valid) / len(valid)


def _rms(values: list[float]):
    valid = [
        value for value in values
        if value is not None
    ]

    if not valid:
        return None

    return math.sqrt(
        sum(value * value for value in valid) / len(valid)
    )


def _cap(value, low: float, high: float):
    if value is None:
        return None

    return max(low, min(high, value))


def calculate_health_model_v61(
    answers: dict,
) -> dict:
    load = calculate_load_blocks(answers)
    resources = calculate_resource_deficit(answers)
    load_failure = calculate_load_failure_risk(
        load=load,
        resources=resources,
        answers=answers,
    )
    multipliers = calculate_multipliers(
        load=load,
        resources=resources,
        answers=answers,
    )
    manifestation = calculate_manifestation_layer(answers)

    stress = calculate_stress_burden(
        load=load,
        resources=resources,
        load_failure=load_failure,
        multipliers=multipliers,
        manifestation=manifestation,
        answers=answers,
    )

    modeled_burden = calculate_modeled_burden(
        load=load,
        resources=resources,
    )

    current_state = calculate_current_state(
        modeled_burden=modeled_burden,
        manifestation=manifestation,
    )

    critical = calculate_critical_status(answers)

    if critical["is_critical"]:
        current_state["current_state_final"] = 5
        stress["stress_burden_final"] = 10

    return {
        "model_id": "health_model_v6_1",
        "status": "completed",
        "load_blocks": load,
        "resource_deficit_domains": resources,
        "load_failure_risk": load_failure,
        "multipliers": multipliers,
        "manifestation_layer": manifestation,
        "stress_burden": stress,
        "modeled_burden": modeled_burden,
        "current_state": current_state,
        "critical_status": critical,
        "state_risk": {
            "status": NOT_ENOUGH_DATA,
            "reason": "Repeated comparable measurements are required for StateRisk.",
        },
        "trajectory_risk": {
            "status": NOT_ENOUGH_DATA,
            "reason": "Trajectory mechanisms are not implemented for participant-level calculation yet.",
        },
        "forecast_allowed": False,
        "readiness_status": "ORIENTING",
    }


def calculate_load_blocks(answers: dict) -> dict:
    d11_max = max(
        value for value in [
            _num(answers, "d11a"),
            _num(answers, "d11b"),
            _num(answers, "d11c"),
            _num(answers, "d11d"),
        ]
        if value is not None
    ) if any(
        _num(answers, code) is not None
        for code in ["d11a", "d11b", "d11c", "d11d"]
    ) else None

    l_environment_base = _mean([
        _num(answers, "d7"),
        _num(answers, "d8"),
        _num(answers, "d9"),
        _num(answers, "d10"),
        d11_max,
        _num(answers, "d12"),
        _num(answers, "d13"),
    ])

    b8 = _num(answers, "b8")

    l_environment = None
    if l_environment_base is not None:
        l_environment = l_environment_base + (
            b8 / 4 if b8 is not None else 0
        )

    l_requirements = _mean([
        _num(answers, "d4b"),
        _num(answers, "d5a"),
        _num(answers, "d6b"),
    ])

    external_values = calculate_external_pressure_values(answers)

    l_external = None
    if external_values:
        b9 = _num(answers, "b9")
        l_external = min(5, sum(external_values)) + (
            b9 / 4 if b9 is not None else 0
        )

    d14 = _num(answers, "d14")
    d15 = _num(answers, "d15")
    l_environment_additional = _num(
        answers,
        "l_environment_additional",
    )

    if (
        l_environment_additional is not None
        and d14 is not None
        and d15 is not None
    ):
        l_additional = (
            l_environment_additional
            * (d14 / 40)
            * (1 + d15 / 3)
        )
    else:
        l_additional = 0

    l_total = _mean([
        l_environment,
        l_requirements,
        l_external,
        l_additional,
    ])

    return {
        "l_environment": l_environment,
        "l_requirements": l_requirements,
        "l_external": l_external,
        "l_additional": l_additional,
        "l_total": l_total,
    }


def calculate_external_pressure_values(answers: dict) -> list[float]:
    values = []

    e1b = _num(answers, "e1b")
    e1c = _num(answers, "e1c")
    e1d = _num(answers, "e1d")
    if None not in [e1b, e1c, e1d]:
        values.append((e1b * e1c * e1d) / 8)

    e2b = _num(answers, "e2b")
    e2c = _num(answers, "e2c")
    if None not in [e2b, e2c]:
        values.append(e2c * (1 + (4 - e2b) * (4 - e2c) / 16))

    e3b = _num(answers, "e3b")
    e3c = _num(answers, "e3c")
    if None not in [e3b, e3c]:
        values.append((e3b * e3c) / 4)

    e4b = _num(answers, "e4b")
    e4c = _num(answers, "e4c")
    if None not in [e4b, e4c]:
        values.append((e4b * e4c) / 4)

    for code in ["e5", "e6"]:
        value = _num(answers, code)
        if value is not None:
            values.append(value)

    e7b = _num(answers, "e7b")
    e7c = _num(answers, "e7c")
    if None not in [e7b, e7c]:
        values.append((e7c * (3 - e7b)) / 3)

    return [
        value for value in values
        if value != 0
    ]


def calculate_resource_deficit(answers: dict) -> dict:
    r_phys_base = _mean([
        _num(answers, "t1"),
        _num(answers, "t2"),
        _num(answers, "t3"),
        _num(answers, "t4"),
    ])

    b3 = _num(answers, "b3")
    b4 = _num(answers, "b4")

    r_phys = None
    if r_phys_base is not None:
        r_phys = min(
            5,
            r_phys_base
            + (b3 / 5 if b3 is not None else 0)
            + (b4 / 3 if b4 is not None else 0),
        )

    r_psych = _mean([
        _num(answers, "m1"),
        _num(answers, "m2"),
        _num(answers, "m3"),
        _num(answers, "m4"),
    ])

    r_goal = _mean([
        _num(answers, "g1"),
        _num(answers, "g2"),
        _num(answers, "g3"),
    ])

    c1 = _num(answers, "c1")
    c2 = _num(answers, "c2")
    c3 = _num(answers, "c3")

    r_social = None
    if None not in [c1, c2, c3]:
        r_social = (c1 + c2 * 5 / 3 + c3) / 3

    r_fin = _mean([
        _num(answers, "f1"),
        _num(answers, "f2"),
        _num(answers, "f3"),
        _num(answers, "f4"),
    ])

    r_spiritual = _mean([
        _num(answers, "p1"),
        _num(answers, "p2"),
        _num(answers, "p3"),
    ])

    domains = {
        "r_phys": r_phys,
        "r_psych": r_psych,
        "r_goal": r_goal,
        "r_social": r_social,
        "r_fin": r_fin,
        "r_spiritual": r_spiritual,
    }

    corrected = apply_coping_x_correction(
        answers=answers,
        domains=domains,
    )

    corrected["resource_deficit_global"] = _mean(
        list(corrected.values())
    )

    return corrected

def apply_coping_x_correction(
    *,
    answers: dict,
    domains: dict,
) -> dict:
    corrected = dict(domains)

    coping_rules = {
        "x1": {
            "r_phys": 1.0,
            "r_psych": 0.7,
            "r_fin": 0.5,
        },
        "x2": {
            "r_phys": 1.0,
        },
        "x3": {
            "r_psych": 0.5,
            "r_goal": 0.5,
        },
        "x4": {
            "r_phys": 1.0,
            "r_social": 1.0,
        },
    }

    for coping_code, affected_domains in coping_rules.items():
        active = _num(answers, coping_code)
        x5 = _num(answers, f"{coping_code}_x5")
        x6 = _num(answers, f"{coping_code}_x6")
        x7 = _num(answers, f"{coping_code}_x7")

        if active is None or active < 1:
            continue

        if x5 is None or x5 < 2 or x6 is None:
            continue

        if x7 == 2:
            b = 1.5
        elif x7 == 1:
            b = 1.0
        elif x7 == 0:
            b = 0.5
        else:
            b = 1.0

        k_x = (x5 + x6) / 10 * b

        for domain, weight in affected_domains.items():
            if corrected.get(domain) is None:
                continue

            corrected[domain] = min(
                5,
                corrected[domain] + k_x * weight,
            )

    return corrected


def calculate_load_failure_risk(
    *,
    load: dict,
    resources: dict,
    answers: dict,
) -> dict:
    d1_mean = _mean([
        _num(answers, "d1a"),
        _num(answers, "d1b"),
        _num(answers, "d1c"),
    ])

    d2_mean = _mean([
        _num(answers, "d2a"),
        _num(answers, "d2b"),
        _num(answers, "d2c"),
    ])

    d3_mean = _mean([
        _num(answers, "d3a"),
        _num(answers, "d3b"),
        _num(answers, "d3c"),
    ])

    r_phys = resources.get("r_phys")
    r_psych = resources.get("r_psych")
    r_social = resources.get("r_social")
    r_spiritual = resources.get("r_spiritual")
    r_goal = resources.get("r_goal")

    l_external = load.get("l_external")
    l_environment = load.get("l_environment")

    p1 = (
        d1_mean * r_phys / 5
        if d1_mean is not None and r_phys is not None
        and d1_mean >= 3 and r_phys >= 3
        else 0
    )

    p2 = (
        d2_mean * r_psych / 5
        if d2_mean is not None and r_psych is not None
        and d2_mean >= 3 and r_psych >= 3
        else 0
    )

    p3 = (
        d3_mean * r_social / 5
        if d3_mean is not None and r_social is not None
        and d3_mean >= 3 and r_social >= 3
        else 0
    )

    p4 = (
        l_external * r_spiritual / 5
        if l_external is not None and r_spiritual is not None
        and l_external >= 3 and r_spiritual >= 3
        else 0
    )

    p5 = (
        l_environment * r_goal / 5
        if l_environment is not None and r_goal is not None
        and l_environment >= 3 and r_goal >= 3
        else 0
    )

    return {
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "p4": p4,
        "p5": p5,
        "p_total": p1 + p2 + p3 + p4 + p5,
    }


def calculate_multipliers(
    *,
    load: dict,
    resources: dict,
    answers: dict,
) -> dict:
    b12 = _num(answers, "b12")
    d5a = _num(answers, "d5a")

    if b12 is not None and d5a is not None:
        m_o = 1 + (b12 * d5a) / 25
    else:
        m_o = 1.0

    b11_affected = _num(answers, "b11_affected")
    m_b = 1.5 if b11_affected == 1 else 1.0

    b13 = _num(answers, "b13")
    m_d = 1 + b13 / 5 if b13 is not None else 1.0

    resource_domains_high = sum(
        1 for value in [
            resources.get("r_phys"),
            resources.get("r_psych"),
            resources.get("r_goal"),
            resources.get("r_social"),
            resources.get("r_fin"),
            resources.get("r_spiritual"),
        ]
        if value is not None and value >= 3
    )

    if resource_domains_high <= 1:
        m_k = 1.0
    elif resource_domains_high == 2:
        m_k = 1.3
    elif resource_domains_high == 3:
        m_k = 1.7
    elif resource_domains_high == 4:
        m_k = 2.2
    elif resource_domains_high == 5:
        m_k = 2.8
    else:
        m_k = 3.5

    v_level = answers.get("v_level") or answers.get("V")

    if v_level == "V3":
        v = 1.5
    elif v_level == "V2":
        v = 1.3
    else:
        v = 1.0

    return {
        "m_o": m_o,
        "m_b": m_b,
        "m_d": m_d,
        "m_k": m_k,
        "v": v,
        "v_level": v_level or "V1",
    }


def calculate_manifestation_layer(answers: dict) -> dict:
    values = [
        _num(answers, f"k{i}")
        for i in range(1, 23)
    ]

    k_fact = _mean(values)

    if k_fact is None:
        return {
            "manifestation_score": None,
            "manifestation_score_norm": None,
            "status": NOT_ENOUGH_DATA,
        }

    return {
        "manifestation_score": k_fact,
        "manifestation_score_norm": k_fact / 5 * 10,
        "status": "completed",
    }


def calculate_stress_burden(
    *,
    load: dict,
    resources: dict,
    load_failure: dict,
    multipliers: dict,
    manifestation: dict,
    answers: dict,
) -> dict:
    l = load.get("l_total")
    r = resources.get("resource_deficit_global")
    p = load_failure.get("p_total")

    if l is None or r is None or p is None:
        return {
            "status": NOT_ENOUGH_DATA,
            "stress_burden_raw": None,
            "stress_burden_norm": None,
            "stress_burden_final": None,
        }

    raw = (
        (l + r + p)
        * multipliers["m_o"]
        * multipliers["m_b"]
        * multipliers["m_d"]
        * multipliers["m_k"]
    )

    norm = 10 * math.log10(1 + raw) / math.log10(700)
    final = min(10, multipliers["v"] * norm)

    k23 = _num(answers, "k23")
    k24 = _num(answers, "k24")

    critical_override = (
        (k23 is not None and k23 >= 3)
        or (k24 is not None and k24 >= 2)
    )

    if critical_override:
        final = 10

    return {
        "status": "completed",
        "stress_burden_raw": raw,
        "stress_burden_norm": norm,
        "stress_burden_final": final,
        "critical_override_applied": critical_override,
    }


def calculate_modeled_burden(
    *,
    load: dict,
    resources: dict,
) -> dict:
    pressure_proxy = _rms([
        load.get("l_environment"),
        load.get("l_requirements"),
        load.get("l_external"),
        load.get("l_additional"),
    ])

    resource_deficit = resources.get("resource_deficit_global")

    modeled = _rms([
        pressure_proxy,
        resource_deficit,
    ])

    return {
        "pressure_proxy": pressure_proxy,
        "resource_deficit": resource_deficit,
        "modeled_burden": modeled,
    }


def calculate_current_state(
    *,
    modeled_burden: dict,
    manifestation: dict,
) -> dict:
    modeled = modeled_burden.get("modeled_burden")
    k = manifestation.get("manifestation_score")

    if modeled is None:
        return {
            "status": NOT_ENOUGH_DATA,
            "current_state_final": None,
            "burden_manifestation_delta": None,
        }

    if k is None:
        return {
            "status": "completed_without_manifestation",
            "current_state_final": modeled,
            "burden_manifestation_delta": NOT_ENOUGH_DATA,
        }

    current = (modeled + k) / 2
    delta = modeled - k

    if delta > 1.5:
        mode = "PREVENTIVE_WINDOW"
    elif delta < -1.5:
        mode = "HIDDEN_FACTOR_MODE"
    else:
        mode = "DIAGNOSTIC_MODE"

    return {
        "status": "completed",
        "current_state_final": current,
        "burden_manifestation_delta": delta,
        "mode": mode,
    }


def calculate_critical_status(answers: dict) -> dict:
    k23 = _num(answers, "k23")
    k24 = _num(answers, "k24")

    is_critical = (
        (k23 is not None and k23 >= 3)
        or (k24 is not None and k24 >= 2)
    )

    return {
        "is_critical": is_critical,
        "k23": k23,
        "k24": k24,
    }