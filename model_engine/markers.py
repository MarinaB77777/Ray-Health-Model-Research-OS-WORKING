MARKER_DOMAINS = {
    "physical": ["k3", "k7"],
    "psych": ["k8", "k10", "k11", "k12", "k13"],
    "goals": ["k14", "k15"],
    "social": ["k16", "k17", "k18"],
    "spiritual": ["k21", "k22"],
}


def valid_values(answers: dict, fields: list):
    values = []

    for field in fields:
        value = answers.get(field)

        if value is None:
            continue

        values.append(float(value))

    return values


def mean(values: list):
    if not values:
        return None

    return sum(values) / len(values)


def cap_0_5(value):
    if value is None:
        return None

    return max(0, min(5, value))


def compute_k_self(answers: dict):
    domains = {}

    for domain, fields in MARKER_DOMAINS.items():
        values = valid_values(answers, fields)
        score = mean(values)

        domains[domain] = {
            "score": cap_0_5(score),
            "valid_count": len(values),
            "required_count": len(fields),
            "coverage": round(len(values) / len(fields), 3),
        }

    valid_domain_scores = [
        data["score"]
        for data in domains.values()
        if data["score"] is not None
    ]

    k_self_total_0_5 = mean(valid_domain_scores)

    if k_self_total_0_5 is None:
        k_self_norm = None
    else:
        k_self_norm = (k_self_total_0_5 / 5) * 10

    return {
        "domains": domains,
        "k_self_total_0_5": cap_0_5(k_self_total_0_5),
        "k_self_norm": None if k_self_norm is None else round(k_self_norm, 3),
    }