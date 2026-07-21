from research.analyses.health_model.function_registry import get_function

FUNCTION_LAYER_SCHEMA_VERSION = "function-layer-2"


def _clip_0_5(value):
    if value is None:
        return None
    return max(0, min(5, float(value)))


def _function_strength(source_scores: list[dict]) -> float | None:
    values = [
        _clip_0_5(item.get("score"))
        for item in source_scores
        if item.get("score") is not None
    ]
    values = [v for v in values if v is not None]

    if not values:
        return None

    return round(max(values), 3)


def extract_functions_from_level_maps(level_maps: dict) -> dict:
    records = level_maps.get("records", [])

    extracted_functions = {}
    unresolved_functions = []

    for record in records:
        interpretations = record.get("interpretations", {})

        if not isinstance(interpretations, dict):
            continue

        for domain, item in interpretations.items():
            interpretation = item.get("interpretation", {})
            level_key = item.get("level_key")
            score = item.get("score")

            vulnerable_functions = interpretation.get(
                "vulnerable_functions",
                [],
            )

            for function_id in vulnerable_functions:
                if function_id.startswith("no_significant_"):
                    continue

                function = get_function(function_id)

                if function is None:
                    unresolved_functions.append({
                        "function_id": function_id,
                        "domain": domain,
                        "level_key": level_key,
                        "score": score,
                        "reason": "FUNCTION_NOT_IN_REGISTRY",
                    })
                    continue

                if function_id not in extracted_functions:
                    extracted_functions[function_id] = {
                        **function,
                        "source_domains": [],
                        "source_levels": [],
                        "source_scores": [],
                        "strength": None,
                        "strength_method": "max_source_score_0_5",
                    }

                if domain not in extracted_functions[function_id]["source_domains"]:
                    extracted_functions[function_id]["source_domains"].append(domain)

                extracted_functions[function_id]["source_levels"].append({
                    "domain": domain,
                    "level_key": level_key,
                })

                extracted_functions[function_id]["source_scores"].append({
                    "domain": domain,
                    "score": score,
                })

                extracted_functions[function_id]["strength"] = _function_strength(
                    extracted_functions[function_id]["source_scores"]
                )

    return {
        "schema_version": FUNCTION_LAYER_SCHEMA_VERSION,
        "function_count": len(extracted_functions),
        "functions": extracted_functions,
        "unresolved_functions": unresolved_functions,
        "unresolved_count": len(unresolved_functions),
        "raw_answers_included": False,
        "questions_included": False,
        "scores_exposed_to_participant": False,
    }