def check_scale_defined(
    *,
    left_scale: str | None,
    right_scale: str | None,
) -> dict:
    missing = []

    if not left_scale:
        missing.append("left")

    if not right_scale:
        missing.append("right")

    status = "passed" if not missing else "failed"

    return {
        "check_id": "scale_defined",
        "status": status,
        "details": {
            "left_scale": left_scale,
            "right_scale": right_scale,
            "missing_sides": missing,
        },
    }