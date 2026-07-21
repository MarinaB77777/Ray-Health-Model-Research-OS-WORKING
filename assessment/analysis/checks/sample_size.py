def check_minimum_paired_sample_size(
    *,
    paired_count: int,
    minimum_required: int = 3,
) -> dict:
    return {
        "check_id": "minimum_paired_sample_size",
        "status": "passed" if paired_count >= minimum_required else "failed",
        "details": {
            "paired_count": paired_count,
            "minimum_required": minimum_required,
        },
    }