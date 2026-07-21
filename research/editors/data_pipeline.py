from __future__ import annotations

import json
import math
import statistics
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from threading import RLock
from uuid import uuid4

from measurement_graph.time_contract import (
    normalize_measurement_time_reference,
    validate_measurement_time_reference,
)
from research.editors.audit import append_audit_event


PIPELINE_SCHEMA_VERSION = "research-data-transformation-pipeline-1"
OBSERVATION_ENVELOPE_VERSION = "standard-observation-envelope-1"
RECIPE_STORE_PATH = Path("data/data_transformation_recipes.json")
RUN_STORE_PATH = Path("data/data_transformation_runs.json")
SUPPORTED_SOURCE_TYPES = {
    "question_answer",
    "sensor_observation",
    "video_marker",
    "game_event",
    "parameter_measurement",
    "mechanism_state",
}
_LOCK = RLock()


OPERATION_CATALOG = {
    "question_answer": ["missing_tokens", "recode", "reverse_score", "range_check"],
    "sensor_observation": [
        "calibration", "unit_conversion", "range_check", "missing_linear_interpolation",
        "moving_average", "median_filter", "hampel_filter", "center_mean",
        "z_score", "robust_z_score", "min_max_normalize",
    ],
    "video_marker": ["confidence_threshold", "time_offset_seconds", "marker_mapping", "range_check"],
    "game_event": ["event_mapping", "latency_range", "score_min_max", "time_offset_seconds"],
    "parameter_measurement": [
        "definition_binding", "unit_conversion", "range_check", "center_mean",
        "z_score", "robust_z_score", "min_max_normalize",
    ],
    "mechanism_state": ["definition_binding", "state_mapping", "range_check"],
}


def transformation_contract() -> dict:
    return {
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "observation_envelope_version": OBSERVATION_ENVELOPE_VERSION,
        "source_types": sorted(SUPPORTED_SOURCE_TYPES),
        "operation_catalog": deepcopy(OPERATION_CATALOG),
        "ingestion_formats": {
            "direct_observation_tables": ["application/json", "text/csv", "text/tab-separated-values"],
            "container_formats_requiring_source_specific_extraction": [
                "video/x-msvideo", "video/mp4", "video/quicktime", "audio/wav",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ],
            "video_output_contract": "video_marker + measurement-time-contract-1",
            "sensor_output_contract": "sensor_observation + measurement-time-contract-1",
            "raw_binary_is_never_treated_as_text": True,
        },
        "principles": {
            "raw_input_is_immutable": True,
            "preview_precedes_apply": True,
            "every_applied_run_is_audited": True,
            "time_reference": "UTC",
            "source_specific_payloads_are_preserved": True,
            "excluded_records_are_retained_with_reason": True,
        },
    }


