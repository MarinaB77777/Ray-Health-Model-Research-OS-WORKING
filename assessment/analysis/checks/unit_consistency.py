from collections import Counter


def check_unit_consistency(
    *,
    records: list[dict],
    expected_unit: str | None = None,
) -> dict:
    units = []

    for record in records:
        unit = (
            record.get("unit")
            or record.get("measurement_unit")
            or record.get("value_unit")
        )

        if unit:
            units.append(unit)

    counts = Counter(units)

    if not records:
        status = "blocked"
    elif not units:
        status = "warning"
    elif expected_unit and any(unit != expected_unit for unit in units):
        status = "failed"
    elif len(counts) == 1:
        status = "passed"
    else:
        status = "warning"

    return {
        "check_id": "unit_consistency",
        "status": status,
        "details": {
            "expected_unit": expected_unit,
            "unit_counts": dict(counts),
            "note": "Warning means units are missing or mixed; conversion or explicit unit handling may be required.",
        },
    }