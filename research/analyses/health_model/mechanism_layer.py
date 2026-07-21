from research.analyses.health_model.mechanism_registry import list_mechanisms

MECHANISM_LAYER_SCHEMA_VERSION = "mechanism-layer-2"


def _clip_0_5(value):
    if value is None:
        return None
    return max(0, min(5, float(value)))


def _mean(values):
    clean = [_clip_0_5(v) for v in values if v is not None]
    clean = [v for v in clean if v is not None]

    if not clean:
        return None

    return round(sum(clean) / len(clean), 3)


def _status_for_score(score, threshold: float = 2.5) -> str:
    if score is None:
        return "NOT_ENOUGH_DATA"

    if score >= threshold:
        return "LIKELY"

    if score > 0:
        return "SUSPECTED"

    return "NOT_ENOUGH_DATA"


def _function_strength(functions: dict, function_id: str):
    function = functions.get(function_id)

    if not isinstance(function, dict):
        return None

    return function.get("strength")


def _mechanism_score(
    functions: dict,
    required_functions: list[str],
    supporting_functions: list[str],
    minimum_required: int,
):
    required_scores = [
        _function_strength(functions, function_id)
        for function_id in required_functions
    ]

    required_scores = [
        score for score in required_scores
        if score is not None
    ]

    supporting_scores = [
        _function_strength(functions, function_id)
        for function_id in supporting_functions
    ]

    supporting_scores = [
        score for score in supporting_scores
        if score is not None
    ]

    if minimum_required <= 0:
        return None

    if len(required_scores) < minimum_required:
        if not required_scores:
            return None

        return round(_mean(required_scores) * 0.6, 3)

    base_score = _mean(required_scores)

    if base_score is None:
        return None

    if supporting_scores:
        support_score = _mean(supporting_scores)
        return round(
            min(5, base_score + 0.2 * support_score),
            3,
        )

    return base_score


def build_mechanism_layer(function_layer: dict) -> dict:
    functions = function_layer.get("functions", {})

    if not isinstance(functions, dict):
        functions = {}

    available_function_ids = set(functions.keys())
    mechanisms = {}

    for mechanism in list_mechanisms():
        mechanism_id = mechanism["id"]

        required_functions = mechanism.get("required_functions", [])
        supporting_functions = mechanism.get("supporting_functions", [])
        minimum_required = mechanism.get("minimum_required", 0)

        matched_required = [
            function_id for function_id in required_functions
            if function_id in available_function_ids
        ]

        matched_supporting = [
            function_id for function_id in supporting_functions
            if function_id in available_function_ids
        ]

        missing_required = [
            function_id for function_id in required_functions
            if function_id not in available_function_ids
        ]

        score = _mechanism_score(
            functions=functions,
            required_functions=required_functions,
            supporting_functions=supporting_functions,
            minimum_required=minimum_required,
        )

        status = _status_for_score(score)

        mechanisms[mechanism_id] = {
            "id": mechanism_id,
            "title": mechanism.get("title"),
            "type": mechanism.get("type"),
            "status": status,
            "score": score,
            "score_method": (
                "mean_required_strength_plus_0_2_supporting_strength"
            ),
            "matched_required_functions": matched_required,
            "matched_supporting_functions": matched_supporting,
            "missing_required_functions": missing_required,
            "matched_required_count": len(matched_required),
            "matched_supporting_count": len(matched_supporting),
            "minimum_required": minimum_required,
            "first_measurement_allowed_statuses": (
                mechanism.get("first_measurement_allowed_statuses", [])
            ),
            "confirmed_requires_repeated_measurement": (
                mechanism.get("confirmed_requires_repeated_measurement", True)
            ),
            "trajectory_contributes_to": (
                mechanism.get("trajectory_contributes_to", [])
            ),
        }

    active_mechanisms = {
        mechanism_id: item
        for mechanism_id, item in mechanisms.items()
        if item["status"] in {"SUSPECTED", "LIKELY"}
    }

    likely_mechanisms = {
        mechanism_id: item
        for mechanism_id, item in mechanisms.items()
        if item["status"] == "LIKELY"
    }

    suspected_mechanisms = {
        mechanism_id: item
        for mechanism_id, item in mechanisms.items()
        if item["status"] == "SUSPECTED"
    }

    return {
        "schema_version": MECHANISM_LAYER_SCHEMA_VERSION,
        "mechanism_count": len(mechanisms),
        "active_count": len(active_mechanisms),
        "likely_count": len(likely_mechanisms),
        "suspected_count": len(suspected_mechanisms),
        "mechanisms": mechanisms,
        "active_mechanisms": active_mechanisms,
        "likely_mechanisms": likely_mechanisms,
        "suspected_mechanisms": suspected_mechanisms,
        "raw_answers_included": False,
        "questions_included": False,
        "scores_exposed_to_participant": False,
    }