def _json_hash(payload: object) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return sha256(serialized.encode("utf-8")).hexdigest()


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def profile_records(*, source_type: str, records: list[dict]) -> dict:
    """Create an observed quality profile; recommendations never alter the input."""
    if source_type not in SUPPORTED_SOURCE_TYPES:
        raise ValueError(f"unsupported source_type: {source_type}")
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ValueError("records must be a list of objects")
    raw_values = [_record_value(record) for record in records]
    numeric = [_number(value) for value in raw_values]
    available = [value for value in numeric if value is not None]
    missing_count = sum(value in (None, "") for value in raw_values)
    non_numeric_count = sum(value not in (None, "") and parsed is None for value, parsed in zip(raw_values, numeric))
    median = statistics.median(available) if available else None
    absolute_deviations = [abs(value - median) for value in available] if median is not None else []
    mad = statistics.median(absolute_deviations) if absolute_deviations else None
    times, invalid_times = [], 0
    for record in records:
        value = record.get("observation_time") or record.get("timestamp") or record.get("created_at")
        if not value:
            continue
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            times.append(parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC))
        except (TypeError, ValueError):
            invalid_times += 1
    intervals = sorted((right - left).total_seconds() for left, right in zip(sorted(times), sorted(times)[1:]))
    interval_median = statistics.median(intervals) if intervals else None
    interval_irregularity = None
    if intervals and interval_median not in (None, 0):
        interval_irregularity = statistics.median(abs(item - interval_median) for item in intervals) / abs(interval_median)
    suggestions = []
    if missing_count and source_type == "sensor_observation":
        suggestions.append({"operation": "missing_linear_interpolation", "reason": "MISSING_SENSOR_VALUES_OBSERVED", "automatic_apply": False, "requires": ["maximum_gap", "regular_time_or_explicit_times"]})
    if source_type == "sensor_observation" and len(available) >= 5:
        suggestions.append({"operation": "median_filter", "reason": "ROBUST_LOCAL_NOISE_REDUCTION_CANDIDATE", "automatic_apply": False, "warning": "MAY_REMOVE_SHORT_REAL_EVENTS"})
        suggestions.append({"operation": "hampel_filter", "reason": "LOCAL_OUTLIER_REVIEW_CANDIDATE", "automatic_apply": False, "warning": "DETECTION_IS_NOT_PROOF_OF_ARTIFACT"})
    if available and len(available) >= 2:
        suggestions.extend([
            {"operation": "z_score", "reason": "COMPARE_RELATIVE_DEVIATIONS_IF_MEAN_SD_ARE_SCIENTIFICALLY_APPROPRIATE", "automatic_apply": False},
            {"operation": "robust_z_score", "reason": "COMPARE_RELATIVE_DEVIATIONS_WITH_OUTLIER_RESISTANCE", "automatic_apply": False},
            {"operation": "min_max_normalize", "reason": "MAP_OBSERVED_RANGE_TO_CONFIGURED_INTERVAL", "automatic_apply": False, "warning": "SENSITIVE_TO_EXTREMES_AND_NEW_FUTURE_VALUES"},
        ])
    return {
        "ok": True,
        "schema_version": "research-data-quality-profile-1",
        "source_type": source_type,
        "input_hash": _json_hash(records),
        "record_count": len(records),
        "missing_count": missing_count,
        "missing_fraction": missing_count / len(records) if records else None,
        "non_numeric_count": non_numeric_count,
        "numeric_summary": {
            "count": len(available), "minimum": min(available) if available else None,
            "q1": _quantile(available, .25), "median": median, "q3": _quantile(available, .75),
            "maximum": max(available) if available else None,
            "mean": statistics.fmean(available) if available else None,
            "sample_standard_deviation": statistics.stdev(available) if len(available) > 1 else None,
            "median_absolute_deviation": mad,
        },
        "time_summary": {
            "valid_time_count": len(times), "invalid_time_count": invalid_times,
            "median_interval_seconds": interval_median,
            "median_relative_interval_deviation": interval_irregularity,
        },
        "recommendations": suggestions,
        "decision_rule": "researcher_selects_after_preview_raw_input_remains_immutable",
    }


def _record_value(record: dict):
    for key in ("value", "answer_value", "measurement_value", "score", "state_value"):
        if key in record:
            return record[key]
    return None


def _operation(operations: list[dict], name: str) -> dict | None:
    for operation in operations:
        if operation.get("type") == name and operation.get("enabled", True):
            return operation
    return None


def _apply_common_time(record: dict, context: dict, operations: list[dict]) -> tuple[dict, list[dict]]:
    time_value = record.get("observation_time") or record.get("timestamp") or record.get("created_at")
    offset = _operation(operations, "time_offset_seconds")
    if offset and time_value:
        text = str(time_value).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=UTC)
            time_value = (parsed.astimezone(UTC) + timedelta(seconds=float(offset.get("seconds", 0)))).isoformat()
        except (TypeError, ValueError):
            pass
    normalized = normalize_measurement_time_reference(
        {
            "observation_time": time_value,
            "synchronization_reference": record.get("synchronization_reference") or context.get("synchronization_reference"),
            "clock_source": record.get("clock_source") or context.get("clock_source"),
            "timezone": record.get("timezone") or context.get("timezone"),
        },
        context=context,
    )
    validation = validate_measurement_time_reference(normalized)
    return normalized, validation.get("errors", []) + validation.get("warnings", [])


def _range_check(value, operation: dict | None, flags: list[dict]):
    if not operation:
        return value
    numeric = _number(value)
    if numeric is None:
        flags.append({"code": "NON_NUMERIC_VALUE", "severity": "error"})
        return value
    minimum, maximum = _number(operation.get("minimum")), _number(operation.get("maximum"))
    if minimum is not None and numeric < minimum:
        flags.append({"code": "VALUE_BELOW_RANGE", "severity": "warning", "minimum": minimum})
    if maximum is not None and numeric > maximum:
        flags.append({"code": "VALUE_ABOVE_RANGE", "severity": "warning", "maximum": maximum})
    return numeric


