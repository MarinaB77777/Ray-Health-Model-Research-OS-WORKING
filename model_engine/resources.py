RESOURCE_DOMAINS = {
    "physical": ["t1", "t2", "t3", "t4"],
    "psych": ["m1", "m2", "m3", "m4"],
    "goals": ["g1", "g2", "g3"],
    "social": ["c1", "c2", "c3"],
    "finance": ["f1", "f2", "f3", "f4"],
    "spiritual": ["p1", "p2", "p3"],
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


def compute_r(answers: dict):
    domains = {}

    for domain, fields in RESOURCE_DOMAINS.items():
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

    r_total = mean(valid_domain_scores)

    return {
        "domains": domains,
        "r_total": cap_0_5(r_total),
    }