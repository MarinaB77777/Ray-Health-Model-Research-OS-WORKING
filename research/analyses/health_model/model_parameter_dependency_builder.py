from itertools import combinations
from typing import Any

from assessment.analysis.analysis_method_registry import (
    EXECUTABLE_METHOD_IDS,
    METHODS,
)
from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
    scale_matches_requirement,
)
from research.analyses.health_model.model_parameter_catalog import (
    collect_health_model_parameter_records,
)


MODEL_PARAMETER_DEPENDENCY_SCHEMA_VERSION = (
    "health-model-parameter-dependency-catalog-1"
)


def _scale_pattern_matches(
    method: dict,
    left_scale: str | None,
    right_scale: str | None,
) -> bool:
    if left_scale is None or right_scale is None:
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


def _single_or_mixed(
    values: set,
) -> str | None:
    clean = {
        value
        for value in values
        if value is not None and value != ""
    }

    if not clean:
        return None

    if len(clean) == 1:
        return next(iter(clean))

    return "mixed"


def _build_variable_catalog(
    parameter_records: list[dict],
) -> dict[str, dict]:
    grouped = {}

    for record in parameter_records:
        parameter_code = record.get("parameter_code")

        if not parameter_code:
            continue

        grouped.setdefault(
            parameter_code,
            {
                "parameter_code": parameter_code,
                "scale_types": set(),
                "value_types": set(),
                "session_ids": set(),
                "record_count": 0,
            },
        )

        group = grouped[parameter_code]

        group["record_count"] += 1
        group["scale_types"].add(
            record.get("scale_type")
        )
        group["value_types"].add(
            record.get("parameter_value_type")
        )

        session_id = record.get("session_id")

        if session_id:
            group["session_ids"].add(session_id)

    variables = {}

    for parameter_code, group in grouped.items():
        scale_type = _single_or_mixed(
            group["scale_types"]
        )
        scale_definition = get_scale_definition(
            scale_type
        )
        variables[parameter_code] = {
            "variable_source": (
                "calculated_model_parameter"
            ),
            "variable_code": parameter_code,
            "parameter_code": parameter_code,
            "title": parameter_code,
            "scale_type": scale_type,
            "scale_binding_status": (
                "registered"
                if scale_definition is not None
                else "unbound"
            ),
            "standard_analysis_compatibility": (
                "scale_compatible_methods_may_be_selected"
                if scale_definition is not None
                else "not_assumed_until_scale_or_method_contract_is_explicit"
            ),
            "scale_reference": (
                build_scale_reference(scale_type)
                if scale_definition is not None
                else None
            ),
            "measurement_level": (
                scale_definition.get("measurement_level")
                if scale_definition is not None
                else None
            ),
            "value_structure": (
                scale_definition.get("value_structure")
                if scale_definition is not None
                else None
            ),
            "numeric_nature": (
                scale_definition.get("numeric_nature")
                if scale_definition is not None
                else None
            ),
            "parameter_value_type": _single_or_mixed(
                group["value_types"]
            ),
            "available_records_count": group[
                "record_count"
            ],
            "available_session_count": len(
                group["session_ids"]
            ),
        }

    return variables


def _paired_session_count(
    parameter_records: list[dict],
    left_parameter_code: str,
    right_parameter_code: str,
) -> int:
    left_runs = {
        record.get("calculation_run_id")
        for record in parameter_records
        if (
            record.get("parameter_code")
            == left_parameter_code
            and record.get(
                "calculation_status"
            ) == "calculated"
            and record.get(
                "calculation_run_id"
            )
        )
    }

    right_runs = {
        record.get("calculation_run_id")
        for record in parameter_records
        if (
            record.get("parameter_code")
            == right_parameter_code
            and record.get(
                "calculation_status"
            ) == "calculated"
            and record.get(
                "calculation_run_id"
            )
        )
    }

    return len(
        left_runs & right_runs
    )


