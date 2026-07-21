from research.analyses.health_model.resource_level_maps import (
    get_resource_level_interpretation,
)


SUPPORTED_LEVEL_MAP_DOMAINS = [
    "physical",
    "psychological",
    "goal",
    "social",
    "cognitive",
    "recovery",
    "pep",
]


def extract_domain_scores_from_record(record: dict) -> dict:
    result = record.get("result", {})
    prepared = record.get("prepared_domain_output", {})

    prepared_payload = prepared.get("prepared_payload", {})

    prepared_scores = prepared_payload.get("domain_scores")

    if isinstance(prepared_scores, dict):
        return prepared_scores
    
    if not isinstance(result, dict):
        return {}

    domain_scores = result.get("domain_scores")

    if isinstance(domain_scores, dict):
        return domain_scores

    scores = result.get("scores")

    if isinstance(scores, dict):
        return scores

    r_data = result.get("r")

    if isinstance(r_data, dict):
        domains = r_data.get("domains")

        if isinstance(domains, dict):
            mapped = {
                "physical": domains.get("physical", {}).get("score"),
                "psychological": domains.get("psych", {}).get("score"),
                "goal": domains.get("goals", {}).get("score"),
                "social": domains.get("social", {}).get("score"),
                "financial": domains.get("finance", {}).get("score"),
                "spiritual": domains.get("spiritual", {}).get("score"),
            }

            return {
                key: value
                for key, value in mapped.items()
                if value is not None
            }

    return {}


def analyze_record_level_maps(record: dict) -> dict:
    domain_scores = extract_domain_scores_from_record(record)

    interpretations = {}
    missing_domains = []

    for domain in SUPPORTED_LEVEL_MAP_DOMAINS:
        score = domain_scores.get(domain)

        if score is None:
            missing_domains.append(domain)
            continue

        interpretation = get_resource_level_interpretation(
            domain=domain,
            score=score,
        )

        if interpretation is None:
            missing_domains.append(domain)
            continue

        interpretations[domain] = interpretation

    return {
        "analysis_type": "resource_level_map_analysis",
        "record_id": record.get("record_id"),
        "session_id": record.get("session_id"),
        "study_id": record.get("study_id"),
        "available_domain_scores": list(domain_scores.keys()),
        "interpreted_domains": list(interpretations.keys()),
        "missing_domains": missing_domains,
        "interpretations": interpretations,
    }


def analyze_level_maps(records: list[dict]) -> dict:
    record_results = [
        analyze_record_level_maps(record)
        for record in records
    ]

    interpreted_record_count = sum(
        1 for item in record_results
        if item["interpreted_domains"]
    )

    return {
        "analysis_type": "resource_level_maps_batch",
        "record_count": len(records),
        "interpreted_record_count": interpreted_record_count,
        "supported_domains": SUPPORTED_LEVEL_MAP_DOMAINS,
        "records": record_results,
    }