def _transform_question(value, operations, flags):
    missing = _operation(operations, "missing_tokens")
    if missing and str(value) in {str(item) for item in missing.get("tokens", [])}:
        flags.append({"code": "MISSING_VALUE_TOKEN", "severity": "info"})
        value = None
    recode = _operation(operations, "recode")
    if recode and value is not None:
        mapping = recode.get("mapping") or {}
        if str(value) in mapping:
            value = mapping[str(value)]
        elif recode.get("require_match"):
            flags.append({"code": "RECODE_MAPPING_MISSING", "severity": "error"})
    reverse = _operation(operations, "reverse_score")
    if reverse and value is not None:
        numeric, minimum, maximum = _number(value), _number(reverse.get("minimum")), _number(reverse.get("maximum"))
        if None in (numeric, minimum, maximum):
            flags.append({"code": "REVERSE_SCORE_INPUT_INVALID", "severity": "error"})
        else:
            value = minimum + maximum - numeric
    return _range_check(value, _operation(operations, "range_check"), flags)


def _transform_sensor(value, operations, flags):
    numeric = _number(value)
    if numeric is None:
        flags.append({"code": "SENSOR_VALUE_NOT_NUMERIC", "severity": "error"})
        return value
    calibration = _operation(operations, "calibration")
    if calibration:
        numeric = numeric * float(calibration.get("gain", 1)) + float(calibration.get("offset", 0))
    conversion = _operation(operations, "unit_conversion")
    if conversion:
        numeric = numeric * float(conversion.get("factor", 1)) + float(conversion.get("offset", 0))
    return _range_check(numeric, _operation(operations, "range_check"), flags)


def _transform_video(record, value, operations, flags):
    confidence_op = _operation(operations, "confidence_threshold")
    if confidence_op:
        confidence = _number(record.get("confidence"))
        threshold = _number(confidence_op.get("minimum"))
        if confidence is None:
            flags.append({"code": "CONFIDENCE_MISSING", "severity": "error"})
        elif threshold is not None and confidence < threshold:
            flags.append({"code": "LOW_CONFIDENCE", "severity": "exclusion", "minimum": threshold})
    marker = _operation(operations, "marker_mapping")
    if marker:
        record["marker_code"] = (marker.get("mapping") or {}).get(str(record.get("marker_code")), record.get("marker_code"))
    return _range_check(value, _operation(operations, "range_check"), flags)


def _transform_game(record, value, operations, flags):
    mapping = _operation(operations, "event_mapping")
    if mapping:
        record["event_type"] = (mapping.get("mapping") or {}).get(str(record.get("event_type")), record.get("event_type"))
    latency = _operation(operations, "latency_range")
    if latency:
        _range_check(record.get("latency_ms"), {"minimum": latency.get("minimum"), "maximum": latency.get("maximum")}, flags)
    normalizer = _operation(operations, "score_min_max")
    if normalizer and value is not None:
        numeric, minimum, maximum = _number(value), _number(normalizer.get("minimum")), _number(normalizer.get("maximum"))
        if None in (numeric, minimum, maximum) or maximum == minimum:
            flags.append({"code": "SCORE_NORMALIZATION_INVALID", "severity": "error"})
        else:
            value = (numeric - minimum) / (maximum - minimum)
    return value


