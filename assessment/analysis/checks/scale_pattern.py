from assessment.measurement.scale_registry import (
    scale_matches_requirement,
)


def scale_matches(
    method: dict,
    left_scale: str | None,
    right_scale: str | None,
) -> bool:
    if not left_scale or not right_scale:
        return False

    for pattern in method.get("scale_patterns", []):
        if (
            any(
                scale_matches_requirement(left_scale, requirement)
                for requirement in pattern.get("left", [])
            )
            and any(
                scale_matches_requirement(right_scale, requirement)
                for requirement in pattern.get("right", [])
            )
        ):
            return True

    return False


def check_scale_pattern_supported(
    *,
    method: dict,
    left_scale: str | None,
    right_scale: str | None,
) -> dict:
    if not left_scale or not right_scale:
        return {
            "check_id": "scale_pattern_supported",
            "status": "blocked",
            "details": {
                "left_scale": left_scale,
                "right_scale": right_scale,
                "reason": "scale_type is missing",
            },
        }

    return {
        "check_id": "scale_pattern_supported",
        "status": (
            "passed"
            if scale_matches(method, left_scale, right_scale)
            else "failed"
        ),
        "details": {
            "left_scale": left_scale,
            "right_scale": right_scale,
        },
    }