def build_available_model_parameter_dependencies(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str = "health_model",
) -> dict:
    parameter_records = (
        collect_health_model_parameter_records(
            research_records=research_records,
            pilot_sessions=pilot_sessions,
            study_id=study_id,
        )
    )

    variables_by_code = _build_variable_catalog(
        parameter_records
    )

    available_codes = sorted(
        variables_by_code.keys()
    )

    available_variables = [
        variables_by_code[code]
        for code in available_codes
    ]

    available_dependencies = []

    for left_code, right_code in combinations(
        available_codes,
        2,
    ):
        left_variable = variables_by_code[left_code]
        right_variable = variables_by_code[right_code]

        left_scale = left_variable.get("scale_type")
        right_scale = right_variable.get("scale_type")

        standard_methods = []

        for method in METHODS:
            if method.get("category") != "standard":
                continue

            if method.get("method_id") not in EXECUTABLE_METHOD_IDS:
                continue

            if not _scale_pattern_matches(
                method,
                left_scale,
                right_scale,
            ):
                continue

            standard_methods.append({
                "method_id": method.get("method_id"),
                "title": method.get("title"),
                "purpose": method.get("purpose"),
                "selection_status": (
                    "candidate_requires_condition_check"
                ),
                "missing_condition_checks": method.get(
                    "required_conditions",
                    [],
                ),
            })

        paired_session_count = _paired_session_count(
            parameter_records=parameter_records,
            left_parameter_code=left_code,
            right_parameter_code=right_code,
        )

        available_dependencies.append({
            "dependency_id": (
                f"model_parameter:{left_code}"
                f"__model_parameter:{right_code}"
            ),
            "variable_source": (
                "calculated_model_parameter"
            ),
            "pairing_unit": "session_id",
            "left": left_variable,
            "right": right_variable,
            "paired_session_count": (
                paired_session_count
            ),
            "available_standard_methods": (
                standard_methods
            ),
            "available_author_methods": [],
            "method_selection_status": (
                "methods_available"
                if standard_methods
                else (
                    "no_applicable_methods_from_metadata"
                )
            ),
        })

    return {
        "ok": True,
        "schema_version": (
            MODEL_PARAMETER_DEPENDENCY_SCHEMA_VERSION
        ),
        "study_id": study_id,
        "variable_source": (
            "calculated_model_parameter"
        ),
        "pairing_unit": "session_id",
        "available_variables_count": len(
            available_variables
        ),
        "available_dependencies_count": len(
            available_dependencies
        ),
        "available_variables": available_variables,
        "available_dependencies": (
            available_dependencies
        ),
    }
def build_selected_model_parameter_pair_options(
    *,
    parameter_records: list[dict],
    model_id: str,
    left_parameter_code: str,
    right_parameter_code: str,
) -> dict:
    if (
        left_parameter_code
        == right_parameter_code
    ):
        return {
            "ok": False,
            "status": "same_variable_selected",
        }

    model_records = [
        record
        for record in parameter_records
        if record.get("model_id") == model_id
    ]

    variables_by_code = _build_variable_catalog(
        model_records
    )

    left_variable = variables_by_code.get(
        left_parameter_code
    )

    if left_variable is None:
        return {
            "ok": False,
            "status": "left_parameter_not_found",
            "model_id": model_id,
            "left_parameter_code": (
                left_parameter_code
            ),
        }

    right_variable = variables_by_code.get(
        right_parameter_code
    )

    if right_variable is None:
        return {
            "ok": False,
            "status": "right_parameter_not_found",
            "model_id": model_id,
            "right_parameter_code": (
                right_parameter_code
            ),
        }

    left_scale = left_variable.get(
        "scale_type"
    )

    right_scale = right_variable.get(
        "scale_type"
    )

    standard_methods = []

    for method in METHODS:
        if method.get("category") != "standard":
            continue

        direct_match = _scale_pattern_matches(
            method,
            left_scale,
            right_scale,
        )

        reverse_match = _scale_pattern_matches(
            method,
            right_scale,
            left_scale,
        )

        if not direct_match and not reverse_match:
            continue

        standard_methods.append({
            "method_id": method.get(
                "method_id"
            ),
            "title": method.get("title"),
            "purpose": method.get(
                "purpose"
            ),
            "required_conditions": method.get(
                "required_conditions",
                [],
            ),
            "selection_status": (
                "candidate_requires_dataset_check"
            ),
            "matched_orientation": (
                "direct"
                if direct_match
                else "reversed"
            ),
        })

    paired_observation_count = (
        _paired_session_count(
            parameter_records=model_records,
            left_parameter_code=(
                left_parameter_code
            ),
            right_parameter_code=(
                right_parameter_code
            ),
        )
    )

    return {
        "ok": True,
        "status": (
            "methods_available"
            if standard_methods
            else "no_methods_for_scale_pair"
        ),
        "schema_version": (
            MODEL_PARAMETER_DEPENDENCY_SCHEMA_VERSION
        ),
        "model_id": model_id,
        "pairing_unit": (
            "calculation_run_id"
        ),
        "left": left_variable,
        "right": right_variable,
        "left_scale_type": left_scale,
        "right_scale_type": right_scale,
        "paired_observation_count": (
            paired_observation_count
        ),
        "available_standard_methods": (
            standard_methods
        ),
        "available_author_methods": [],
        "method_selection_status": (
            "methods_available"
            if standard_methods
            else (
                "no_applicable_methods_from_metadata"
            )
        ),
    }
