from model_engine.forecast_tables import RESOURCE_FORECAST_TABLE

DOMAIN_CODE_TO_KEY = {
    "T": "physical",
    "M": "psych",
    "G": "goals",
    "C": "social",
    "F": "finance",
}


def get_resource_table_row(domain_code: str, score):
    if score is None:
        return None

    domain_key = DOMAIN_CODE_TO_KEY.get(domain_code)
    if domain_key is None:
        return None

    domain_table = RESOURCE_FORECAST_TABLE.get(domain_key)
    if not domain_table:
        return None

    level = int(round(score))
    level = max(0, min(5, level))

    row = domain_table.get(level)
    if row and row.get("alias_of") is not None:
        row = domain_table.get(row["alias_of"])

    return row


def build_table_based_item(
    mechanism: str,
    domain_code: str,
    score,
    severity: str = "caution",
):
    row = get_resource_table_row(domain_code, score)

    if row is None:
        return None

    return {
        "mechanism": mechanism,
        "domain": domain_code,
        "severity": severity,
        "level_range": row.get("level_range"),
        "resource_state": row.get("resource_state"),
        "vulnerable_functions": row.get("vulnerable_functions"),
        "preserved_functions": row.get("preserved_functions"),
        "functional_consequences": row.get("functional_consequences"),
        "decision_forecast": row.get("decision_forecast"),
    }

def build_forecast_narratives(engine_result: dict) -> list:
    forecast = engine_result.get("forecast", {})
    r_data = engine_result.get("r", {})

    factors = forecast.get("trajectory_factors", [])
    narratives = []

    domains = r_data.get("domains", {})

    resource_levels = {
        "T": domains.get("physical", {}).get("score"),
        "M": domains.get("psych", {}).get("score"),
        "G": domains.get("goals", {}).get("score"),
        "C": domains.get("social", {}).get("score"),
        "F": domains.get("finance", {}).get("score"),
        "P": domains.get("spiritual", {}).get("score"),
    }

    for factor in factors:
        code = factor.get("code")

        if code == "OPTION_SPACE_COLLAPSE":
            narratives.extend(
                build_option_space_narratives(resource_levels)
            )

        if code == "HOPELESSNESS_SIGNAL":
            narratives.extend(
                build_hopelessness_narratives(resource_levels)
            )

        if code == "NEGATIVE_SPIRAL":
            narratives.extend(
                build_negative_spiral_narratives(resource_levels)
            )

    return narratives


def build_option_space_narratives(resource_levels: dict) -> list:
    items = []

    linked_domains = ["G", "C", "F", "M"]

    for domain_code in linked_domains:
        score = resource_levels.get(domain_code)

        if score is None:
            continue

        if score < 3:
            continue

        item = build_table_based_item(
            mechanism="OPTION_SPACE_COLLAPSE",
            domain_code=domain_code,
            score=score,
        )

        if item:
            items.append(item)

    return items


def build_hopelessness_narratives(resource_levels: dict) -> list:
    items = []

    linked_domains = ["G", "M"]

    for domain_code in linked_domains:
        score = resource_levels.get(domain_code)

        if score is None:
            continue

        if score < 3:
            continue

        item = build_table_based_item(
            mechanism="HOPELESSNESS_SIGNAL",
            domain_code=domain_code,
            score=score,
        )

        if item:
            items.append(item)

    return items

def build_negative_spiral_narratives(resource_levels: dict) -> list:
    items = []

    linked_domains = ["T", "M", "C", "G", "F"]

    for domain_code in linked_domains:
        score = resource_levels.get(domain_code)

        if score is None:
            continue

        if score < 3:
            continue

        item = build_table_based_item(
            mechanism="NEGATIVE_SPIRAL",
            domain_code=domain_code,
            score=score,
        )

        if item:
            items.append(item)

    return items