def check_minimum_total_sample_size(
    *,
    values: list,
    minimum_required: int = 3,
) -> dict:
    non_missing = [
        value
        for value in values
        if value is not None and value != ""
    ]

    count = len(non_missing)

    return {
        "check_id": "minimum_total_sample_size",
        "status": "passed" if count >= minimum_required else "failed",
        "details": {
            "non_missing_count": count,
            "minimum_required": minimum_required,
        },
    }