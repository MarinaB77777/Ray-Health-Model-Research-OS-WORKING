from collections import Counter


def check_source_consistency(
    *,
    answer_records: list[dict],
) -> dict:
    sources = []

    for record in answer_records:
        source = (
            record.get("record_source")
            or record.get("source_type")
            or record.get("data_source")
            or record.get("record_type")
        )

        if source:
            sources.append(source)

    counts = Counter(sources)

    if not answer_records:
        status = "blocked"
    elif not sources:
        status = "warning"
    elif len(counts) == 1:
        status = "passed"
    else:
        status = "warning"

    return {
        "check_id": "source_consistency",
        "status": status,
        "details": {
            "source_counts": dict(counts),
            "note": "Warning means multiple or missing data sources; analysis may still be valid, but source handling should be explicit.",
        },
    }