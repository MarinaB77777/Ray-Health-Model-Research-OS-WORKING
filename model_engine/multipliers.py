def safe_num(value, default=0.0):
    if value is None:
        return default
    return float(value)


def cap(value, min_value=0.0, max_value=5.0):
    return max(min_value, min(max_value, value))


def compute_domain_pressure(loads_data: dict, r_data: dict):
    r_domains = r_data.get("domains", {})
    domain_loads = loads_data.get("domain_loads", {})

    pressures = {}

    for domain, load_item in domain_loads.items():
        l_score = load_item.get("score")

        r_score = r_domains.get(domain, {}).get("score")

        if l_score is None or r_score is None:
            pressures[domain] = None
            continue

        pressure = (l_score + r_score) / 2
        pressures[domain] = cap(pressure)

    return pressures

def compute_multipliers(answers: dict, r_data: dict, loads_data: dict):
    b12 = safe_num(answers.get("b12"))
    d5a = safe_num(answers.get("d5a"))

    # price of error
    m_error = 1 + (b12 * d5a) / 25

    # pain point optional, not active in MVP
    m_pain = 1.0

    # duration
    b13 = safe_num(answers.get("b13"))
    m_duration = 1 + b13 / 5

    # resource deficit cascade
    r_domains = r_data.get("domains", {})
    n_deficit = 0

    for item in r_domains.values():
        score = item.get("score")
        if score is not None and score >= 3:
            n_deficit += 1

    m_cascade = min(3.5, 1 + (n_deficit ** 1.3) / 5)

    # multiple pressure domains
    domain_pressure = compute_domain_pressure(
        loads_data=loads_data,
        r_data=r_data,
    )

    n_pressure = 0
    for value in domain_pressure.values():
        if value is not None and value >= 3:
            n_pressure += 1

    m_pressure = min(2.2, 1 + (n_pressure ** 1.25) / 8)

    m_total = m_error * m_pain * m_duration * m_cascade * m_pressure
    m_total = min(5.0, m_total)

    return {
        "m_error": round(m_error, 3),
        "m_pain": round(m_pain, 3),
        "m_duration": round(m_duration, 3),
        "m_cascade": round(m_cascade, 3),
        "m_pressure": round(m_pressure, 3),
        "m_total": round(m_total, 3),
        "n_deficit": n_deficit,
        "n_pressure": n_pressure,
        "domain_pressure": domain_pressure,
    }