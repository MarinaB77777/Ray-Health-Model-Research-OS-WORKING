from collections import Counter


def check_observed_groups(
    *,
    values: list,
    side: str,
) -> dict:
    groups = Counter(values)

    return {
        "check_id": f"observed_{side}_groups",
        "status": "info",
        "details": {
            "group_count": len(groups),
            "groups": dict(groups),
        },
    }