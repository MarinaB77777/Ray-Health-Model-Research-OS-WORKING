from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from research.analyses.health_model.model_parameter_registry import (
    MODEL_PARAMETER_REGISTRY_SCHEMA_VERSION,
    SUPPORTED_CALCULATION_STATUSES,
    list_model_parameter_definitions,
    validate_model_parameter_definition,
)


PARAMETER_RECORD_SCHEMA_VERSION = (
    "health-model-parameter-record-2"
)


def _value_at_path(
    data: dict,
    path: str | None,
) -> tuple[bool, Any]:
    if not path:
        return False, None

    current: Any = data

    for part in path.split("."):
        if not isinstance(current, dict):
            return False, None

        if part not in current:
            return False, None

        current = current[part]

    return True, current


def _normalize_calculation_status(
    raw_status: Any,
    *,
    value_found: bool,
    value: Any,
) -> str:
    if raw_status is None:
        if value_found and value is not None:
            return "calculated"

        if value_found and value is None:
            return "not_enough_data"

        return "unknown"

    normalized = str(raw_status).strip().lower()

    status_map = {
        "completed": "calculated",
        "calculated": "calculated",
        "completed_without_manifestation": (
            "calculated"
        ),
        "not_enough_data": "not_enough_data",
        "not enough data": "not_enough_data",
        "not_applicable": "not_applicable",
        "blocked": "blocked",
        "invalid": "invalid",
        "error": "error",
        "unknown": "unknown",
        "orienting": "not_enough_data",
    }

    mapped = status_map.get(normalized)

    if mapped in SUPPORTED_CALCULATION_STATUSES:
        return mapped

    if value_found and value is not None:
        return "calculated"

    return "unknown"


def _runtime_value_type(
    value: Any,
) -> str:
    if value is None:
        return "none"

    if isinstance(value, bool):
        return "bool"

    if isinstance(value, int):
        return "int"

    if isinstance(value, float):
        return "float"

    if isinstance(value, str):
        return "str"

    if isinstance(value, list):
        return "list"

    if isinstance(value, dict):
        return "dict"

    return type(value).__name__


def _numeric_value_is_valid(
    value: Any,
    *,
    minimum: Any,
    maximum: Any,
) -> bool:
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    if minimum is not None and value < minimum:
        return False

    if maximum is not None and value > maximum:
        return False

    return True


def _validate_parameter_value(
    *,
    definition: dict,
    value_found: bool,
    value: Any,
    calculation_status: str,
) -> dict:
    if calculation_status != "calculated":
        return {
            "valid": True,
            "status": (
                "not_validated_without_calculated_value"
            ),
            "errors": [],
        }

    if not value_found or value is None:
        return {
            "valid": False,
            "status": "calculated_value_missing",
            "errors": [
                {
                    "code": (
                        "CALCULATED_PARAMETER_VALUE_MISSING"
                    ),
                }
            ],
        }

    expected_value_type = definition.get(
        "value_type"
    )

    actual_value_type = _runtime_value_type(value)

    value_type_matches = {
        "bool": isinstance(value, bool),
        "int": (
            isinstance(value, int)
            and not isinstance(value, bool)
        ),
        "float": (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        ),
        "str": isinstance(value, str),
        "list": isinstance(value, list),
        "dict": isinstance(value, dict),
    }.get(expected_value_type, False)

    errors = []

    if not value_type_matches:
        errors.append({
            "code": "PARAMETER_VALUE_TYPE_MISMATCH",
            "expected_value_type": expected_value_type,
            "actual_value_type": actual_value_type,
        })

    value_schema = (
        definition.get("value_schema") or {}
    )

    allowed_values = value_schema.get(
        "allowed_values"
    )

    if (
        isinstance(allowed_values, list)
        and value not in allowed_values
    ):
        errors.append({
            "code": (
                "PARAMETER_VALUE_NOT_IN_ALLOWED_VALUES"
            ),
            "allowed_values": allowed_values,
            "actual_value": value,
        })

    ordered_values = value_schema.get(
        "ordered_values"
    )

    if (
        isinstance(ordered_values, list)
        and value not in ordered_values
    ):
        errors.append({
            "code": (
                "PARAMETER_VALUE_NOT_IN_ORDERED_VALUES"
            ),
            "ordered_values": ordered_values,
            "actual_value": value,
        })

    minimum = value_schema.get("minimum")
    maximum = value_schema.get("maximum")

    if (
        minimum is not None
        or maximum is not None
    ):
        if not _numeric_value_is_valid(
            value,
            minimum=minimum,
            maximum=maximum,
        ):
            errors.append({
                "code": (
                    "PARAMETER_VALUE_OUTSIDE_VALID_RANGE"
                ),
                "minimum": minimum,
                "maximum": maximum,
                "actual_value": value,
            })

    components = value_schema.get("components")

    if (
        definition.get("parameter_kind")
        == "vector"
        and isinstance(components, list)
    ):
        if not isinstance(value, (dict, list)):
            errors.append({
                "code": (
                    "VECTOR_PARAMETER_VALUE_INVALID"
                ),
                "actual_value_type": actual_value_type,
            })

    return {
        "valid": not errors,
        "status": (
            "valid"
            if not errors
            else "invalid"
        ),
        "errors": errors,
    }


