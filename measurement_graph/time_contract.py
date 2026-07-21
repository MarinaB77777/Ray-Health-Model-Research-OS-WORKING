from copy import deepcopy
from datetime import UTC, datetime

from assessment.measurement.scale_registry import build_scale_reference


MEASUREMENT_TIME_CONTRACT_VERSION = "measurement-time-contract-1"
GLOBAL_TIME_SCALE_CODE = "datetime"


def _parse_datetime(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        text = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def normalize_measurement_time_reference(
    time_reference: dict | None,
    *,
    context: dict | None = None,
) -> dict:
    """Bind a measurement to the shared UTC datetime scale without inventing time."""
    normalized = deepcopy(time_reference) if isinstance(time_reference, dict) else {}
    context = context or {}

    candidates = (
        (normalized.get("observation_time"), "explicit_observation_time"),
        (normalized.get("finished_at"), "finished_at_fallback"),
        (normalized.get("started_at"), "started_at_fallback"),
    )
    observation_time = None
    observation_time_source = None
    for value, source in candidates:
        parsed = _parse_datetime(value)
        if parsed is not None:
            observation_time = parsed.isoformat()
            observation_time_source = source
            break

    source_global_reference = (
        normalized.get("global_time_reference")
        or context.get("global_time_reference")
    )
    parsed_global_anchor = _parse_datetime(source_global_reference)
    if parsed_global_anchor is not None:
        normalized.setdefault(
            "global_time_anchor",
            parsed_global_anchor.isoformat(),
        )
        normalized["global_time_reference_source"] = (
            "legacy_timestamp_migrated_to_global_time_anchor"
        )
    elif source_global_reference not in (None, "", "UTC"):
        normalized["unrecognized_global_time_reference"] = (
            source_global_reference
        )

    normalized["observation_time"] = observation_time
    normalized["observation_time_source"] = observation_time_source
    normalized["global_time_reference"] = (
        "UTC" if observation_time else None
    )
    normalized["timezone"] = (
        normalized.get("timezone")
        or context.get("timezone")
        or ("UTC" if observation_time else None)
    )
    normalized["synchronization_reference"] = (
        normalized.get("synchronization_reference")
        or context.get("synchronization_reference")
    )
    normalized["clock_source"] = (
        normalized.get("clock_source")
        or context.get("clock_source")
    )
    normalized["contract_version"] = MEASUREMENT_TIME_CONTRACT_VERSION
    normalized["global_time_scale"] = {
        "scale_type": GLOBAL_TIME_SCALE_CODE,
        "scale_reference": build_scale_reference(GLOBAL_TIME_SCALE_CODE),
        "axis": "UTC",
    }
    if not isinstance(normalized.get("time_scale"), dict):
        normalized["time_scale"] = {
            "scale_type": None,
            "scale_reference": None,
            "binding_status": "unbound",
        }
    return normalized


def validate_measurement_time_reference(time_reference: dict) -> dict:
    errors = []
    warnings = []
    if not time_reference.get("observation_time"):
        errors.append({"field": "observation_time", "code": "OBSERVATION_TIME_REQUIRED"})
    if time_reference.get("global_time_reference") != "UTC":
        errors.append({"field": "global_time_reference", "code": "GLOBAL_UTC_REFERENCE_REQUIRED"})
    if time_reference.get("unrecognized_global_time_reference"):
        errors.append({
            "field": "unrecognized_global_time_reference",
            "code": "GLOBAL_TIME_REFERENCE_UNRECOGNIZED",
            "value": time_reference.get("unrecognized_global_time_reference"),
        })
    if (time_reference.get("global_time_scale") or {}).get("scale_type") != GLOBAL_TIME_SCALE_CODE:
        errors.append({"field": "global_time_scale.scale_type", "code": "GLOBAL_TIME_SCALE_MUST_BE_DATETIME"})
    if not time_reference.get("synchronization_reference"):
        warnings.append({"field": "synchronization_reference", "code": "CLOCK_SYNCHRONIZATION_UNVERIFIED"})
    if not time_reference.get("clock_source"):
        warnings.append({"field": "clock_source", "code": "CLOCK_SOURCE_UNRECORDED"})
    status = "unbound" if errors else ("bound_with_unverified_clock" if warnings else "bound")
    return {"valid": not errors, "status": status, "errors": errors, "warnings": warnings}