def _apply_sequence_filters(values: list, operations: list[dict], flags_by_index: list[list[dict]]) -> list:
    result = list(values)
    interpolation = _operation(operations, "missing_linear_interpolation")
    if interpolation:
        maximum_gap = max(1, int(interpolation.get("maximum_gap", 1)))
        index = 0
        while index < len(result):
            if _number(result[index]) is not None:
                index += 1
                continue
            start = index
            while index < len(result) and _number(result[index]) is None:
                index += 1
            gap = index - start
            left = _number(result[start - 1]) if start > 0 else None
            right = _number(result[index]) if index < len(result) else None
            if gap <= maximum_gap and left is not None and right is not None:
                for offset in range(gap):
                    result[start + offset] = left + (right - left) * ((offset + 1) / (gap + 1))
                    flags_by_index[start + offset].append({"code": "LINEAR_INTERPOLATION_APPLIED", "severity": "info", "gap_length": gap})
            else:
                for position in range(start, index):
                    flags_by_index[position].append({"code": "MISSING_VALUE_NOT_INTERPOLATED", "severity": "error", "gap_length": gap})
    for operation_name, reducer in (("moving_average", statistics.fmean), ("median_filter", statistics.median)):
        operation = _operation(operations, operation_name)
        if not operation:
            continue
        window = max(1, int(operation.get("window", 3)))
        if window % 2 == 0:
            window += 1
        radius = window // 2
        source = list(result)
        for index in range(len(source)):
            candidates = [_number(source[position]) for position in range(max(0, index-radius), min(len(source), index+radius+1))]
            candidates = [item for item in candidates if item is not None]
            if candidates:
                result[index] = reducer(candidates)
                flags_by_index[index].append({"code": operation_name.upper() + "_APPLIED", "severity": "info", "window": window})
    hampel = _operation(operations, "hampel_filter")
    if hampel:
        window = max(3, int(hampel.get("window", 5)))
        if window % 2 == 0:
            window += 1
        threshold = float(hampel.get("threshold", 3.0))
        replace = bool(hampel.get("replace", False))
        source, radius = list(result), window // 2
        for index, value in enumerate(source):
            numeric = _number(value)
            local = [_number(source[p]) for p in range(max(0, index-radius), min(len(source), index+radius+1))]
            local = [item for item in local if item is not None]
            if numeric is None or len(local) < 3:
                continue
            center = statistics.median(local)
            mad = statistics.median(abs(item - center) for item in local)
            if mad > 0 and abs(numeric - center) > threshold * 1.4826 * mad:
                flags_by_index[index].append({"code": "HAMPEL_OUTLIER_FLAG", "severity": "warning", "window": window, "threshold": threshold, "replaced": replace})
                if replace:
                    result[index] = center
    available = [_number(value) for value in result]
    usable = [value for value in available if value is not None]
    normalizers = [name for name in ("center_mean", "z_score", "robust_z_score", "min_max_normalize") if _operation(operations, name)]
    if len(normalizers) > 1:
        raise ValueError("only one sequence normalization may be selected")
    if normalizers and usable:
        name = normalizers[0]
        if name == "center_mean":
            center, denominator, target_min = statistics.fmean(usable), 1.0, 0.0
        elif name == "z_score":
            center, denominator, target_min = statistics.fmean(usable), statistics.stdev(usable) if len(usable) > 1 else 0.0, 0.0
        elif name == "robust_z_score":
            center = statistics.median(usable)
            denominator = 1.4826 * statistics.median(abs(value - center) for value in usable)
            target_min = 0.0
        else:
            operation = _operation(operations, name) or {}
            source_min, source_max = min(usable), max(usable)
            target_min, target_max = float(operation.get("target_minimum", 0)), float(operation.get("target_maximum", 1))
            center, denominator = source_min, source_max - source_min
        if denominator == 0:
            raise ValueError(f"{name} undefined because the reference spread is zero")
        for index, numeric in enumerate(available):
            if numeric is None:
                continue
            normalized = (numeric - center) / denominator
            if name == "min_max_normalize":
                normalized = target_min + normalized * (target_max - target_min)
            result[index] = normalized
            flags_by_index[index].append({"code": name.upper() + "_APPLIED", "severity": "info", "reference_center": center, "reference_spread": denominator})
    return result