def _reason_codes_for_record(
    *,
    calculation_status: str,
    value_found: bool,
    value_validation: dict,
) -> list[str]:
    reason_codes = []

    if calculation_status == "not_enough_data":
        reason_codes.append(
            "PARAMETER_NOT_ENOUGH_DATA"
        )

    elif calculation_status == "not_applicable":
        reason_codes.append(
            "PARAMETER_NOT_APPLICABLE"
        )

    elif calculation_status == "blocked":
        reason_codes.append(
            "PARAMETER_CALCULATION_BLOCKED"
        )

    elif calculation_status == "invalid":
        reason_codes.append(
            "PARAMETER_CALCULATION_INVALID"
        )

    elif calculation_status == "error":
        reason_codes.append(
            "PARAMETER_CALCULATION_ERROR"
        )

    elif calculation_status == "unknown":
        reason_codes.append(
            "PARAMETER_CALCULATION_STATUS_UNKNOWN"
        )

    if not value_found:
        reason_codes.append(
            "PARAMETER_VALUE_PATH_NOT_FOUND"
        )

    for error in value_validation.get(
        "errors",
        [],
    ):
        code = error.get("code")

        if code and code not in reason_codes:
            reason_codes.append(code)

    return reason_codes


def build_health_model_parameter_records(
    *,
    session_id: str | None,
    participant_id: str | None,
    subject_link_id: str | None,
    study_id: str,
    analysis_output: dict,
    observation_time: (
        str | datetime | None
    ) = None,
) -> list[dict]:
    if not isinstance(analysis_output, dict):
        raise ValueError(
            "analysis_output must be a dict"
        )

    model_id = analysis_output.get(
        "model_id",
        "health_model_v6_1",
    )

    if isinstance(observation_time, datetime):
        observation_time_value = (
            observation_time.isoformat()
        )
        observation_time_source = (
            "explicit_datetime"
        )

    elif observation_time is not None:
        observation_time_value = str(
            observation_time
        )
        observation_time_source = (
            "explicit_value"
        )

    else:
        observation_time_value = (
            datetime.now(UTC).isoformat()
        )
        observation_time_source = (
            "parameter_record_created_at"
        )

    created_at = datetime.now(UTC).isoformat()

    records = []

    definitions = (
        list_model_parameter_definitions(
            include_inactive=False,
        )
    )

    for definition in definitions:
        definition_validation = (
            validate_model_parameter_definition(
                definition
            )
        )

        if definition_validation["valid"] is not True:
            continue

        calculation = (
            definition.get("calculation") or {}
        )

        definition_model_id = calculation.get(
            "model_id"
        )

        if (
            definition_model_id
            and definition_model_id != model_id
        ):
            continue

        value_path = calculation.get(
            "value_path"
        )

        status_path = calculation.get(
            "status_path"
        )

        value_found, value = _value_at_path(
            analysis_output,
            value_path,
        )

        status_found, raw_status = (
            _value_at_path(
                analysis_output,
                status_path,
            )
            if status_path
            else (False, None)
        )

        calculation_status = (
            _normalize_calculation_status(
                raw_status,
                value_found=value_found,
                value=value,
            )
        )

        value_validation = (
            _validate_parameter_value(
                definition=definition,
                value_found=value_found,
                value=value,
                calculation_status=(
                    calculation_status
                ),
            )
        )

        if value_validation["valid"] is not True:
            calculation_status = "invalid"

        reason_codes = (
            _reason_codes_for_record(
                calculation_status=(
                    calculation_status
                ),
                value_found=value_found,
                value_validation=(
                    value_validation
                ),
            )
        )

        parameter_value = (
            value
            if calculation_status == "calculated"
            else None
        )

        records.append({
            "parameter_record_id": str(
                uuid4()
            ),
            "schema_version": (
                PARAMETER_RECORD_SCHEMA_VERSION
            ),
            "registry_schema_version": (
                MODEL_PARAMETER_REGISTRY_SCHEMA_VERSION
            ),
            "record_type": (
                "calculated_model_parameter"
            ),

            "parameter_id": definition.get(
                "parameter_id"
            ),
            "parameter_code": definition.get(
                "parameter_code"
            ),
            "parameter_definition_version": (
                definition.get(
                    "definition_version"
                )
            ),
            "parameter_definition_source": (
                definition.get(
                    "definition_source"
                )
            ),

            "title": definition.get("title"),
            "parameter_role": definition.get(
                "parameter_role"
            ),
            "parameter_kind": definition.get(
                "parameter_kind"
            ),
            "parameter_value": parameter_value,
            "parameter_value_type": (
                definition.get("value_type")
            ),
            "runtime_value_type": (
                _runtime_value_type(value)
            ),
            "scale_type": definition.get(
                "scale_type"
            ),
            "value_schema": definition.get(
                "value_schema"
            ),
            "score_direction": definition.get(
                "score_direction"
            ),

            "calculation_status": (
                calculation_status
            ),
            "raw_calculation_status": (
                raw_status
                if status_found
                else None
            ),
            "value_path": value_path,
            "status_path": status_path,
            "value_path_found": value_found,
            "status_path_found": status_found,
            "value_validation": (
                value_validation
            ),
            "reason_codes": reason_codes,

            "model_id": model_id,
            "calculator_id": calculation.get(
                "calculator_id"
            ),
            "calculation_version": (
                calculation.get(
                    "calculation_version"
                )
            ),

            "study_id": study_id,
            "session_id": session_id,
            "participant_id": participant_id,
            "subject_link_id": subject_link_id,

            "observation_time": (
                observation_time_value
            ),
            "observation_time_source": (
                observation_time_source
            ),
            "created_at": created_at,

            "research_available": (
                definition.get(
                    "research",
                    {},
                ).get(
                    "available",
                    False,
                )
            ),
            "allowed_analysis_roles": (
                definition.get(
                    "research",
                    {},
                ).get(
                    "allowed_analysis_roles",
                    [],
                )
            ),

            "source_mode": (
                "health_model_v61_registry_extraction"
            ),
        })

    return records