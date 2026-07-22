import math

from research.analyses.health_model.constellation_registry import (
    list_constellations,
)

CONSTELLATION_LAYER_SCHEMA_VERSION = "constellation-layer-1"


def _clip_0_5(value):
    if value is None:
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    return max(0, min(5, numeric))


def _mechanism_score(mechanisms: dict, mechanism_id: str):
    item = mechanisms.get(mechanism_id)

    if not isinstance(item, dict):
        return None

    return item.get("score")


def _is_active_score(score, threshold: float) -> bool:
    score = _clip_0_5(score)

    if score is None:
        return False

    return score >= threshold


def _constellation_strength(
    mechanisms: dict,
    required_mechanisms: list[str],
):
    scores = [
        _clip_0_5(_mechanism_score(mechanisms, mechanism_id))
        for mechanism_id in required_mechanisms
    ]

    scores = [score for score in scores if score is not None]

    if not scores:
        return None

    return round(sum(scores) / len(scores), 3)


def build_constellation_layer(mechanism_layer: dict) -> dict:
    mechanisms = mechanism_layer.get("mechanisms", {})

    if not isinstance(mechanisms, dict):
        mechanisms = {}

    constellations = {}
    active_constellations = {}
    suspected_constellations = {}
    not_supported_constellations = {}
    blocked_constellations_due_to_missing_data = {}

    for constellation in list_constellations():
        constellation_id = constellation["id"]
        required_mechanisms = constellation.get("required_mechanisms", [])
        threshold = constellation.get("threshold", 2.5)

        matched_required = []
        missing_required = []
        below_threshold_required = []

        for mechanism_id in required_mechanisms:
            score = _mechanism_score(mechanisms, mechanism_id)

            if score is None:
                missing_required.append(mechanism_id)
                continue

            if _is_active_score(score, threshold):
                matched_required.append(mechanism_id)
            else:
                below_threshold_required.append({
                    "mechanism_id": mechanism_id,
                    "score": score,
                    "threshold": threshold,
                })

        strength = _constellation_strength(
            mechanisms=mechanisms,
            required_mechanisms=required_mechanisms,
        )

        if missing_required:
            status = "NOT_ENOUGH_DATA"
        elif below_threshold_required:
            status = "NOT_SUPPORTED"
        else:
            status = "ACTIVE"

        item = {
            "id": constellation_id,
            "title": constellation.get("title"),
            "type": constellation.get("type"),
            "status": status,
            "strength": strength,
            "threshold": threshold,
            "priority": constellation.get("priority"),
            "configuration_adjustment": (
                constellation.get("configuration_adjustment")
                if status == "ACTIVE"
                else None
            ),
            "matched_required_mechanisms": matched_required,
            "missing_required_mechanisms": missing_required,
            "below_threshold_required_mechanisms": below_threshold_required,
            "optional_amplifiers": constellation.get("optional_amplifiers", []),
            "protective_signals": constellation.get("protective_signals", []),
            "interpretation": constellation.get("interpretation"),
            "likely_trajectory": constellation.get("likely_trajectory"),
            "user_facing_explanation": (
                constellation.get("user_facing_explanation")
            ),
            "first_safe_action": constellation.get("first_safe_action"),
            "protective_factors": constellation.get("protective_factors", []),
            "forecast_targets": constellation.get("forecast_targets", []),
            "do_not_say": constellation.get("do_not_say", []),
            "raw_answers_included": False,
            "questions_included": False,
            "scores_exposed_to_participant": False,
        }

        constellations[constellation_id] = item

        if status == "ACTIVE":
            active_constellations[constellation_id] = item
        elif status == "SUSPECTED":
            suspected_constellations[constellation_id] = item
        elif status == "NOT_SUPPORTED":
            not_supported_constellations[constellation_id] = item
        else:
            blocked_constellations_due_to_missing_data[constellation_id] = item

    configuration_adjustments = [
        item.get("configuration_adjustment")
        for item in active_constellations.values()
        if item.get("configuration_adjustment") is not None
    ]

    configuration_adjustment = (
        max(configuration_adjustments)
        if configuration_adjustments
        else None
    )

    dominant_constellation = None

    if active_constellations:
        dominant_constellation = max(
            active_constellations.values(),
            key=lambda item: (
                item.get("strength") or 0,
                item.get("configuration_adjustment") or 0,
            ),
        )

    return {
        "schema_version": CONSTELLATION_LAYER_SCHEMA_VERSION,
        "constellation_count": len(constellations),
        "active_count": len(active_constellations),
        "suspected_count": len(suspected_constellations),
        "not_supported_count": len(not_supported_constellations),
        "blocked_count": len(blocked_constellations_due_to_missing_data),
        "constellations": constellations,
        "active_constellations": active_constellations,
        "suspected_constellations": suspected_constellations,
        "not_supported_constellations": not_supported_constellations,
        "blocked_constellations_due_to_missing_data": (
            blocked_constellations_due_to_missing_data
        ),
        "dominant_constellation": dominant_constellation,
        "secondary_constellations": [
            item for item in active_constellations.values()
            if dominant_constellation is None
            or item["id"] != dominant_constellation["id"]
        ],
        "configuration_adjustment": configuration_adjustment,
        "raw_answers_included": False,
        "questions_included": False,
        "scores_exposed_to_participant": False,
    }