def transform_records(
    *,
    source_type: str,
    records: list[dict],
    operations: list[dict],
    context: dict,
) -> dict:
    if source_type not in SUPPORTED_SOURCE_TYPES:
        raise ValueError(f"unsupported source_type: {source_type}")
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ValueError("records must be a list of objects")
    allowed = set(OPERATION_CATALOG[source_type])
    unknown = sorted({str(item.get("type")) for item in operations if item.get("type") not in allowed})
    if unknown:
        raise ValueError(f"unsupported operations for {source_type}: {', '.join(unknown)}")
    transformed_values, flags_by_index, working_records = [], [], []
    for raw in records:
        record, flags = deepcopy(raw), []
        value = _record_value(record)
        if source_type == "question_answer":
            value = _transform_question(value, operations, flags)
        elif source_type == "sensor_observation":
            value = _transform_sensor(value, operations, flags)
        elif source_type == "video_marker":
            value = _transform_video(record, value, operations, flags)
        elif source_type == "game_event":
            value = _transform_game(record, value, operations, flags)
        elif source_type in {"parameter_measurement", "mechanism_state"}:
            binding = _operation(operations, "definition_binding")
            if binding:
                record["definition_reference"] = deepcopy(binding.get("definition_reference") or {})
            state_mapping = _operation(operations, "state_mapping")
            if state_mapping:
                value = (state_mapping.get("mapping") or {}).get(str(value), value)
            conversion = _operation(operations, "unit_conversion")
            if conversion and value is not None:
                numeric = _number(value)
                if numeric is None:
                    flags.append({"code": "UNIT_CONVERSION_NON_NUMERIC", "severity": "error"})
                else:
                    value = numeric * float(conversion.get("factor", 1)) + float(conversion.get("offset", 0))
            value = _range_check(value, _operation(operations, "range_check"), flags)
        transformed_values.append(value)
        flags_by_index.append(flags)
        working_records.append(record)
    if source_type in {"sensor_observation", "parameter_measurement"}:
        transformed_values = _apply_sequence_filters(transformed_values, operations, flags_by_index)
    outputs = []
    for index, (raw, record, value, flags) in enumerate(zip(records, working_records, transformed_values, flags_by_index)):
        time_reference, time_flags = _apply_common_time(record, context, operations)
        flags.extend(time_flags)
        status = "excluded" if any(item.get("severity") in {"error", "exclusion"} for item in flags) else "usable"
        payload = deepcopy(record)
        for key in ("observation_time", "timestamp", "created_at", "value", "answer_value", "measurement_value", "score", "state_value"):
            payload.pop(key, None)
        outputs.append({
            "schema_version": OBSERVATION_ENVELOPE_VERSION,
            "record_id": str(uuid4()),
            "source_type": source_type,
            "source_record_id": raw.get("record_id") or raw.get("answer_record_id") or raw.get("event_id") or f"input-{index+1}",
            "source_record_hash": _json_hash(raw),
            "study_id": record.get("study_id") or context.get("study_id"),
            "subject_link_id": record.get("subject_link_id") or context.get("subject_link_id"),
            "session_id": record.get("session_id") or context.get("session_id"),
            "definition_reference": record.get("definition_reference") or context.get("definition_reference") or {},
            "scale_reference": record.get("scale_reference") or context.get("scale_reference"),
            "unit": record.get("unit") or context.get("unit"),
            "value": value,
            "time_reference": time_reference,
            "quality_status": status,
            "quality_flags": flags,
            "payload": payload,
        })
    return {
        "ok": True,
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "source_type": source_type,
        "input_hash": _json_hash(records),
        "operation_hash": _json_hash(operations),
        "input_count": len(records),
        "usable_count": sum(item["quality_status"] == "usable" for item in outputs),
        "excluded_count": sum(item["quality_status"] == "excluded" for item in outputs),
        "records": outputs,
    }


def _read_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8") or "[]")
    return value if isinstance(value, list) else []


def _append_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        values = _read_list(path)
        values.append(value)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)


def apply_transformation(
    *, source_type: str, records: list[dict], operations: list[dict], context: dict,
    actor_id: str, reason: str, recipe_name: str,
) -> dict:
    preview = transform_records(source_type=source_type, records=records, operations=operations, context=context)
    now = datetime.now(UTC).isoformat()
    recipe = {
        "schema_version": "data-transformation-recipe-1",
        "recipe_id": str(uuid4()), "recipe_name": recipe_name,
        "source_type": source_type, "operations": deepcopy(operations),
        "context_contract": deepcopy(context), "created_at": now,
        "created_by": actor_id, "reason": reason, "status": "active",
    }
    run = {
        "schema_version": "data-transformation-run-1", "run_id": str(uuid4()),
        "recipe_id": recipe["recipe_id"], "applied_at": now, "applied_by": actor_id,
        "reason": reason, "input_hash": preview["input_hash"],
        "output_hash": _json_hash(preview["records"]), "result": preview,
    }
    _append_json(RECIPE_STORE_PATH, recipe)
    _append_json(RUN_STORE_PATH, run)
    audit = append_audit_event(
        action="data_transformation_applied", actor_id=actor_id,
        object_type="data_transformation_run", object_id=run["run_id"], reason=reason,
        details={"recipe_id": recipe["recipe_id"], "source_type": source_type, "input_count": preview["input_count"]},
    )
    return {"ok": True, "recipe": recipe, "run": run, "audit_event": audit}


def list_recipes(source_type: str | None = None) -> list[dict]:
    recipes = _read_list(RECIPE_STORE_PATH)
    return [item for item in recipes if not source_type or item.get("source_type") == source_type]
