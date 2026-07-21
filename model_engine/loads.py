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


def compute_domain_loads(answers: dict):
    domain_specs = {
        "physical": ["d1", "d11"],
        "psych": ["d2", "d3", "d9", "d10", "e8"],
        "goals": ["d7", "d8", "d13", "d0", "e8"],
        "social": ["d3", "e1", "e6"],
        "finance": ["e8", "d5a"],
        "spiritual": ["e2", "e4"],
    }

    result = {}

    for domain, fields in domain_specs.items():
        values = valid_values(answers, fields)
        score = cap_0_5(mean(values))

        result[domain] = {
            "score": score,
            "valid_count": len(values),
            "required_count": len(fields),
            "coverage": round(len(values) / len(fields), 3),
            "fields": fields,
        }

    return result


def compute_loads(answers: dict):
    environment_values = valid_values(
        answers,
        ["d7", "d8", "d9", "d10", "d11", "d12", "d13"],
    )

    requirements_values = valid_values(
        answers,
        ["d4b", "d5a", "d6b"],
    )

    external_values = valid_values(
        answers,
        ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8"],
    )

    l_environment = mean(environment_values)
    l_requirements = mean(requirements_values)

    if external_values:
        l_external = 0.7 * mean(external_values) + 0.3 * max(external_values)
    else:
        l_external = None

    return {
        "l_environment": cap_0_5(l_environment),
        "l_requirements": cap_0_5(l_requirements),
        "l_external": cap_0_5(l_external),
        "l_additional": None,
        "domain_loads": compute_domain_loads(answers),
    }